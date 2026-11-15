import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import traceback
import re

import database
import config
import idgen
import sanitize


ANSWER_TYPES = ("mc", "rf", "cloze", "speak")

# Cara menjawab rumpang Lückentext: "mc" = pilihan A–D (kartu soal, default),
# "input" = peserta mengetik jawaban (isian, dinilai otomatis via answer_text),
# "select" = pilihan A–D tapi TAMPIL INLINE di teks (dropdown pada penanda [n]).
CLOZE_ANSWER_MODES = ("mc", "input", "select")


def normalize_answer_type(value):
    value = str(value or "").lower().strip()
    return value if value in ANSWER_TYPES else "mc"
# end def


def normalize_cloze_answer_mode(value):
    value = str(value or "").lower().strip()
    return value if value in CLOZE_ANSWER_MODES else "mc"
# end def


def cloze_question_text(gap_no):
    return "Lücke %s" % gap_no
# end def


def normalize_text_for_check(value):
    """Normalisasi jawaban isian: casefold, rapatkan spasi, buang tanda baca akhir,
    dan samakan koma desimal Jerman dengan titik (0,50 == 0.50)."""
    text = str(value or "").lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = text.rstrip(".,!?;:")
    text = re.sub(r"(\d),(\d)", r"\1.\2", text)
    return text.strip()
# end def


def check_text_answer(user_answer, answer_text):
    """True bila jawaban isian cocok dengan kunci (boleh beberapa kunci, pisahkan dengan ';')."""
    keys = [normalize_text_for_check(part) for part in str(answer_text or "").split(";")]
    keys = [k for k in keys if k]
    if not keys:
        return False
    # end if
    return normalize_text_for_check(user_answer) in keys
# end def


def _apply_answer_type(answer_type, options, correct_answer, option_images):
    """Richtig/Falsch disimpan sebagai opsi A=Richtig, B=Falsch agar penilaian tetap A–D.
    Lückentext (cloze) tanpa gambar opsi."""
    correct = str(correct_answer or "A").upper().strip()
    if answer_type == "cloze":
        images = None if option_images is None else {"a": "", "b": "", "c": "", "d": ""}
        return options, correct, images
    # end if
    if answer_type != "rf":
        return options, correct, option_images
    # end if
    options = {"a": "Richtig", "b": "Falsch", "c": "", "d": ""}
    if correct not in ("A", "B"):
        correct = "A"
    # end if
    images = None if option_images is None else {"a": "", "b": "", "c": "", "d": ""}
    return options, correct, images
# end def


def get_passages(section_id=None, expert_id=None):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        query = {"is_deleted": False}
        if section_id:
            query["fk_package_section_id"] = section_id
        # end if
        if expert_id:
            query["fk_expert_id"] = expert_id
        # end if
        passages = list(mgdDB.db_toefl_passage.find(query).sort("sort_order", 1))
        return {"status": "OK", "data": passages}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def get_passage_by_id(passage_pkey):
    try:
        mgdDB   = database.get_db_conn(config.mainDB)
        passage = mgdDB.db_toefl_passage.find_one({"pkey": passage_pkey, "is_deleted": False})
        return {"status": "OK", "data": passage}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": None}
    # end try
# end def


