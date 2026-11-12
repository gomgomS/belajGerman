import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import traceback
import random
import time

import database
import config
import idgen


def start_exam(user_pkey, package_pkey, order_pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)

        existing = mgdDB.db_toefl_exam_session.find_one({
            "fk_user_id"   : user_pkey,
            "fk_package_id": package_pkey,
            "status"       : "IN_PROGRESS",
            "is_deleted"   : False,
        })
        if existing:
            return {"status": "OK", "exam_session_pkey": existing.get("pkey")}
        # end if

        sections = list(
            mgdDB.db_toefl_package_section.find(
                {"fk_package_id": package_pkey, "is_deleted": False}
            ).sort("sort_order", 1)
        )
        if not sections:
            return {"status": "ERROR", "message": "Paket tidak memiliki seksi soal"}
        # end if

        first_section    = sections[0]
        now              = int(time.time() * 1000)
        section_deadline = now + (first_section.get("duration_minutes", 60) * 60 * 1000)

        rec = database.new(mgdDB, "db_toefl_exam_session")
        rec.put("exam_session_id",     idgen._get_unique_id())
        rec.put("fk_user_id",          user_pkey)
        rec.put("fk_package_id",       package_pkey)
        rec.put("fk_order_id",         order_pkey)
        rec.put("current_section_id",  first_section.get("pkey", ""))
        rec.put("current_question_index", 0)
        rec.put("section_deadline",    section_deadline)
        rec.put("status",              "IN_PROGRESS")
        rec.put("started_at",          now)
        rec.put("completed_at",        0)
        rec.put("section_order",       [s.get("pkey") for s in sections])
        exam_session_pkey = rec._mongo_record.get("pkey", "")
        rec.insert()

        return {"status": "OK", "exam_session_pkey": exam_session_pkey}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal memulai ujian"}
    # end try
# end def


def get_exam_session(exam_session_pkey, user_pkey):
    try:
        mgdDB   = database.get_db_conn(config.mainDB)
        session = mgdDB.db_toefl_exam_session.find_one({
            "pkey"       : exam_session_pkey,
            "fk_user_id" : user_pkey,
            "is_deleted" : False,
        })
        return {"status": "OK", "data": session}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": None}
    # end try
# end def


