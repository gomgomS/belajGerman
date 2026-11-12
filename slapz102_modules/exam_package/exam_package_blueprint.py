import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import traceback
from flask import Blueprint, request, redirect, g, jsonify

from middleware import middleware_privilege
from view.exam_package import view_exam_package
import sanitize

exam_package_blueprint = Blueprint("exam_package_blueprint", __name__)


def _load_package(package_ref):
    """package_ref = nomor urut paket (atau pkey lama)."""
    from exam_package import exam_package_proc
    from sanitize import strip_objectid
    return strip_objectid(exam_package_proc.get_package_by_ref(package_ref).get("data"))
# end def


def _package_url(package):
    return "/expert/exam-package/" + str(package.get("package_no") or package.get("pkey"))
# end def


def _load_section(package, section_pkey):
    from exam_package import exam_package_proc
    from sanitize import strip_objectid
    section = strip_objectid(exam_package_proc.get_section_by_id(section_pkey).get("data"))
    if not section or section.get("fk_package_id") != package.get("pkey"):
        return None
    # end if
    return section
# end def


def _load_part(package, part_pkey):
    from exam_package import exam_package_proc
    from sanitize import strip_objectid
    part = strip_objectid(exam_package_proc.get_part_by_id(part_pkey).get("data"))
    if not part or part.get("fk_package_id") != package.get("pkey"):
        return None
    # end if
    return part
# end def


def _settings_options():
    from app_settings import app_settings_proc
    from sanitize import strip_objectid_list
    return {
        "levels"     : strip_objectid_list(app_settings_proc.get_test_types().get("data", [])),
        "test_names" : strip_objectid_list(app_settings_proc.get_test_names().get("data", [])),
        "type_tests" : strip_objectid_list(app_settings_proc.get_type_tests().get("data", [])),
    }
# end def