def create_passage(title, content_type, content_text, audio_url, section_id, expert_id,
                   question_mode="grouped", passage_sub_type="", section_key="", sub_type_key="",
                   answer_type="mc", cloze_answer_mode="",
                   instruction="", sample_answer="", image_url="", prep_seconds=0, speak_seconds=0, is_premium=False):
    try:
        mgdDB = database.get_db_conn(config.mainDB)

        max_order_doc = mgdDB.db_toefl_passage.find_one(
            {"fk_package_section_id": section_id, "is_deleted": False},
            sort=[("sort_order", -1)]
        )
        next_order = (max_order_doc.get("sort_order", 0) + 1) if max_order_doc else 1

        rec = database.new(mgdDB, "db_toefl_passage")
        rec.put("passage_id",            idgen._get_unique_id())
        rec.put("fk_package_section_id", section_id)
        rec.put("fk_expert_id",          expert_id)
        rec.put("title",                 title)
        rec.put("content_type",          content_type)
        rec.put("content_text",          content_text)
        rec.put("audio_url",             audio_url)
        rec.put("instruction",           instruction or "")
        rec.put("sample_answer",         sample_answer or "")
        rec.put("image_url",             image_url or "")
        rec.put("prep_seconds",          int(prep_seconds or 0))
        rec.put("speak_seconds",         int(speak_seconds or 0))
        rec.put("is_premium",            bool(is_premium))
        rec.put("sort_order",            next_order)
        rec.put("question_count",        0)
        rec.put("question_mode",         question_mode)
        rec.put("answer_type",           normalize_answer_type(answer_type))
        rec.put("cloze_answer_mode",     normalize_cloze_answer_mode(cloze_answer_mode))
        rec.put("passage_sub_type",      passage_sub_type)
        rec.put("section_key",           section_key)
        rec.put("sub_type_key",          sub_type_key)
        rec.put("status",                "DRAFT")
        passage_pkey = rec._mongo_record.get("pkey", "")
        rec.insert()

        if section_id and passage_pkey:
            from exam_package import exam_package_proc
            section_doc = exam_package_proc.get_section_by_id(section_id).get("data") or {}
            exam_package_proc.attach_passage_to_section(
                section_id, passage_pkey, section_doc.get("fk_package_id", "")
            )
        # end if

        return {"status": "OK", "passage_pkey": passage_pkey}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal menyimpan passage"}
    # end try
# end def


def update_passage(passage_pkey, title, content_type, content_text, audio_url,
                   question_mode="grouped", passage_sub_type="", section_key=None, sub_type_key=None,
                   section_id=None, cloze_answer_mode=None,
                   instruction=None, sample_answer=None, image_url=None,
                   prep_seconds=None, speak_seconds=None, is_premium=None):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        update_fields = {
            "title"            : title,
            "content_type"     : content_type,
            "content_text"     : content_text,
            "audio_url"        : audio_url,
            "question_mode"    : question_mode,
            "passage_sub_type" : passage_sub_type,
        }
        if section_id   is not None: update_fields["fk_package_section_id"] = section_id
        if section_key  is not None: update_fields["section_key"]  = section_key
        if sub_type_key is not None: update_fields["sub_type_key"] = sub_type_key
        if cloze_answer_mode is not None:
            update_fields["cloze_answer_mode"] = normalize_cloze_answer_mode(cloze_answer_mode)
        # end if
        if instruction   is not None: update_fields["instruction"]   = instruction
        if sample_answer is not None: update_fields["sample_answer"] = sample_answer
        if image_url     is not None: update_fields["image_url"]     = image_url
        if prep_seconds  is not None: update_fields["prep_seconds"]  = int(prep_seconds or 0)
        if speak_seconds is not None: update_fields["speak_seconds"] = int(speak_seconds or 0)
        if is_premium    is not None: update_fields["is_premium"]    = bool(is_premium)
        # end if
        mgdDB.db_toefl_passage.update_one({"pkey": passage_pkey}, {"$set": update_fields})
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def delete_passage(passage_pkey):
    return delete_passages([passage_pkey])
# end def


def delete_passages(passage_pkeys):
    try:
        pkeys = [pk for pk in (passage_pkeys or []) if pk]
        if not pkeys:
            return {"status": "OK"}
        # end if
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_toefl_passage.update_many(
            {"pkey": {"$in": pkeys}},
            {"$set": {"is_deleted": True}}
        )
        mgdDB.db_toefl_question.update_many(
            {"fk_passage_id": {"$in": pkeys}},
            {"$set": {"is_deleted": True}}
        )
        mgdDB.db_toefl_section_item.update_many(
            {"fk_passage_id": {"$in": pkeys}},
            {"$set": {"is_deleted": True}}
        )
        from exam_package import exam_package_proc
        exam_package_proc.recount_packages_for_passages(pkeys)
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def get_questions_by_passage(passage_pkey):
    try:
        mgdDB     = database.get_db_conn(config.mainDB)
        questions = list(
            mgdDB.db_toefl_question.find(
                {"fk_passage_id": passage_pkey, "is_deleted": False}
            ).sort("sort_order", 1)
        )
        return {"status": "OK", "data": questions}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def get_question_by_id(question_pkey):
    try:
        mgdDB    = database.get_db_conn(config.mainDB)
        question = mgdDB.db_toefl_question.find_one({"pkey": question_pkey, "is_deleted": False})
        return {"status": "OK", "data": question}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": None}
    # end try
