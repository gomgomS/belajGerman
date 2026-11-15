import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import traceback
import time

import database
import config
import idgen


def get_active_subscription(user_pkey):
    """Akses langganan platform (scope PLATFORM) yang masih berlaku untuk user."""
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        now   = int(time.time() * 1000)
        access = mgdDB.db_toefl_access.find_one({
            "fk_user_id": user_pkey,
            "scope"     : "PLATFORM",
            "status"    : "ACTIVE",
            "expire_at" : {"$gt": now},
        })
        if not access:
            # akses PLATFORM tanpa expire (legacy) tetap dianggap aktif
            access = mgdDB.db_toefl_access.find_one({
                "fk_user_id": user_pkey,
                "scope"     : "PLATFORM",
                "status"    : "ACTIVE",
                "expire_at" : 0,
            })
        # end if
        if not access:
            return {"status": "OK", "data": None}
        # end if
        plan = mgdDB.db_subscription_plan.find_one({"code": access.get("tier", ""), "is_deleted": False})
        access["plan_data"] = plan or None
        return {"status": "OK", "data": access}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": None}
    # end try
# end def


def create_subscription_order(user_pkey, plan_code, cycle):
    """Buat order langganan (order_type=SUBSCRIPTION) — model bayar per siklus, bukan per paket ujian."""
    try:
        from app_settings import app_settings_proc
        mgdDB = database.get_db_conn(config.mainDB)

        plan_code = str(plan_code or "").upper().strip()
        plan      = mgdDB.db_subscription_plan.find_one({"code": plan_code, "is_deleted": False})
        if not plan:
            return {"status": "ERROR", "message": "Paket langganan tidak ditemukan"}
        # end if
        if str(plan.get("status", "ACTIVE")).upper() != "ACTIVE":
            return {"status": "ERROR", "message": "Paket langganan sedang tidak tersedia"}
        # end if
        if int(plan.get("price_idr", 0) or 0) <= 0:
            return {"status": "ERROR", "message": "Paket gratis tidak perlu dipesan — cukup daftar"}
        # end if

        pricing = app_settings_proc.compute_cycle_pricing(plan, cycle)
        if not pricing:
            return {"status": "ERROR", "message": "Durasi langganan tidak valid"}
        # end if

        pending = mgdDB.db_toefl_order.find_one({
            "fk_user_id": user_pkey,
            "order_type" : "SUBSCRIPTION",
            "status"     : "PENDING",
        })
        if pending:
            return {"status": "OK", "order_pkey": pending.get("pkey", ""), "amount": pending.get("amount", 0)}
        # end if

        cycle_label = {
            "MONTHLY": "1 bulan", "QUARTERLY": "3 bulan", "YEARLY": "12 bulan",
        }.get(pricing["cycle"], "")

        rec = database.new(mgdDB, "db_toefl_order")
        rec.put("order_id",       idgen._get_unique_id())
        rec.put("order_type",     "SUBSCRIPTION")
        rec.put("fk_user_id",     user_pkey)
        rec.put("fk_package_id",  "")
        rec.put("package_title",  "Langganan " + plan.get("label", plan_code) + " — " + cycle_label)
        rec.put("tier",           plan_code)
        rec.put("plan_code",      plan_code)
        rec.put("cycle",          pricing["cycle"])
        rec.put("months",         pricing["months"])
        rec.put("amount",         pricing["final_price"])
        rec.put("status",         "PENDING")
        rec.put("payment_method", "MANUAL")
        rec.put("payment_proof",  "")
        rec.put("confirmed_by",   "")
        rec.put("confirmed_at",   0)
        rec.put("notes",          "")
        order_pkey = rec._mongo_record.get("pkey", "")
        rec.insert()

        return {"status": "OK", "order_pkey": order_pkey, "amount": pricing["final_price"]}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal membuat order langganan"}
    # end try
# end def


def create_order(user_pkey, package_pkey, tier):
    try:
        mgdDB = database.get_db_conn(config.mainDB)

        existing_access = mgdDB.db_toefl_access.find_one({
            "fk_user_id"  : user_pkey,
            "fk_package_id": package_pkey,
            "status"      : "ACTIVE",
        })
        if existing_access:
            return {"status": "ERROR", "message": "Kamu sudah memiliki akses ke paket ini"}
        # end if

        package = mgdDB.db_toefl_package.find_one({"pkey": package_pkey, "is_deleted": False})
        if not package:
            return {"status": "ERROR", "message": "Paket tidak ditemukan"}
        # end if

        tier   = tier.upper()
        amount = package.get("price_premium", 0) if tier == "PREMIUM" else package.get("price_basic", 0)

        rec = database.new(mgdDB, "db_toefl_order")
        rec.put("order_id",       idgen._get_unique_id())
        rec.put("fk_user_id",     user_pkey)
        rec.put("fk_package_id",  package_pkey)
        rec.put("package_title",  package.get("title", ""))
        rec.put("tier",           tier)
        rec.put("amount",         amount)
        rec.put("status",         "PENDING")
        rec.put("payment_method", "MANUAL")
        rec.put("payment_proof",  "")
        rec.put("confirmed_by",   "")
        rec.put("confirmed_at",   0)
        rec.put("notes",          "")
        order_pkey = rec._mongo_record.get("pkey", "")
        rec.insert()

        return {"status": "OK", "order_pkey": order_pkey, "amount": amount}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal membuat order"}
    # end try
# end def


