import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template


def html_exam(exam_session, section, package, all_sections, passages, existing_answers, user):
    return render_template("peserta/exam.html",
                           exam_session=exam_session, section=section,
                           package=package, all_sections=all_sections,
                           passages=passages, existing_answers=existing_answers,
                           user=user)
# end def


def html_result(result, has_premium, user):
    return render_template("peserta/result.html", result=result, has_premium=has_premium, user=user)
# end def


def html_review(result, user):
    return render_template("peserta/review.html", result=result, user=user)
# end def
