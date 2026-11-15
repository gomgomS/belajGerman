import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template


def html_passages_list(passages, packages, user, sections_map=None,
                      filter_section="", filter_mode="", pagination=None,
                      filter_total=0, per_page_options=None,
                      bank_sections=None, section_labels=None, group_keys=None,
                      dump_counts=None):
    return render_template("expert/questions_list.html",
                           dump_counts=dump_counts or {},
                           passages=passages, packages=packages, user=user,
                           sections_map=sections_map or {},
                           filter_section=filter_section,
                           filter_mode=filter_mode,
                           pagination=pagination or {},
                           filter_total=filter_total,
                           per_page_options=per_page_options or [10, 20, 50, 100],
                           bank_sections=bank_sections or [],
                           section_labels=section_labels or {},
                           group_keys=group_keys or [])
# end def


def html_passage_editor(passage, questions, packages, sections_map, user,
                        preset_package_pkey="", preset_section=None,
                        section_config=None, first_question=None,
                        requested_mode="", return_to="",
                        used_in_packages=None, bank_section_options=None,
                        current_section_key="", requested_answer_type="mc",
                        cloze_answer_mode=""):
    return render_template("expert/question_editor.html",
                           passage=passage, questions=questions,
                           packages=packages, sections_map=sections_map, user=user,
                           preset_package_pkey=preset_package_pkey,
                           preset_section=preset_section,
                           section_config=section_config,
                           first_question=first_question,
                           requested_mode=requested_mode,
                           return_to=return_to,
                           used_in_packages=used_in_packages or [],
                           bank_section_options=bank_section_options or [],
                           current_section_key=current_section_key,
                           answer_type=((passage or {}).get("answer_type") or requested_answer_type or "mc"),
                           cloze_answer_mode=((passage or {}).get("cloze_answer_mode") or cloze_answer_mode or "mc"))
# end def


def html_passage_new(type_tests, user):
    return render_template("expert/question_new.html", type_tests=type_tests, user=user)
# end def


def html_passage_preview(passage, questions, user, gaps=None):
    return render_template("expert/question_preview.html",
                           passage=passage, questions=questions, user=user,
                           gaps=gaps or [])
# end def


def html_passage_usage(passage, q_count, placements, user):
    return render_template("expert/passage_usage.html",
                           passage=passage, q_count=q_count,
                           placements=placements, user=user)
# end def


def html_passage_sprechen_preview(passage, user):
    """Pratinjau passage Sprechen memakai halaman siswa dengan perekam suara."""
    item = {
        "title"        : passage.get("title", ""),
        "instruction"  : passage.get("instruction", ""),
        "question_text": passage.get("content_text", ""),
        "image"        : passage.get("image_url", ""),
        "sample_answer": passage.get("sample_answer", ""),
        "prep_seconds" : passage.get("prep_seconds", 0) or 0,
        "speak_seconds": passage.get("speak_seconds", 0) or 0,
    }
    return render_template(
        "admin/dump_preview_sprechen.html",
        item       = item,
        heading    = passage.get("title", "Sprechen"),
        back_url   = "/expert/question-bank/" + passage.get("pkey", ""),
        back_label = "Kembali ke editor",
        user       = user,
    )
# end def