# end def


def create_question(passage_pkey, section_id, expert_id, question_text,
                    option_a, option_b, option_c, option_d,
                    correct_answer, explanation,
                    section_key="", sub_type_key="", option_images=None, answer_type=None,
                    answer_text="", is_premium=False):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        if answer_type is None:
            passage = mgdDB.db_toefl_passage.find_one({"pkey": passage_pkey}, {"answer_type": 1}) or {}
            answer_type = passage.get("answer_type")
        # end if
        answer_type = normalize_answer_type(answer_type)
        options, correct_answer, option_images = _apply_answer_type(
            answer_type,
            {"a": option_a, "b": option_b, "c": option_c, "d": option_d},
            correct_answer,
            option_images or {},
        )
        option_a, option_b, option_c, option_d = options["a"], options["b"], options["c"], options["d"]

        max_order_doc = mgdDB.db_toefl_question.find_one(
            {"fk_passage_id": passage_pkey, "is_deleted": False},
            sort=[("sort_order", -1)]
        )
        next_order = (max_order_doc.get("sort_order", 0) + 1) if max_order_doc else 1

        rec = database.new(mgdDB, "db_toefl_question")
        rec.put("question_id",           idgen._get_unique_id())
        rec.put("fk_passage_id",         passage_pkey)
        rec.put("fk_package_section_id", section_id)
        rec.put("fk_expert_id",          expert_id)
        rec.put("question_text",         question_text)
        rec.put("option_a",              option_a)
        rec.put("option_b",              option_b)
        rec.put("option_c",              option_c)
        rec.put("option_d",              option_d)
        for key in ("a", "b", "c", "d"):
            rec.put("option_" + key + "_image", option_images.get(key, "") or "")
        # end for
        rec.put("answer_type",           answer_type)
        rec.put("correct_answer",        correct_answer.upper())
        rec.put("answer_text",           str(answer_text or "").strip() if answer_type == "cloze" else "")
        rec.put("explanation",           explanation)
        rec.put("section_key",           section_key)
        rec.put("sub_type_key",          sub_type_key)
        rec.put("is_premium",            bool(is_premium))
        rec.put("sort_order",            next_order)
        rec.put("status",                "DRAFT")
        rec.insert()

        question_pkey = rec._mongo_record.get("pkey", "")

        mgdDB.db_toefl_passage.update_one(
            {"pkey": passage_pkey},
            {"$inc": {"question_count": 1}}
        )

        return {"status": "OK", "question_pkey": question_pkey}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal menyimpan soal"}
    # end try
# end def


