import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import traceback
import uuid
import time

from werkzeug.security import generate_password_hash, check_password_hash

import database
import config
import idgen

# Python 3.8 (WSL) cannot verify scrypt hashes from newer Werkzeug/Windows.
HASH_METHOD = "pbkdf2:sha256"


def _hash_password(password):
    return generate_password_hash(password, method=HASH_METHOD)
# end def


def register_user(full_name, email, password, phone=""):
    try:
        mgdDB = database.get_db_conn(config.mainDB)

        existing = mgdDB.db_toefl_user.find_one({"email": email.lower().strip()})
        if existing:
            return {"status": "ERROR", "message": "Email sudah terdaftar"}
        # end if

        rec = database.new(mgdDB, "db_toefl_user")
        rec.put("user_id",   idgen._get_unique_id())
        rec.put("username",  email.lower().strip())
        rec.put("email",     email.lower().strip())
        rec.put("password",  _hash_password(password))
        rec.put("full_name", full_name.strip())
        rec.put("phone",     phone.strip())
        rec.put("role",      "peserta")
        rec.put("status",    "ACTIVE")
        rec.insert()

        return {"status": "OK", "message": "Registrasi berhasil"}

    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Terjadi kesalahan sistem"}
    # end try
# end def


def login_user(email, password, user_agent="", ip_address=""):
    try:
        mgdDB = database.get_db_conn(config.mainDB)

        user = mgdDB.db_toefl_user.find_one({
            "email"  : email.lower().strip(),
            "status" : "ACTIVE",
        })

        if not user:
            return {"status": "ERROR", "message": "Email atau password salah"}
        # end if

        if not check_password_hash(user.get("password", ""), password):
            return {"status": "ERROR", "message": "Email atau password salah"}
        # end if

        session_id  = str(uuid.uuid4())
        expire_time = int(time.time() * 1000) + config.MS_7_DAYS

        rec = database.new(mgdDB, "db_toefl_session")
        rec.put("session_id",  session_id)
        rec.put("fk_user_id",  user.get("pkey", ""))
        rec.put("username",    user.get("email", ""))
        rec.put("role",        user.get("role", "peserta"))
        rec.put("full_name",   user.get("full_name", ""))
        rec.put("user_agent",  user_agent)
        rec.put("ip_address",  ip_address)
        rec.put("expire_time", expire_time)
        rec.put("is_active",   True)
        rec.insert()

        return {
            "status"     : "OK",
            "session_id" : session_id,
            "role"       : user.get("role", "peserta"),
            "full_name"  : user.get("full_name", ""),
        }

    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Terjadi kesalahan sistem"}
    # end try
# end def


def logout_user(session_id):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_toefl_session.update_one(
            {"session_id": session_id},
            {"$set": {"is_active": False}}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def create_super_admin(full_name, email, password):
    try:
        mgdDB = database.get_db_conn(config.mainDB)

        existing_admin = mgdDB.db_toefl_user.find_one({"role": "super_admin"})
        if existing_admin:
            return {"status": "ERROR", "message": "Super admin sudah ada"}
        # end if

        rec = database.new(mgdDB, "db_toefl_user")
        rec.put("user_id",   idgen._get_unique_id())
        rec.put("username",  email.lower().strip())
        rec.put("email",     email.lower().strip())
        rec.put("password",  _hash_password(password))
        rec.put("full_name", full_name.strip())
        rec.put("phone",     "")
        rec.put("role",      "super_admin")
        rec.put("status",    "ACTIVE")
        rec.insert()

        return {"status": "OK", "message": "Super admin berhasil dibuat"}

    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Terjadi kesalahan sistem"}
    # end try
# end def


def get_all_users(role_filter=None, roles=None):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        query = {"is_deleted": False}
        if roles:
            # beberapa peran sekaligus, mis. ["super_admin", "expert"]
            query["role"] = {"$in": list(roles)}
        elif role_filter:
            query["role"] = role_filter
        # end if
        users = list(mgdDB.db_toefl_user.find(query, {"password": 0}).sort("rec_timestamp", -1))
        return {"status": "OK", "data": users}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def update_user_role(user_pkey, new_role):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_toefl_user.update_one(
            {"pkey": user_pkey},
            {"$set": {"role": new_role}}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def ensure_dev_user(full_name, email, password, role):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        email = (email or "").lower().strip()
        if not email or not password:
            return {"status": "ERROR", "message": "Email atau password kosong"}
        # end if

        existing = mgdDB.db_toefl_user.find_one({"email": email})
        if existing:
            mgdDB.db_toefl_user.update_one(
                {"pkey": existing["pkey"]},
                {"$set": {
                    "password" : _hash_password(password),
                    "role"     : role,
                    "status"   : "ACTIVE",
                    "full_name": full_name,
                    "is_deleted": False,
                }}
            )
            return {"status": "OK", "message": "Akun diperbarui", "pkey": existing.get("pkey", "")}
        # end if

        rec = database.new(mgdDB, "db_toefl_user")
        rec.put("user_id",   idgen._get_unique_id())
        rec.put("username",  email)
        rec.put("email",     email)
        rec.put("password",  _hash_password(password))
        rec.put("full_name", full_name)
        rec.put("phone",     "")
        rec.put("role",      role)
        rec.put("status",    "ACTIVE")
        rec.insert()
        return {"status": "OK", "message": "Akun dibuat"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal membuat akun"}
    # end try
# end def


def update_user_status(user_pkey, new_status):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_toefl_user.update_one(
            {"pkey": user_pkey},
            {"$set": {"status": new_status}}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def
