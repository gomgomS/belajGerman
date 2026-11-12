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

        rec = database.new(mgdDB, "db_toefl_access")
        rec.put("access_id",     idgen._get_unique_id())
        rec.put("fk_user_id",    order.get("fk_user_id", ""))
        rec.put("fk_package_id", order.get("fk_package_id", ""))
        rec.put("fk_order_id",   order_pkey)
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
    try:
        mgdDB  = database.get_db_conn(config.mainDB)
        access = mgdDB.db_toefl_access.find_one({
            "fk_user_id"   : user_pkey,
            "fk_package_id": package_pkey,
            "status"       : "ACTIVE",
        })
        if not access:
            return {"has_access": False, "tier": None}
        # end if
        return {"has_access": True, "tier": access.get("tier", "BASIC")}
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