def get_section_questions_grouped(section_pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)

        from exam_package import exam_package_proc
        passages = exam_package_proc.load_passages_for_section(section_pkey, mgdDB)

        # Urutan bagian (Teil) tetap; acak hanya di dalam tiap bagian
        part_groups = []
        for passage in passages:
            part_key = passage.get("part_pkey", "")
            if not part_groups or part_groups[-1][0] != part_key:
                part_groups.append((part_key, []))
            # end if
            part_groups[-1][1].append(passage["pkey"])
        # end for
        passage_pkeys = []
        for _part_key, group in part_groups:
            random.shuffle(group)
            passage_pkeys.extend(group)
        # end for

        result_passages = []
        for pkey in passage_pkeys:
            passage   = next((p for p in passages if p["pkey"] == pkey), None)
            if not passage:
                continue
            # end if
            questions = list(
                mgdDB.db_toefl_question.find(
                    {"fk_passage_id": pkey, "is_deleted": False}
                ).sort("sort_order", 1)
            )
            for q in questions:
                q.pop("correct_answer", None)
                q.pop("explanation",    None)
                q.pop("answer_text",    None)
            # end for
            passage["questions"] = questions
            result_passages.append(passage)
        # end for

        return {"status": "OK", "data": result_passages}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def save_answer(exam_session_pkey, question_pkey, section_pkey, selected_answer):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        now   = int(time.time() * 1000)

        # Jawaban huruf (A–D) disimpan uppercase; jawaban isian (teks) apa adanya
        stored_answer = str(selected_answer or "").strip()
        if len(stored_answer) == 1:
            stored_answer = stored_answer.upper()
        # end if

        existing = mgdDB.db_toefl_exam_answer.find_one({
            "fk_exam_session_id": exam_session_pkey,
            "fk_question_id"    : question_pkey,
        })

        if existing:
            mgdDB.db_toefl_exam_answer.update_one(
                {"fk_exam_session_id": exam_session_pkey, "fk_question_id": question_pkey},
                {"$set": {"selected_answer": stored_answer, "saved_at": now}}
            )
        else:
            rec = database.new(mgdDB, "db_toefl_exam_answer")
            rec.put("answer_id",          idgen._get_unique_id())
            rec.put("fk_exam_session_id", exam_session_pkey)
            rec.put("fk_question_id",     question_pkey)
            rec.put("fk_section_id",      section_pkey)
            rec.put("selected_answer",    stored_answer)
            rec.put("is_correct",         False)
            rec.put("saved_at",           now)
            rec.insert()
        # end if

        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def move_to_next_section(exam_session_pkey, user_pkey):
    try:
        mgdDB       = database.get_db_conn(config.mainDB)
        exam_session = mgdDB.db_toefl_exam_session.find_one({
            "pkey"       : exam_session_pkey,
            "fk_user_id" : user_pkey,
        })
        if not exam_session:
            return {"status": "ERROR", "message": "Sesi tidak ditemukan"}
        # end if

        section_order  = exam_session.get("section_order", [])
        current_sec_id = exam_session.get("current_section_id", "")

        try:
            current_idx = section_order.index(current_sec_id)
        except ValueError:
            current_idx = -1
        # end try

        if current_idx + 1 >= len(section_order):
            return submit_exam(exam_session_pkey, user_pkey)
        # end if

        next_section_pkey = section_order[current_idx + 1]
        next_section      = mgdDB.db_toefl_package_section.find_one({"pkey": next_section_pkey})
        now               = int(time.time() * 1000)
        new_deadline      = now + (next_section.get("duration_minutes", 60) * 60 * 1000)

        mgdDB.db_toefl_exam_session.update_one(
            {"pkey": exam_session_pkey},
            {"$set": {
                "current_section_id"      : next_section_pkey,
                "current_question_index"  : 0,
                "section_deadline"        : new_deadline,
            }}
        )

        return {"status": "OK", "next_section_id": next_section_pkey}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def submit_exam(exam_session_pkey, user_pkey):
    try:
        mgdDB        = database.get_db_conn(config.mainDB)
        exam_session  = mgdDB.db_toefl_exam_session.find_one({"pkey": exam_session_pkey})
        if not exam_session:
            return {"status": "ERROR"}
        # end if

        answers  = list(mgdDB.db_toefl_exam_answer.find({"fk_exam_session_id": exam_session_pkey}))
        sections = list(
            mgdDB.db_toefl_package_section.find(
                {"fk_package_id": exam_session.get("fk_package_id"), "is_deleted": False}
            )
        )

        section_breakdown = {}
        total_correct     = 0
        total_questions   = 0

        for section in sections:
            section_pkey      = section.get("pkey")
            from exam_package import exam_package_proc
            passage_pkeys = exam_package_proc.get_passage_pkeys_for_section(section_pkey, mgdDB)
            section_questions = []
            if passage_pkeys:
                section_questions = list(
                    mgdDB.db_toefl_question.find(
                        {"fk_passage_id": {"$in": passage_pkeys}, "is_deleted": False},
                        {"pkey": 1, "correct_answer": 1, "answer_text": 1}
                    )
                )
            # end if

            correct_map    = {q["pkey"]: q for q in section_questions}
            section_correct = 0
            section_total   = len(section_questions)

            from question_bank import question_bank_proc
            for answer in answers:
                qpkey = answer.get("fk_question_id")
                if qpkey in correct_map:
                    key_doc = correct_map[qpkey]
                    answer_text = key_doc.get("answer_text") or ""
                    if answer_text:
                        # Lückentext isian — cocokkan teks (case-insensitive, boleh multi-kunci ';')
                        is_correct = question_bank_proc.check_text_answer(
                            answer.get("selected_answer"), answer_text
                        )
                    else:
                        is_correct = answer.get("selected_answer") == key_doc.get("correct_answer")
                    # end if
                    mgdDB.db_toefl_exam_answer.update_one(
                        {"pkey": answer.get("pkey")},
                        {"$set": {"is_correct": is_correct}}
                    )
                    if is_correct:
                        section_correct += 1
                    # end if
                # end if
            # end for

            section_score = round((section_correct / section_total * 100), 1) if section_total > 0 else 0
            section_breakdown[section_pkey] = {
                "title"    : section.get("title"),
                "correct"  : section_correct,
                "total"    : section_total,
                "score"    : section_score,
            }
            total_correct   += section_correct
            total_questions += section_total
        # end for

        total_score = round((total_correct / total_questions * 100), 1) if total_questions > 0 else 0

        toefl_itp_score = _convert_to_toefl_itp(section_breakdown, total_correct, total_questions)

        now = int(time.time() * 1000)
        rec = database.new(mgdDB, "db_toefl_result")
        rec.put("result_id",         idgen._get_unique_id())
        rec.put("fk_exam_session_id",exam_session_pkey)
        rec.put("fk_user_id",        user_pkey)
        rec.put("fk_package_id",     exam_session.get("fk_package_id", ""))
        rec.put("total_score",       toefl_itp_score)
        rec.put("listening_score",   section_breakdown.get(_get_section_pkey_by_type(sections, "LISTENING"), {}).get("score", 0))
        rec.put("structure_score",   section_breakdown.get(_get_section_pkey_by_type(sections, "STRUCTURE"), {}).get("score", 0))
        rec.put("reading_score",     section_breakdown.get(_get_section_pkey_by_type(sections, "READING"), {}).get("score", 0))
        rec.put("section_breakdown", section_breakdown)
        rec.put("completed_at",      now)
        result_pkey = rec._mongo_record.get("pkey", "")
        rec.insert()

        mgdDB.db_toefl_exam_session.update_one(
            {"pkey": exam_session_pkey},
            {"$set": {"status": "COMPLETED", "completed_at": now}}
        )

        # ── AI Feedback (German Platform) ──────────────────────────────────────
        # Jalankan setelah hasil tersimpan; gagal secara graceful.
        try:
            package      = mgdDB.db_toefl_package.find_one({"pkey": exam_session.get("fk_package_id", "")})
            test_type_code = package.get("test_type", "") if package else ""
            pct_score    = round((total_correct / total_questions * 100), 1) if total_questions > 0 else 0
            from exam_engine.german_ai_proc import generate_and_save_feedback
            generate_and_save_feedback(
                result_pkey       = result_pkey,
                exam_session_pkey = exam_session_pkey,
                user_pkey         = user_pkey,
                package_pkey      = exam_session.get("fk_package_id", ""),
                section_breakdown = section_breakdown,
                total_score       = pct_score,
                test_type_code    = test_type_code,
            )
        except Exception:
            print("[exam_engine_proc] AI feedback error (non-fatal):")
            print(traceback.format_exc())
        # end try
        # ──────────────────────────────────────────────────────────────────────

        return {"status": "OK", "result_pkey": result_pkey}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def get_result(result_pkey, user_pkey):
    try:
        mgdDB  = database.get_db_conn(config.mainDB)
        result = mgdDB.db_toefl_result.find_one({"pkey": result_pkey, "fk_user_id": user_pkey})
        if not result:
            return {"status": "ERROR", "data": None}
        # end if

        package = mgdDB.db_toefl_package.find_one({"pkey": result.get("fk_package_id")})
        result["package_data"] = package

        # Sertakan AI feedback jika tersedia
        try:
            from exam_engine.german_ai_proc import get_feedback_for_result
            ai_result = get_feedback_for_result(result_pkey)
            result["ai_feedback"] = ai_result.get("data")
        except Exception:
            result["ai_feedback"] = None
        # end try

        return {"status": "OK", "data": result}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": None}
    # end try
