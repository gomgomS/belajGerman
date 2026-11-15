import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import traceback
from flask import Blueprint, request, redirect, g, jsonify, session

from middleware import middleware_privilege
from view.exam_engine import view_exam_engine
import sanitize

exam_engine_blueprint = Blueprint("exam_engine_blueprint", __name__)


@exam_engine_blueprint.route("/exam/<package_pkey>/start", methods=["GET"])
@middleware_privilege(roles=["peserta", "super_admin"])
def start_exam(package_pkey):
    try:
        from payment import payment_proc
        access = payment_proc.check_user_access(g.current_user["user_id"], package_pkey)
        if not access["has_access"]:
            return redirect("/student/preise")
        # end if

        import database, config as cfg
        mgdDB  = database.get_db_conn(cfg.mainDB)
        order  = mgdDB.db_toefl_order.find_one({
            "fk_user_id"   : g.current_user["user_id"],
            "fk_package_id": package_pkey,
            "status"       : "CONFIRMED",
        })
        order_pkey = order.get("pkey", "") if order else ""

        from exam_engine import exam_engine_proc
        result = exam_engine_proc.start_exam(
            user_pkey    = g.current_user["user_id"],
            package_pkey = package_pkey,
            order_pkey   = order_pkey,
        )

        if result["status"] != "OK":
            return redirect("/student/preise")
        # end if

        return redirect("/exam/session/" + result["exam_session_pkey"])
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_engine_blueprint.route("/exam/session/<exam_session_pkey>", methods=["GET"])
@middleware_privilege(roles=["peserta", "super_admin"])
def exam_session_page(exam_session_pkey):
    try:
        from exam_engine import exam_engine_proc
        sess_result = exam_engine_proc.get_exam_session(exam_session_pkey, g.current_user["user_id"])
        exam_session = sess_result.get("data")

        if not exam_session:
            return redirect("/student/preise")
        # end if

        if exam_session.get("status") == "COMPLETED":
            import database, config as cfg
            mgdDB  = database.get_db_conn(cfg.mainDB)
            result = mgdDB.db_toefl_result.find_one({"fk_exam_session_id": exam_session_pkey})
            if result:
                return redirect("/exam/result/" + result["pkey"])
            # end if
        # end if

        section_id        = exam_session.get("current_section_id")
        questions_result  = exam_engine_proc.get_section_questions_grouped(section_id)

        import database, config as cfg
        mgdDB   = database.get_db_conn(cfg.mainDB)
        section = mgdDB.db_toefl_package_section.find_one({"pkey": section_id})
        package = mgdDB.db_toefl_package.find_one({"pkey": exam_session.get("fk_package_id")})

        all_sections = list(
            mgdDB.db_toefl_package_section.find(
                {"fk_package_id": exam_session.get("fk_package_id"), "is_deleted": False}
            ).sort("sort_order", 1)
        )

        existing_answers = {
            a["fk_question_id"]: a["selected_answer"]
            for a in mgdDB.db_toefl_exam_answer.find({"fk_exam_session_id": exam_session_pkey})
        }

        return view_exam_engine.html_exam(
            exam_session     = exam_session,
            section          = section,
            package          = package,
            all_sections     = all_sections,
            passages         = questions_result.get("data", []),
            existing_answers = existing_answers,
            user             = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_engine_blueprint.route("/api/exam/save-answer", methods=["POST"])
@middleware_privilege(roles=["peserta", "super_admin"])
def save_answer_api():
    try:
        data             = request.get_json()
        exam_session_pkey = data.get("exam_session_pkey", "")
        question_pkey    = data.get("question_pkey", "")
        section_pkey     = data.get("section_pkey", "")
        selected_answer  = data.get("selected_answer", "")

        from exam_engine import exam_engine_proc
        result = exam_engine_proc.save_answer(
            exam_session_pkey = exam_session_pkey,
            question_pkey     = question_pkey,
            section_pkey      = section_pkey,
            selected_answer   = selected_answer,
        )
        return jsonify(result)
    except Exception:
        print(traceback.format_exc())
        return jsonify({"status": "ERROR"}), 500
    # end try
# end def


@exam_engine_blueprint.route("/api/exam/next-section", methods=["POST"])
@middleware_privilege(roles=["peserta", "super_admin"])
def next_section_api():
    try:
        data             = request.get_json()
        exam_session_pkey = data.get("exam_session_pkey", "")

        from exam_engine import exam_engine_proc
        result = exam_engine_proc.move_to_next_section(exam_session_pkey, g.current_user["user_id"])

        if result.get("result_pkey"):
            return jsonify({"status": "OK", "redirect": "/exam/result/" + result["result_pkey"]})
        # end if

        return jsonify({"status": "OK", "redirect": "/exam/session/" + exam_session_pkey})
    except Exception:
        print(traceback.format_exc())
        return jsonify({"status": "ERROR"}), 500
    # end try
# end def


@exam_engine_blueprint.route("/exam/session/<exam_session_pkey>/submit", methods=["POST"])
@middleware_privilege(roles=["peserta", "super_admin"])
def submit_exam(exam_session_pkey):
    try:
        from exam_engine import exam_engine_proc
        result = exam_engine_proc.submit_exam(exam_session_pkey, g.current_user["user_id"])
        if result["status"] == "OK":
            return redirect("/exam/result/" + result["result_pkey"])
        # end if
        return redirect("/student/preise")
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_engine_blueprint.route("/exam/result/<result_pkey>", methods=["GET"])
@middleware_privilege(roles=["peserta", "super_admin"])
def result_page(result_pkey):
    try:
        from exam_engine import exam_engine_proc
        from payment     import payment_proc

        result_data = exam_engine_proc.get_result(result_pkey, g.current_user["user_id"])
        if result_data["status"] != "OK" or not result_data["data"]:
            return redirect("/student/verlauf")
        # end if

        result  = result_data["data"]
        access  = payment_proc.check_user_access(g.current_user["user_id"], result.get("fk_package_id", ""))

        return view_exam_engine.html_result(
            result      = result,
            has_premium = access["tier"] == "PREMIUM" if access["has_access"] else False,
            user        = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@exam_engine_blueprint.route("/exam/review/<result_pkey>", methods=["GET"])
@middleware_privilege(roles=["peserta", "super_admin"])
def review_page(result_pkey):
    try:
        from exam_engine import exam_engine_proc
        from payment     import payment_proc

        result_data = exam_engine_proc.get_result(result_pkey, g.current_user["user_id"])
        if result_data["status"] != "OK" or not result_data["data"]:
            return redirect("/student/verlauf")
        # end if

        result = result_data["data"]
        access = payment_proc.check_user_access(g.current_user["user_id"], result.get("fk_package_id", ""))

        if not access["has_access"] or access["tier"] != "PREMIUM":
            return redirect("/exam/result/" + result_pkey)
        # end if

        review_data = exam_engine_proc.get_result_with_answers(result_pkey, g.current_user["user_id"])

        return view_exam_engine.html_review(
            result = review_data.get("data"),
            user   = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def
