import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import traceback
from flask import Blueprint, request, redirect, session, jsonify

from view.auth import view_auth
import sanitize

auth_blueprint = Blueprint("auth_blueprint", __name__)


@auth_blueprint.route("/login", methods=["GET"])
def login_page():
    try:
        if session.get("session_id"):
            return _redirect_by_role(session.get("role", "peserta"))
        # end if
        return view_auth.html_login()
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@auth_blueprint.route("/login", methods=["POST"])
def login_post():
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        email    = params.get("email", "")
        password = params.get("password", "")

        from auth import auth_proc
        result = auth_proc.login_user(
            email      = email,
            password   = password,
            user_agent = request.user_agent.string,
            ip_address = request.remote_addr,
        )

        if result["status"] != "OK":
            return view_auth.html_login(error=result["message"])
        # end if

        session.permanent  = True
        session["session_id"] = result["session_id"]
        session["role"]       = result["role"]
        session["full_name"]  = result["full_name"]

        return _redirect_by_role(result["role"])

    except Exception:
        print(traceback.format_exc())
        return view_auth.html_login(error="Terjadi kesalahan sistem")
    # end try
# end def


@auth_blueprint.route("/register", methods=["GET"])
def register_page():
    try:
        if session.get("session_id"):
            return _redirect_by_role(session.get("role", "peserta"))
        # end if
        return view_auth.html_register()
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@auth_blueprint.route("/register", methods=["POST"])
def register_post():
    try:
        params    = sanitize.clean_html_dic(request.form.to_dict())
        full_name = params.get("full_name", "")
        email     = params.get("email", "")
        phone     = params.get("phone", "")
        password  = params.get("password", "")
        confirm   = params.get("confirm_password", "")

        if len(full_name) < 2:
            return view_auth.html_register(error="Nama lengkap minimal 2 karakter")
        # end if

        if len(password) < 6:
            return view_auth.html_register(error="Password minimal 6 karakter")
        # end if

        if password != confirm:
            return view_auth.html_register(error="Konfirmasi password tidak cocok")
        # end if

        from auth import auth_proc
        result = auth_proc.register_user(full_name, email, password, phone)

        if result["status"] != "OK":
            return view_auth.html_register(error=result["message"])
        # end if

        return view_auth.html_login(success="Registrasi berhasil! Silakan login.")

    except Exception:
        print(traceback.format_exc())
        return view_auth.html_register(error="Terjadi kesalahan sistem")
    # end try
# end def


@auth_blueprint.route("/logout", methods=["GET"])
def logout():
    try:
        sid = session.get("session_id")
        if sid:
            from auth import auth_proc
            auth_proc.logout_user(sid)
        # end if
        session.clear()
        return redirect("/login")
    except Exception:
        print(traceback.format_exc())
        session.clear()
        return redirect("/login")
    # end try
# end def


@auth_blueprint.route("/unauthorized", methods=["GET"])
def unauthorized():
    try:
        return view_auth.html_unauthorized()
    except Exception:
        print(traceback.format_exc())
        return "Akses ditolak", 403
    # end try
# end def


@auth_blueprint.route("/setup/create-admin", methods=["GET", "POST"])
def setup_admin():
    try:
        from auth import auth_proc
        import database, config

        mgdDB = database.get_db_conn(config.mainDB)
        existing = mgdDB.db_toefl_user.find_one({"role": "super_admin"})
        if existing:
            return redirect("/login")
        # end if

        if request.method == "POST":
            params    = sanitize.clean_html_dic(request.form.to_dict())
            full_name = params.get("full_name", "")
            email     = params.get("email", "")
            password  = params.get("password", "")
            result    = auth_proc.create_super_admin(full_name, email, password)
            if result["status"] == "OK":
                return redirect("/login")
            # end if
            return view_auth.html_setup(error=result.get("message"))
        # end if

        return view_auth.html_setup()

    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


def _redirect_by_role(role):
    if role == "super_admin":
        return redirect("/dashboard/admin")
    elif role == "expert":
        return redirect("/dashboard/expert")
    else:
        return redirect("/catalog")
    # end if
# end def