@exam_package_blueprint.route("/expert/exam-package", methods=["GET"])
@middleware_privilege(roles=["super_admin", "expert"])
def list_packages():
    try:
        from exam_package import exam_package_proc
        result = exam_package_proc.get_all_packages()
        opts   = _settings_options()
        return view_exam_package.html_packages_list(
            packages    = result.get("data", []),
            user        = g.current_user,
            level_names = {row.get("code"): row.get("label") for row in opts["levels"]},
            test_names  = {row.get("code"): row.get("label") for row in opts["test_names"]},
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/create", methods=["GET"])
@middleware_privilege(roles=["super_admin", "expert"])
def create_package_page():
    try:
        opts = _settings_options()
        return view_exam_package.html_package_form(
            package    = None,
            user       = g.current_user,
            levels     = opts["levels"],
            test_names = opts["test_names"],
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/create", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def create_package_post():
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        from exam_package import exam_package_proc
        result = exam_package_proc.create_package(
            title          = params.get("title", ""),
            test_type      = params.get("level_code", ""),
            description    = params.get("description", ""),
            expert_id      = g.current_user["user_id"],
            level_code     = params.get("level_code", ""),
            test_name_code = params.get("test_name_code", ""),
        )
        if result["status"] == "OK":
            return redirect("/expert/exam-package/" + str(result["package_no"]))
        # end if
        return redirect("/expert/exam-package")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>", methods=["GET"])
@middleware_privilege(roles=["super_admin", "expert"])
def view_package(package_ref):
    try:
        from exam_package import exam_package_proc
        from sanitize import strip_objectid
        package = _load_package(package_ref)
        if not package:
            return redirect("/expert/exam-package")
        # end if
        result = exam_package_proc.get_package_with_sections_and_questions(package["pkey"])
        opts   = _settings_options()
        return view_exam_package.html_package_detail(
            package    = strip_objectid(result.get("data")),
            user       = g.current_user,
            levels     = opts["levels"],
            test_names = opts["test_names"],
            type_tests = opts["type_tests"],
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/preview", methods=["GET"])
@middleware_privilege(roles=["super_admin", "expert"])
def preview_package(package_ref):
    try:
        from exam_package import exam_package_proc
        from sanitize import strip_objectid
        package = _load_package(package_ref)
        if not package:
            return redirect("/expert/exam-package")
        # end if
        result = exam_package_proc.get_package_with_sections_and_questions(package["pkey"])
        return view_exam_package.html_package_preview(
            package = strip_objectid(result.get("data")),
            user    = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/update", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def update_package_post(package_ref):
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        from exam_package import exam_package_proc
        package = _load_package(package_ref)
        if not package:
            return redirect("/expert/exam-package")
        # end if
        exam_package_proc.update_package(
            package_pkey   = package["pkey"],
            title          = params.get("title", ""),
            description    = params.get("description", ""),
            level_code     = params.get("level_code", ""),
            test_name_code = params.get("test_name_code", ""),
        )
        return redirect(_package_url(package))
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/publish", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def publish_package_post(package_ref):
    try:
        from exam_package import exam_package_proc
        package = _load_package(package_ref)
        if not package:
            return redirect("/expert/exam-package")
        # end if
        exam_package_proc.publish_package(package["pkey"])
        return redirect(_package_url(package))
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/unpublish", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def unpublish_package_post(package_ref):
    try:
        from exam_package import exam_package_proc
        package = _load_package(package_ref)
        if not package:
            return redirect("/expert/exam-package")
        # end if
        exam_package_proc.unpublish_package(package["pkey"])
        return redirect(_package_url(package))
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/delete", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def delete_package_post(package_ref):
    try:
        from exam_package import exam_package_proc
        package = _load_package(package_ref)
        if package:
            exam_package_proc.delete_package(package["pkey"])
        # end if
        return redirect("/expert/exam-package")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/section/add", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def add_section_post(package_ref):
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        from exam_package import exam_package_proc
        package = _load_package(package_ref)
        if not package:
            return redirect("/expert/exam-package")
        # end if
        exam_package_proc.add_section(
            package_pkey     = package["pkey"],
            test_type_code   = params.get("test_type_code", ""),
            duration_minutes = sanitize.clean_int(params.get("duration_minutes"), 0),
        )
        return redirect(_package_url(package))
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/section/<section_pkey>/update", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def update_section_post(package_ref, section_pkey):
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        from exam_package import exam_package_proc
        package = _load_package(package_ref)
        if not package:
            return redirect("/expert/exam-package")
        # end if
        if _load_section(package, section_pkey):
            exam_package_proc.update_section(
                section_pkey, sanitize.clean_int(params.get("duration_minutes"), 0)
            )
        # end if
        return redirect(_package_url(package))
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/section/<section_pkey>/delete", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def delete_section_post(package_ref, section_pkey):
    try:
        from exam_package import exam_package_proc
        package = _load_package(package_ref)
        if not package:
            return redirect("/expert/exam-package")
        # end if
        if _load_section(package, section_pkey):
            exam_package_proc.delete_section(package["pkey"], section_pkey)
        # end if
        return redirect(_package_url(package))
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/section/<section_pkey>/part/add", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def add_part_post(package_ref, section_pkey):
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        from exam_package import exam_package_proc
        package = _load_package(package_ref)
        if not package:
            return redirect("/expert/exam-package")
        # end if
        if _load_section(package, section_pkey):
            exam_package_proc.add_part(
                package["pkey"], section_pkey, params.get("name", ""),
                after_pkey = params.get("after_pkey", ""),
            )
        # end if
        return redirect(_package_url(package))
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/part/<part_pkey>/update", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def rename_part_post(package_ref, part_pkey):
    try:
        params = sanitize.clean_html_dic(request.form.to_dict())
        from exam_package import exam_package_proc
        package = _load_package(package_ref)
        if not package:
            return redirect("/expert/exam-package")
        # end if
        if _load_part(package, part_pkey):
            exam_package_proc.rename_part(part_pkey, params.get("name", ""))
        # end if
        return redirect(_package_url(package))
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/part/<part_pkey>/delete", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def delete_part_post(package_ref, part_pkey):
    try:
        from exam_package import exam_package_proc
        package = _load_package(package_ref)
        if not package:
            return redirect("/expert/exam-package")
        # end if
        if _load_part(package, part_pkey):
            exam_package_proc.delete_part(part_pkey)
        # end if
        return redirect(_package_url(package))
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/section/<section_pkey>/from-bank", methods=["GET"])
@middleware_privilege(roles=["super_admin", "expert"])
def attach_from_bank_page(package_ref, section_pkey):
    try:
        from exam_package import exam_package_proc
        from sanitize import strip_objectid_list
        package = _load_package(package_ref)
        if not package:
            return redirect("/expert/exam-package")
        # end if
        section = _load_section(package, section_pkey)
        if not section:
            return redirect(_package_url(package))
        # end if
        part_pkey = sanitize.clean_str(request.args.get("part") or "")
        part = None
        if part_pkey:
            part = _load_part(package, part_pkey)
            if not part or part.get("fk_package_section_id") != section_pkey:
                return redirect(_package_url(package))
            # end if
        # end if
        candidates = strip_objectid_list(
            exam_package_proc.get_bank_candidates_for_section(
                section, expert_id=g.current_user.get("user_id"), part_pkey=part_pkey
            ).get("data", [])
        )
        return view_exam_package.html_package_bank_picker(
            package     = package,
            section     = section,
            part        = part,
            candidates  = candidates,
            package_url = _package_url(package),
            user        = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/section/<section_pkey>/from-bank", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def attach_from_bank_post(package_ref, section_pkey):
    try:
        from exam_package import exam_package_proc
        package = _load_package(package_ref)
        if not package:
            return redirect("/expert/exam-package")
        # end if
        if not _load_section(package, section_pkey):
            return redirect(_package_url(package))
        # end if
        part_pkey = sanitize.clean_str(request.form.get("part_pkey") or "")
        if part_pkey:
            part = _load_part(package, part_pkey)
            if not part or part.get("fk_package_section_id") != section_pkey:
                return redirect(_package_url(package))
            # end if
        # end if
        raw_pkeys = request.form.getlist("passage_pkey")
        passage_pkeys = []
        for raw in raw_pkeys:
            cleaned = sanitize.clean_html_dic({"p": raw}).get("p", "")
            if cleaned:
                passage_pkeys.append(cleaned)
            # end if
        # end for
        exam_package_proc.sync_section_passages(
            package["pkey"], section_pkey, passage_pkeys, part_pkey=part_pkey
        )
        if sanitize.clean_str(request.form.get("ajax") or ""):
            return jsonify({"status": "OK", "count": len(passage_pkeys)})
        # end if
        return redirect(_package_url(package))
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/section/<section_pkey>/detach", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def detach_from_section_post(package_ref, section_pkey):
    try:
        from exam_package import exam_package_proc
        package = _load_package(package_ref)
        if not package:
            return redirect("/expert/exam-package")
        # end if
        params = sanitize.clean_html_dic(request.form.to_dict())
        if _load_section(package, section_pkey):
            exam_package_proc.detach_passage_from_section(
                section_pkey, params.get("passage_pkey", ""), package["pkey"]
            )
        # end if
        return redirect(_package_url(package))
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/section/<section_pkey>/part/reorder", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def reorder_parts_post(package_ref, section_pkey):
    try:
        from exam_package import exam_package_proc
        package = _load_package(package_ref)
        if not package or not _load_section(package, section_pkey):
            return jsonify({"status": "ERROR"}), 400
        # end if
        payload  = request.get_json(silent=True) or {}
        exam_package_proc.reorder_parts(section_pkey, payload.get("part_pkeys") or [])
        return jsonify({"status": "OK"})
    except Exception:
        print(traceback.format_exc())
        return jsonify({"status": "ERROR"}), 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/section/<section_pkey>/item/reorder", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def reorder_items_post(package_ref, section_pkey):
    try:
        from exam_package import exam_package_proc
        package = _load_package(package_ref)
        if not package or not _load_section(package, section_pkey):
            return jsonify({"status": "ERROR"}), 400
        # end if
        payload  = request.get_json(silent=True) or {}
        exam_package_proc.reorder_section_items(section_pkey, payload.get("passage_pkeys") or [])
        return jsonify({"status": "OK"})
    except Exception:
        print(traceback.format_exc())
        return jsonify({"status": "ERROR"}), 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/section/reorder", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def reorder_sections_post(package_ref):
    try:
        from exam_package import exam_package_proc
        package = _load_package(package_ref)
        if not package:
            return jsonify({"status": "ERROR"}), 400
        # end if
        payload  = request.get_json(silent=True) or {}
        exam_package_proc.reorder_sections(package["pkey"], payload.get("section_pkeys") or [])
        return jsonify({"status": "OK"})
    except Exception:
        print(traceback.format_exc())
        return jsonify({"status": "ERROR"}), 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/section/<section_pkey>/part/create-from", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def create_part_from_post(package_ref, section_pkey):
    try:
        from exam_package import exam_package_proc
        package = _load_package(package_ref)
        if not package or not _load_section(package, section_pkey):
            return jsonify({"status": "ERROR"}), 400
        # end if
        payload = request.get_json(silent=True) or {}
        result = exam_package_proc.create_part_from_passages(
            package["pkey"], section_pkey,
            payload.get("name") or "",
            payload.get("passage_pkeys") or [],
        )
        if result.get("status") != "OK":
            return jsonify(result), 400
        # end if
        return jsonify(result)
    except Exception:
        print(traceback.format_exc())
        return jsonify({"status": "ERROR"}), 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/section/<section_pkey>/item/move", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def move_item_post(package_ref, section_pkey):
    try:
        from exam_package import exam_package_proc
        package = _load_package(package_ref)
        if not package or not _load_section(package, section_pkey):
            return jsonify({"status": "ERROR"}), 400
        # end if
        payload     = request.get_json(silent=True) or {}
        passage_pkey = payload.get("passage_pkey") or ""
        part_pkey    = payload.get("part_pkey") or ""
        if not passage_pkey:
            return jsonify({"status": "ERROR"}), 400
        # end if
        if part_pkey and not _load_part(package, part_pkey):
            return jsonify({"status": "ERROR"}), 400
        # end if
        exam_package_proc.attach_passage_to_section(
            section_pkey, passage_pkey, package["pkey"], part_pkey=part_pkey
        )
        return jsonify({"status": "OK"})
    except Exception:
        print(traceback.format_exc())
        return jsonify({"status": "ERROR"}), 500
    # end try
# end def


@exam_package_blueprint.route("/expert/exam-package/<package_ref>/section/<section_pkey>/bank-options", methods=["GET"])
@middleware_privilege(roles=["super_admin", "expert"])
def bank_options_json(package_ref, section_pkey):
    try:
        from exam_package import exam_package_proc
        from sanitize import strip_objectid_list
        package = _load_package(package_ref)
        if not package:
            return jsonify({"status": "ERROR"}), 404
        # end if
        section = _load_section(package, section_pkey)
        if not section:
            return jsonify({"status": "ERROR"}), 404
        # end if
        part_raw  = request.args.get("part")
        part_pkey = sanitize.clean_str(part_raw) if part_raw is not None else None
        result = exam_package_proc.get_bank_candidates_for_section(
            section, part_pkey=part_pkey
        )
        rows = []
        for p in strip_objectid_list(result.get("data", [])):
            rows.append({
                "pkey"          : p.get("pkey", ""),
                "title"         : p.get("title", ""),
                "question_count": p.get("question_count", 0),
                "question_mode" : p.get("question_mode", ""),
                "attached"      : bool(p.get("attached")),
                "in_part_name"  : p.get("in_part_name", ""),
                "used_in_other" : [x.get("title", "") for x in (p.get("used_in_other") or [])][:3],
            })
        # end for
        return jsonify({"status": "OK", "data": rows})
    except Exception:
        print(traceback.format_exc())
        return jsonify({"status": "ERROR"}), 500
    # end try
# end def