# end def


def get_result_with_answers(result_pkey, user_pkey):
    try:
        mgdDB       = database.get_db_conn(config.mainDB)
        result      = mgdDB.db_toefl_result.find_one({"pkey": result_pkey, "fk_user_id": user_pkey})
        exam_session = mgdDB.db_toefl_exam_session.find_one({"pkey": result.get("fk_exam_session_id")})
        answers     = list(mgdDB.db_toefl_exam_answer.find({"fk_exam_session_id": exam_session.get("pkey")}))

        answer_map = {a["fk_question_id"]: a for a in answers}

        sections = list(
            mgdDB.db_toefl_package_section.find(
                {"fk_package_id": result.get("fk_package_id"), "is_deleted": False}
            ).sort("sort_order", 1)
        )

        from exam_package import exam_package_proc
        for section in sections:
            passages = exam_package_proc.load_passages_for_section(section["pkey"], mgdDB)
            for passage in passages:
                for q in passage.get("questions") or []:
                    user_answer = answer_map.get(q["pkey"], {})
                    q["user_answer"]  = user_answer.get("selected_answer", "")
                    q["is_correct"]   = user_answer.get("is_correct", False)
                # end for
            # end for
            section["passages"] = passages
        # end for

        result["sections"] = sections
        return {"status": "OK", "data": result}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": None}
    # end try
# end def


def get_user_results(user_pkey):
    try:
        mgdDB   = database.get_db_conn(config.mainDB)
        results = list(mgdDB.db_toefl_result.find({"fk_user_id": user_pkey}).sort("completed_at", -1))
        for result in results:
            package = mgdDB.db_toefl_package.find_one({"pkey": result.get("fk_package_id")}, {"title": 1, "test_type": 1})
            result["package_data"] = package
        # end for
        return {"status": "OK", "data": results}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def _convert_to_toefl_itp(section_breakdown, total_correct, total_questions):
    pct = (total_correct / total_questions * 100) if total_questions > 0 else 0
    scaled = 310 + round((pct / 100) * (677 - 310))
    return max(310, min(677, scaled))
# end def


def _get_section_pkey_by_type(sections, section_type):
    for s in sections:
        if s.get("section_type") == section_type:
            return s.get("pkey", "")
        # end if
    # end for
    return ""
# end def
