import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import json
import traceback
from urllib.parse import quote
from flask import Blueprint, request, redirect, g, jsonify

from middleware import middleware_privilege
from view.dashboard import view_dashboard
import sanitize

dashboard_blueprint = Blueprint("dashboard_blueprint", __name__)


@dashboard_blueprint.route("/dashboard", methods=["GET"])
@middleware_privilege(roles=["super_admin", "expert", "peserta"])
def dashboard_redirect():
    role = g.current_user.get("role", "peserta")
    if role == "super_admin":
        return redirect("/dashboard/admin")
    elif role == "expert":
        return redirect("/dashboard/expert")
    else:
        return redirect("/student")
    # end if
# end def


@dashboard_blueprint.route("/dashboard/admin", methods=["GET"])
@middleware_privilege(roles=["super_admin"])
def admin_dashboard():
    try:
        from dashboard import dashboard_proc
        stats = dashboard_proc.get_admin_stats()
        return view_dashboard.html_admin_dashboard(stats=stats, user=g.current_user)
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/students", methods=["GET"])
@middleware_privilege(roles=["super_admin"])
def admin_students():
    """Halaman khusus siswa (Lernende) — terpisah dari tim pengelola."""
    try:
        from dashboard import dashboard_proc
        result = dashboard_proc.get_students_with_context()
        return view_dashboard.html_admin_students(
            students = result.get("data", []),
            user     = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/staff", methods=["GET"])
@middleware_privilege(roles=["super_admin"])
def admin_staff():
    """Halaman tim pengelola: admin & guru (penyusun soal)."""
    try:
        from auth import auth_proc
        result = auth_proc.get_all_users(roles=["super_admin", "expert"])
        return view_dashboard.html_admin_staff(
            staff = result.get("data", []),
            user  = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/users", methods=["GET"])
@middleware_privilege(roles=["super_admin"])
def admin_users_legacy():
    # halaman pengguna lama sudah dipecah → siswa & tim pengelola
    role = request.args.get("role", "")
    if role in ("expert", "super_admin"):
        return redirect("/dashboard/admin/staff")
    # end if
    return redirect("/dashboard/admin/students")
# end def


@dashboard_blueprint.route("/api/admin/users/<user_pkey>/role", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def update_user_role(user_pkey):
    try:
        params   = sanitize.clean_html_dic(request.form.to_dict())
        new_role = params.get("role", "peserta")
        from auth import auth_proc
        result = auth_proc.update_user_role(user_pkey, new_role)
        return jsonify(result)
    except Exception:
        print(traceback.format_exc())
        return jsonify({"status": "ERROR"}), 500
    # end try
# end def


@dashboard_blueprint.route("/api/admin/users/<user_pkey>/status", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def update_user_status(user_pkey):
    try:
        params     = sanitize.clean_html_dic(request.form.to_dict())
        new_status = params.get("status", "ACTIVE")
        from auth import auth_proc
        result = auth_proc.update_user_status(user_pkey, new_status)
        return jsonify(result)
    except Exception:
        print(traceback.format_exc())
        return jsonify({"status": "ERROR"}), 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings", methods=["GET"])
@middleware_privilege(roles=["super_admin"])
def admin_settings():
    try:
        return view_dashboard.html_admin_settings_home(user=g.current_user)
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/tes", methods=["GET"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_tes_legacy():
    return redirect("/dashboard/admin/settings/level")
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/level", methods=["GET"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_tes():
    try:
        from app_settings import app_settings_proc
        from sanitize import strip_objectid_list
        bundle = app_settings_proc.get_settings_bundle().get("data", [])
        for item in bundle:
            item["sections"] = strip_objectid_list(item.get("sections", []))
        # end for
        return view_dashboard.html_admin_settings_tes(
            test_types = strip_objectid_list(bundle),
            user       = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/level", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_create_test_type():
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        from app_settings import app_settings_proc
        app_settings_proc.create_test_type(
            code       = params.get("code", ""),
            label      = params.get("label", ""),
            sort_order = params.get("sort_order", 0),
        )
        return redirect("/dashboard/admin/settings/level")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/level/<pkey>/update", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_update_test_type(pkey):
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        from app_settings import app_settings_proc
        app_settings_proc.update_test_type(
            pkey       = pkey,
            label      = params.get("label", ""),
            sort_order = params.get("sort_order", 0),
        )
        return redirect("/dashboard/admin/settings/level")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/level/<pkey>/delete", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_delete_test_type(pkey):
    try:
        from app_settings import app_settings_proc
        app_settings_proc.delete_test_type(pkey)
        return redirect("/dashboard/admin/settings/level")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/section", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_create_section():
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        from app_settings import app_settings_proc
        app_settings_proc.create_section_template(
            test_type_code    = params.get("test_type_code", ""),
            title             = params.get("title", ""),
            section_type      = params.get("section_type", ""),
            duration_minutes  = params.get("duration_minutes", 0),
            sort_order        = params.get("sort_order", 0),
        )
        return redirect("/dashboard/admin/settings/level")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/section/<pkey>/update", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_update_section(pkey):
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        from app_settings import app_settings_proc
        app_settings_proc.update_section_template(
            pkey              = pkey,
            title             = params.get("title", ""),
            section_type      = params.get("section_type", ""),
            duration_minutes  = params.get("duration_minutes", 0),
            sort_order        = params.get("sort_order", 0),
        )
        return redirect("/dashboard/admin/settings/level")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/section/<pkey>/delete", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_delete_section(pkey):
    try:
        from app_settings import app_settings_proc
        app_settings_proc.delete_section_template(pkey)
        return redirect("/dashboard/admin/settings/level")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/test-name", methods=["GET"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_test_name():
    try:
        from app_settings import app_settings_proc
        from sanitize import strip_objectid_list
        rows = app_settings_proc.get_test_names().get("data", [])
        return view_dashboard.html_admin_settings_test_name(
            test_names = strip_objectid_list(rows),
            user       = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/test-name", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_create_test_name():
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        from app_settings import app_settings_proc
        app_settings_proc.create_test_name(
            label      = params.get("label", ""),
            sort_order = params.get("sort_order", 0),
        )
        return redirect("/dashboard/admin/settings/test-name")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/test-name/<pkey>/update", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_update_test_name(pkey):
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        from app_settings import app_settings_proc
        app_settings_proc.update_test_name(
            pkey       = pkey,
            label      = params.get("label", ""),
            sort_order = params.get("sort_order", 0),
        )
        return redirect("/dashboard/admin/settings/test-name")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/test-name/<pkey>/delete", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_delete_test_name(pkey):
    try:
        from app_settings import app_settings_proc
        app_settings_proc.delete_test_name(pkey)
        return redirect("/dashboard/admin/settings/test-name")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/test-type", methods=["GET"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_type_test():
    try:
        from app_settings import app_settings_proc
        from sanitize import strip_objectid_list
        rows = app_settings_proc.get_type_tests().get("data", [])
        return view_dashboard.html_admin_settings_type_test(
            type_tests  = strip_objectid_list(rows),
            dump_counts = app_settings_proc.count_type_test_dumps(),
            user        = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/test-type", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_create_type_test():
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        from app_settings import app_settings_proc
        app_settings_proc.create_type_test(
            label       = params.get("label", ""),
            description = params.get("description", ""),
            sort_order  = params.get("sort_order", 0),
        )
        return redirect("/dashboard/admin/settings/test-type")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/test-type/<pkey>/update", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_update_type_test(pkey):
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        from app_settings import app_settings_proc
        app_settings_proc.update_type_test(
            pkey        = pkey,
            label       = params.get("label", ""),
            description = params.get("description", ""),
            sort_order  = params.get("sort_order", 0),
        )
        return redirect("/dashboard/admin/settings/test-type")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/test-type/<pkey>/delete", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_delete_type_test(pkey):
    try:
        from app_settings import app_settings_proc
        app_settings_proc.delete_type_test(pkey)
        return redirect("/dashboard/admin/settings/test-type")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


def _dumps_redirect(type_pkey, ok="", error=""):
    url = "/dashboard/admin/settings/test-type/" + type_pkey + "/dumps"
    if error:
        url += "?error=" + quote(error)
    elif ok:
        url += "?ok=" + quote(ok)
    # end if
    return redirect(url)
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/test-type/<pkey>/dumps", methods=["GET"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_type_test_dumps(pkey):
    try:
        from app_settings import app_settings_proc
        from sanitize import strip_objectid, strip_objectid_list
        type_test = strip_objectid(app_settings_proc.get_type_test_by_pkey(pkey).get("data"))
        if not type_test:
            return redirect("/dashboard/admin/settings/test-type")
        # end if
        dumps = strip_objectid_list(
            app_settings_proc.get_type_test_dumps(type_test.get("code", "")).get("data", [])
        )
        for item in dumps:
            item["jenis"] = app_settings_proc.dump_jenis_key(
                item.get("question_mode") or "single", item.get("answer_type") or "mc",
                item.get("cloze_mode") or ""
            )
            try:
                item["dump_pretty"] = json.dumps(json.loads(item.get("dump_json") or "{}"), ensure_ascii=False, indent=2)
                item["question_count"] = len(json.loads(item.get("dump_json") or "{}").get("questions") or [])
            except Exception:
                item["dump_pretty"] = item.get("dump_json") or ""
                item["question_count"] = 0
            # end try
        # end for
        return view_dashboard.html_admin_settings_type_test_dumps(
            type_test = type_test,
            dumps     = dumps,
            jenis_labels = app_settings_proc.DUMP_JENIS_LABELS,
            ok        = request.args.get("ok", ""),
            error     = request.args.get("error", ""),
            user      = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/test-type/<pkey>/dumps", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_create_type_test_dump(pkey):
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        from app_settings import app_settings_proc
        type_test = app_settings_proc.get_type_test_by_pkey(pkey).get("data")
        if not type_test:
            return redirect("/dashboard/admin/settings/test-type")
        # end if
        # dump_json divalidasi sebagai JSON; html.escape akan merusak tanda kutip & HTML soal
        result = app_settings_proc.create_type_test_dumps(
            test_type_code = type_test.get("code", ""),
            question_mode  = params.get("question_mode", "single"),
            raw_json       = request.form.get("dump_json", ""),
        )
        if result.get("status") != "OK":
            return _dumps_redirect(pkey, error=result.get("message", "Gagal menyimpan dump"))
        # end if
        return _dumps_redirect(pkey, ok="%s dump tersimpan" % result.get("created", 0))
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/test-type/<pkey>/dumps/<dump_pkey>/update", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_update_type_test_dump(pkey, dump_pkey):
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        from app_settings import app_settings_proc
        result = app_settings_proc.update_type_test_dump(
            pkey          = dump_pkey,
            question_mode = params.get("question_mode", "single"),
            raw_json      = request.form.get("dump_json", ""),
        )
        if result.get("status") != "OK":
            return _dumps_redirect(pkey, error=result.get("message", "Gagal mengubah dump"))
        # end if
        return _dumps_redirect(pkey, ok="Dump diperbarui")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/test-type/<pkey>/dumps/<dump_pkey>/delete", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_delete_type_test_dump(pkey, dump_pkey):
    try:
        from app_settings import app_settings_proc
        app_settings_proc.delete_type_test_dump(dump_pkey)
        return _dumps_redirect(pkey, ok="Dump dihapus")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/test-type/<pkey>/dumps/<dump_pkey>/preview", methods=["GET"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_dump_preview(pkey, dump_pkey):
    """Pratinjau contoh soal tampilan siswa — khusus Sprechen: dengan perekam suara."""
    try:
        from app_settings import app_settings_proc
        from sanitize import strip_objectid
        type_test = strip_objectid(app_settings_proc.get_type_test_by_pkey(pkey).get("data"))
        if not type_test:
            return redirect("/dashboard/admin/settings/test-type")
        # end if
        dump = strip_objectid(app_settings_proc.get_type_test_dump_by_pkey(dump_pkey).get("data"))
        if not dump or dump.get("fk_test_type_code") != type_test.get("code"):
            return _dumps_redirect(pkey, error="Contoh soal tidak ditemukan")
        # end if
        try:
            item = json.loads(dump.get("dump_json") or "{}")
        except Exception:
            item = {}
        # end try
        if isinstance(item, list):
            item = item[0] if item else {}
        # end if
        return view_dashboard.html_admin_settings_dump_preview(
            type_test = type_test,
            dump      = dump,
            item      = item,
            user      = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/sub-plan", methods=["GET"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_sub_plan():
    try:
        from app_settings import app_settings_proc
        from sanitize import strip_objectid_list
        plans = app_settings_proc.get_sub_plans().get("data", [])
        for plan in plans:
            plan["pricing"] = app_settings_proc.build_pricing_matrix(plan)
        # end for
        return view_dashboard.html_admin_settings_sub_plan(
            sub_plans = strip_objectid_list(plans),
            cycles    = app_settings_proc.SUB_CYCLES,
            user      = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/sub-plan", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_create_sub_plan():
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        from app_settings import app_settings_proc
        app_settings_proc.create_sub_plan(
            code                  = params.get("code", ""),
            label                 = params.get("label", ""),
            tagline               = params.get("tagline", ""),
            price_idr             = params.get("price_idr", 0),
            price_quarterly_idr   = params.get("price_quarterly_idr", 0),
            price_yearly_idr      = params.get("price_yearly_idr", 0),
            discount_monthly_pct  = params.get("discount_monthly_pct", 0),
            discount_quarterly_pct = params.get("discount_quarterly_pct", 0),
            discount_yearly_pct   = params.get("discount_yearly_pct", 0),
            ai_credits_monthly    = params.get("ai_credits_monthly", 0),
            sort_order            = params.get("sort_order", 0),
            status                = params.get("status", "ACTIVE"),
        )
        return redirect("/dashboard/admin/settings/sub-plan")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/sub-plan/<pkey>/update", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_update_sub_plan(pkey):
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        from app_settings import app_settings_proc
        app_settings_proc.update_sub_plan(
            pkey                  = pkey,
            label                 = params.get("label", ""),
            tagline               = params.get("tagline", ""),
            price_idr             = params.get("price_idr", 0),
            price_quarterly_idr   = params.get("price_quarterly_idr", 0),
            price_yearly_idr      = params.get("price_yearly_idr", 0),
            discount_monthly_pct  = params.get("discount_monthly_pct", 0),
            discount_quarterly_pct = params.get("discount_quarterly_pct", 0),
            discount_yearly_pct   = params.get("discount_yearly_pct", 0),
            ai_credits_monthly    = params.get("ai_credits_monthly", 0),
            sort_order            = params.get("sort_order", 0),
            status                = params.get("status", "ACTIVE"),
        )
        return redirect("/dashboard/admin/settings/sub-plan")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/admin/settings/sub-plan/<pkey>/delete", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def admin_settings_delete_sub_plan(pkey):
    try:
        from app_settings import app_settings_proc
        app_settings_proc.delete_sub_plan(pkey)
        return redirect("/dashboard/admin/settings/sub-plan")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@dashboard_blueprint.route("/dashboard/expert", methods=["GET"])
@middleware_privilege(roles=["super_admin", "expert"])
def expert_dashboard():
    try:
        from dashboard import dashboard_proc
        stats = dashboard_proc.get_expert_stats(g.current_user["user_id"])
        return view_dashboard.html_expert_dashboard(stats=stats, user=g.current_user)
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def