def update_question(question_pkey, question_text, option_a, option_b, option_c, option_d,
                    correct_answer, explanation, section_key=None, sub_type_key=None,
                    option_images=None, answer_text=None, is_premium=None):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        existing = mgdDB.db_toefl_question.find_one({"pkey": question_pkey}, {"answer_type": 1, "fk_passage_id": 1}) or {}
        answer_type = existing.get("answer_type")
        if not answer_type:
            passage = mgdDB.db_toefl_passage.find_one({"pkey": existing.get("fk_passage_id")}, {"answer_type": 1}) or {}
            answer_type = passage.get("answer_type")
        # end if
        answer_type = normalize_answer_type(answer_type)
        options, correct_answer, option_images = _apply_answer_type(
            answer_type,
            {"a": option_a, "b": option_b, "c": option_c, "d": option_d},
            correct_answer,
            option_images,
        )
        option_a, option_b, option_c, option_d = options["a"], options["b"], options["c"], options["d"]
        update_fields = {
            "question_text" : question_text,
            "option_a"      : option_a,
            "option_b"      : option_b,
            "option_c"      : option_c,
            "option_d"      : option_d,
            "correct_answer": correct_answer.upper(),
            "explanation"   : explanation,
        }
        if answer_text is not None and answer_type == "cloze":
            update_fields["answer_text"] = str(answer_text or "").strip()
        # end if
        if section_key  is not None: update_fields["section_key"]  = section_key
        if sub_type_key is not None: update_fields["sub_type_key"] = sub_type_key
        if is_premium   is not None: update_fields["is_premium"]   = bool(is_premium)
        if option_images is not None:
            for key in ("a", "b", "c", "d"):
                update_fields["option_" + key + "_image"] = option_images.get(key, "") or ""
            # end for
        # end if
        mgdDB.db_toefl_question.update_one(
            {"pkey": question_pkey},
            {"$set": update_fields}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def delete_question(question_pkey):
    try:
        mgdDB    = database.get_db_conn(config.mainDB)
        question = mgdDB.db_toefl_question.find_one({"pkey": question_pkey})
        if question:
            mgdDB.db_toefl_question.update_one({"pkey": question_pkey}, {"$set": {"is_deleted": True}})
            mgdDB.db_toefl_passage.update_one(
                {"pkey": question.get("fk_passage_id")},
                {"$inc": {"question_count": -1}}
            )
        # end if
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


BANK_PER_PAGE_OPTIONS = [10, 20, 50, 100]
BANK_DEFAULT_PER_PAGE = 10


def _bank_list_query(expert_id=None, section_key="", question_mode=""):
    query = {"is_deleted": False}
    if question_mode in ("single", "grouped"):
        query["question_mode"] = question_mode
    # end if
    section_key = str(section_key or "").strip()
    if section_key:
        query["section_key"] = {"$regex": "^" + re.escape(section_key) + "$", "$options": "i"}
    # end if
    return query
# end def


def _normalize_per_page(per_page):
    try:
        value = int(per_page or BANK_DEFAULT_PER_PAGE)
    except Exception:
        value = BANK_DEFAULT_PER_PAGE
    # end try
    if value not in BANK_PER_PAGE_OPTIONS:
        value = BANK_DEFAULT_PER_PAGE
    # end if
    return value
# end def


def _normalize_page(page):
    try:
        value = int(page or 1)
    except Exception:
        value = 1
    # end try
    if value < 1:
        value = 1
    # end if
    return value
# end def


def list_bank_passages(expert_id=None, section_key="", question_mode="", page=1, per_page=10):
    try:
        mgdDB    = database.get_db_conn(config.mainDB)
        query    = _bank_list_query(expert_id, section_key, question_mode)
        per_page = _normalize_per_page(per_page)
        page     = _normalize_page(page)
        total    = mgdDB.db_toefl_passage.count_documents(query)
        total_pages = max(1, (total + per_page - 1) // per_page) if total else 1
        if page > total_pages:
            page = total_pages
        # end if
        skip = (page - 1) * per_page
        passages = list(
            mgdDB.db_toefl_passage.find(query)
            .sort([("section_key", 1), ("rec_timestamp", -1)])
            .skip(skip)
            .limit(per_page)
        )
        for passage in passages:
            questions = list(
                mgdDB.db_toefl_question.find(
                    {"fk_passage_id": passage["pkey"], "is_deleted": False}
                ).sort("sort_order", 1)
            )
            passage["questions"] = questions
        # end for
        return {
            "status": "OK",
            "data": passages,
            "pagination": {
                "page"        : page,
                "per_page"    : per_page,
                "total"       : total,
                "total_pages" : total_pages,
            },
        }
    except Exception:
        print(traceback.format_exc())
        return {
            "status": "ERROR",
            "data": [],
            "pagination": {
                "page": 1,
                "per_page": BANK_DEFAULT_PER_PAGE,
                "total": 0,
                "total_pages": 1,
            },
        }
    # end try
# end def


def list_bank_passage_pkeys(expert_id=None, section_key="", question_mode=""):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        query = _bank_list_query(expert_id, section_key, question_mode)
        return {
            "status": "OK",
            "data": [
                p.get("pkey") for p in mgdDB.db_toefl_passage.find(query, {"pkey": 1})
                if p.get("pkey")
            ],
        }
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def get_all_passages_with_questions(section_id=None, expert_id=None):
    try:
        mgdDB   = database.get_db_conn(config.mainDB)
        query   = {"is_deleted": False}
        if section_id:
            query["fk_package_section_id"] = section_id
        # end if
        if expert_id:
            query["fk_expert_id"] = expert_id
        # end if
        passages = list(mgdDB.db_toefl_passage.find(query).sort("sort_order", 1))

        for passage in passages:
            questions = list(
                mgdDB.db_toefl_question.find(
                    {"fk_passage_id": passage["pkey"], "is_deleted": False}
                ).sort("sort_order", 1)
            )
            passage["questions"] = questions
        # end for

        return {"status": "OK", "data": passages}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def