def confirm_order(order_pkey, admin_pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        order = mgdDB.db_toefl_order.find_one({"pkey": order_pkey})
        if not order:
            return {"status": "ERROR", "message": "Order tidak ditemukan"}
        # end if
        if order.get("status") != "PENDING":
            return {"status": "ERROR", "message": "Order sudah diproses sebelumnya"}
        # end if

        now = int(time.time() * 1000)
        mgdDB.db_toefl_order.update_one(
            {"pkey": order_pkey},
            {"$set": {
                "status"       : "CONFIRMED",
                "confirmed_by" : admin_pkey,
                "confirmed_at" : now,
            }}
        )

        if order.get("order_type") == "SUBSCRIPTION":
            # langganan: akses seluruh ujian, berlaku sampai expire_at (ditumpuk jika sudah ada)
            months      = int(order.get("months", 1) or 1)
            existing    = mgdDB.db_toefl_access.find_one({
                "fk_user_id": order.get("fk_user_id", ""),
                "scope"     : "PLATFORM",
                "status"    : "ACTIVE",
            })
            base        = max(now, (existing or {}).get("expire_at", 0) or 0)
            expire_at   = base + months * 30 * 24 * 60 * 60 * 1000  # 1 bulan = 30 hari
            if existing:
                mgdDB.db_toefl_access.update_one(
                    {"pkey": existing.get("pkey")},
                    {"$set": {
                        "tier"      : order.get("plan_code", order.get("tier", "BASIC")),
                        "expire_at" : expire_at,
                        "fk_order_id": order_pkey,
                    }}
                )
            else:
                rec = database.new(mgdDB, "db_toefl_access")
                rec.put("access_id",     idgen._get_unique_id())
                rec.put("fk_user_id",    order.get("fk_user_id", ""))
                rec.put("fk_package_id", "")
                rec.put("fk_order_id",   order_pkey)
                rec.put("scope",         "PLATFORM")
                rec.put("tier",          order.get("plan_code", order.get("tier", "BASIC")))
                rec.put("status",        "ACTIVE")
                rec.put("granted_at",    now)
                rec.put("expire_at",     expire_at)
                rec.insert()
            # end if
            return {"status": "OK"}
        # end if

        rec = database.new(mgdDB, "db_toefl_access")
        rec.put("access_id",     idgen._get_unique_id())
        rec.put("fk_user_id",    order.get("fk_user_id", ""))
        rec.put("fk_package_id", order.get("fk_package_id", ""))
        rec.put("fk_order_id",   order_pkey)
        rec.put("scope",         "PACKAGE")
        rec.put("tier",          order.get("tier", "BASIC"))
        rec.put("status",        "ACTIVE")
        rec.put("granted_at",    now)
        rec.put("expire_at",     0)
        rec.insert()

        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal konfirmasi order"}
    # end try
# end def


def cancel_order(order_pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_toefl_order.update_one(
            {"pkey": order_pkey},
            {"$set": {"status": "CANCELLED"}}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def get_user_orders(user_pkey):
    try:
        mgdDB  = database.get_db_conn(config.mainDB)
        orders = list(mgdDB.db_toefl_order.find({"fk_user_id": user_pkey}).sort("rec_timestamp", -1))
        return {"status": "OK", "data": orders}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def get_all_orders(status=None):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        query = {}
        if status:
            query["status"] = status
        # end if
        orders = list(mgdDB.db_toefl_order.find(query).sort("rec_timestamp", -1))
        return {"status": "OK", "data": orders}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def get_order_by_id(order_pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        order = mgdDB.db_toefl_order.find_one({"pkey": order_pkey})
        return {"status": "OK", "data": order}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": None}
    # end try
# end def


def check_user_access(user_pkey, package_pkey):
    """Akses paket ujian: berlaku jika ada langganan platform aktif ATAU akses paket legacy."""
    try:
        mgdDB = database.get_db_conn(config.mainDB)

        # 1) langganan platform aktif → semua ujian terbuka
        subscription = get_active_subscription(user_pkey).get("data")
        if subscription:
            return {"has_access": True, "tier": subscription.get("tier", "BASIC"), "scope": "PLATFORM"}
        # end if

        # 2) akses per paket (model lama) — tetap dihormati
        access = mgdDB.db_toefl_access.find_one({
            "fk_user_id"   : user_pkey,
            "fk_package_id": package_pkey,
            "status"       : "ACTIVE",
        })
        if not access:
            return {"has_access": False, "tier": None}
        # end if
        return {"has_access": True, "tier": access.get("tier", "BASIC"), "scope": "PACKAGE"}
    except Exception:
        print(traceback.format_exc())
        return {"has_access": False, "tier": None}
    # end try
# end def


def get_user_access_list(user_pkey):
    try:
        mgdDB       = database.get_db_conn(config.mainDB)
        access_list = list(mgdDB.db_toefl_access.find({
            "fk_user_id": user_pkey,
            "status"    : "ACTIVE",
        }))
        return {"status": "OK", "data": access_list}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def initiate_duitku_payment(order_pkey, amount, description, customer_email):
    """
    Duitku integration scaffold — aktifkan setelah konfigurasi di slapz102_core/config.py.
    Tambahkan: G_DUITKU_MERCHANT_CODE, G_DUITKU_API_KEY, G_DUITKU_BASE_URL
    """
    return {
        "status" : "PENDING_INTEGRATION",
        "message": "Duitku integration belum aktif. Lanjut ke konfirmasi manual.",
    }
# end def


def handle_duitku_webhook(payload):
    """
    Duitku webhook handler scaffold.
    """
    return {"status": "PENDING_INTEGRATION"}
# end def
