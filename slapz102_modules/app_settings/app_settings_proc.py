import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import traceback
import re
import json

import database
import config


FALLBACK_TEST_TYPES = [
    {
        "code": "B1",
        "label": "Goethe-Zertifikat B1",
        "sort_order": 1,
        "sections": [
            {"title": "Hören (Mendengarkan)", "section_type": "HOEREN", "duration_minutes": 40, "sort_order": 1},
            {"title": "Lesen (Membaca)", "section_type": "LESEN", "duration_minutes": 65, "sort_order": 2},
            {"title": "Schreiben (Menulis)", "section_type": "SCHREIBEN", "duration_minutes": 60, "sort_order": 3},
            {"title": "Sprechen (Berbicara)", "section_type": "SPRECHEN", "duration_minutes": 15, "sort_order": 4},
        ],
    },
]


FALLBACK_SUB_PLANS = [
    {
        "code": "FREE", "label": "Free", "tagline": "Coba simulasi dasar",
        "price_idr": 0, "price_quarterly_idr": 0, "price_yearly_idr": 0,
        "discount_monthly_pct": 0, "discount_quarterly_pct": 0, "discount_yearly_pct": 0,
        "ai_credits_monthly": 20, "sort_order": 1,
    },
    {
        "code": "BASIC", "label": "Basic", "tagline": "Latihan rutin semua level",
        "price_idr": 29000, "price_quarterly_idr": 84000, "price_yearly_idr": 290000,
        "discount_monthly_pct": 0, "discount_quarterly_pct": 3, "discount_yearly_pct": 17,
        "ai_credits_monthly": 150, "sort_order": 2,
    },
    {
        "code": "PRO", "label": "Pro", "tagline": "Serius target sertifikat",
        "price_idr": 59000, "price_quarterly_idr": 168000, "price_yearly_idr": 566000,
        "discount_monthly_pct": 0, "discount_quarterly_pct": 5, "discount_yearly_pct": 20,
        "ai_credits_monthly": 400, "sort_order": 3,
    },
    {
        "code": "PREMIUM", "label": "Premium", "tagline": "Persiapan maksimal + AI penuh",
        "price_idr": 99000, "price_quarterly_idr": 277000, "price_yearly_idr": 890000,
        "discount_monthly_pct": 0, "discount_quarterly_pct": 7, "discount_yearly_pct": 25,
        "ai_credits_monthly": 900, "sort_order": 4,
    },
]


# Siklus langganan: (kode, jumlah bulan, label id, label de)
SUB_CYCLES = [
    {"code": "MONTHLY",   "months": 1,  "label_id": "Bulanan",       "label_de": "Monatlich"},
    {"code": "QUARTERLY", "months": 3,  "label_id": "3 Bulan",       "label_de": "Quartal"},
    {"code": "YEARLY",    "months": 12, "label_id": "Tahunan",       "label_de": "Jährlich"},
]


def _cycle_def(cycle_code):
    for cyc in SUB_CYCLES:
        if cyc["code"] == str(cycle_code or "").upper().strip():
            return cyc
        # end if
    # end for
    return None
# end def


def compute_cycle_pricing(plan, cycle_code):
    """Hitung matrix harga satu siklus dari record paket langganan.

    Return dict: months, list_price, discount_pct, final_price, per_month, save_pct.
    list_price kuartal/tahunan 0 = otomatis (bulanan x bulan).
    """
    try:
        cyc     = _cycle_def(cycle_code)
        monthly = int(plan.get("price_idr", 0) or 0)
        if not cyc:
            return None
        # end if
        months = cyc["months"]
        if cyc["code"] == "MONTHLY":
            list_price   = monthly
            discount_pct = float(plan.get("discount_monthly_pct", 0) or 0)
        elif cyc["code"] == "QUARTERLY":
            list_price   = int(plan.get("price_quarterly_idr", 0) or 0) or (monthly * 3)
            discount_pct = float(plan.get("discount_quarterly_pct", 0) or 0)
        else:
            list_price   = int(plan.get("price_yearly_idr", 0) or 0) or (monthly * 12)
            discount_pct = float(plan.get("discount_yearly_pct", 0) or 0)
        # end if
        if discount_pct < 0:
            discount_pct = 0
        # end if
        if discount_pct > 90:
            discount_pct = 90
        # end if
        final_price = int(round(list_price * (100 - discount_pct) / 100.0 / 500.0) * 500)  # pembulatan ke 500
        if final_price < 0:
            final_price = 0
        # end if
        per_month = int(round(final_price / float(months))) if months else final_price
        save_pct  = 0
        if monthly > 0 and months > 1 and final_price > 0:
            save_pct = int(round((1 - float(final_price) / float(monthly * months)) * 100))
        # end if
        return {
            "cycle"       : cyc["code"],
            "months"      : months,
            "label_id"    : cyc["label_id"],
            "label_de"    : cyc["label_de"],
            "list_price"  : list_price,
            "discount_pct": discount_pct,
            "final_price" : final_price,
            "per_month"   : per_month,
            "save_pct"    : save_pct,
        }
    except Exception:
        print(traceback.format_exc())
        return None
    # end try
# end def


def build_pricing_matrix(plan):
    """Matrix harga ketiga siklus untuk satu paket — dipakai landing & area siswa."""
    matrix = {}
    for cyc in SUB_CYCLES:
        pricing = compute_cycle_pricing(plan, cyc["code"])
        if pricing:
            matrix[cyc["code"]] = pricing
        # end if
    # end for
    return matrix
# end def


def _seed_defaults():
    defaults = getattr(config, "G_TEST_TYPE_DEFAULTS", None) or FALLBACK_TEST_TYPES
    return defaults
# end def


def ensure_default_test_settings():
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        existing = mgdDB.db_level.count_documents({"is_deleted": False})
        if existing > 0:
            return {"status": "OK", "seeded": False}
        # end if
        for item in _seed_defaults():
            rec = database.new(mgdDB, "db_level")
            rec.put("code",       str(item.get("code", "")).upper().strip())
            rec.put("label",      item.get("label", "") or item.get("code", ""))
            rec.put("sort_order", int(item.get("sort_order", 0) or 0))
            rec.put("status",     "ACTIVE")
            rec.insert()
            for sec in item.get("sections", []):
                srec = database.new(mgdDB, "db_toefl_section_template")
                srec.put("fk_test_type_code", str(item.get("code", "")).upper().strip())
                srec.put("title",             sec.get("title", ""))
                srec.put("section_type",      str(sec.get("section_type", "")).upper().strip())
                srec.put("duration_minutes",  int(sec.get("duration_minutes", 0) or 0))
                srec.put("sort_order",        int(sec.get("sort_order", 0) or 0))
                srec.insert()
            # end for
        # end for
        return {"status": "OK", "seeded": True}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def get_test_types():
    try:
        ensure_default_test_settings()
        mgdDB = database.get_db_conn(config.mainDB)
        rows  = list(
            mgdDB.db_level.find({"is_deleted": False}).sort("sort_order", 1)
        )
        return {"status": "OK", "data": rows}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def get_sections_for_test_type(test_type_code):
    try:
        ensure_default_test_settings()
        mgdDB = database.get_db_conn(config.mainDB)
        code  = str(test_type_code or "").upper().strip()
        rows  = list(
            mgdDB.db_toefl_section_template.find(
                {"fk_test_type_code": code, "is_deleted": False}
            ).sort("sort_order", 1)
        )
        return {"status": "OK", "data": rows}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def get_settings_bundle():
    types = get_test_types().get("data", [])
    mgdDB = database.get_db_conn(config.mainDB)
    for item in types:
        item["sections"] = list(
            mgdDB.db_toefl_section_template.find(
                {"fk_test_type_code": item.get("code", ""), "is_deleted": False}
            ).sort("sort_order", 1)
        )
    # end for
    return {"status": "OK", "data": types}
# end def


GERMAN_CHAR_MAP = {"Ä": "AE", "Ö": "OE", "Ü": "UE", "ẞ": "SS", "ß": "SS"}


def _code_from_label(mgdDB, label, collection="db_level"):
    text = str(label or "").upper()
    for src, dst in GERMAN_CHAR_MAP.items():
        text = text.replace(src, dst)
    # end for
    base = re.sub(r"[^A-Z0-9]+", "-", text).strip("-")
    if not base:
        return ""
    # end if
    code   = base
    suffix = 2
    while mgdDB[collection].find_one({"code": code, "is_deleted": False}):
        code   = base + "-" + str(suffix)
        suffix += 1
    # end while
    return code
# end def


def create_test_type(code, label, sort_order=0):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        code  = str(code or "").upper().strip()
        if not code:
            code = _code_from_label(mgdDB, label)
        # end if
        if not code:
            return {"status": "ERROR", "message": "Nama level wajib diisi"}
        # end if
        found = mgdDB.db_level.find_one({"code": code, "is_deleted": False})
        if found:
            return {"status": "ERROR", "message": "Level dengan kode ini sudah ada"}
        # end if
        rec = database.new(mgdDB, "db_level")
        rec.put("code",       code)
        rec.put("label",      (label or code).strip())
        rec.put("sort_order", int(sort_order or 0))
        rec.put("status",     "ACTIVE")
        rec.insert()
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal menambah level"}
    # end try
# end def


def update_test_type(pkey, label, sort_order=0):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_level.update_one(
            {"pkey": pkey, "is_deleted": False},
            {"$set": {
                "label"     : (label or "").strip(),
                "sort_order": int(sort_order or 0),
            }}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def delete_test_type(pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        row   = mgdDB.db_level.find_one({"pkey": pkey, "is_deleted": False})
        if not row:
            return {"status": "ERROR"}
        # end if
        mgdDB.db_level.update_one({"pkey": pkey}, {"$set": {"is_deleted": True}})
        mgdDB.db_toefl_section_template.update_many(
            {"fk_test_type_code": row.get("code", "")},
            {"$set": {"is_deleted": True}}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def create_section_template(test_type_code, title, section_type, duration_minutes, sort_order=0):
    try:
        code = str(test_type_code or "").upper().strip()
        title = (title or "").strip()
        section_type = str(section_type or "").upper().strip()
        if not code or not title or not section_type:
            return {"status": "ERROR", "message": "Level, judul, dan kode bagian wajib diisi"}
        # end if
        mgdDB = database.get_db_conn(config.mainDB)
        rec = database.new(mgdDB, "db_toefl_section_template")
        rec.put("fk_test_type_code", code)
        rec.put("title",             title)
        rec.put("section_type",      section_type)
        rec.put("duration_minutes",  int(duration_minutes or 0))
        rec.put("sort_order",        int(sort_order or 0))
        rec.insert()
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal menambah bagian"}
    # end try
# end def


def update_section_template(pkey, title, section_type, duration_minutes, sort_order=0):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_toefl_section_template.update_one(
            {"pkey": pkey, "is_deleted": False},
            {"$set": {
                "title"            : (title or "").strip(),
                "section_type"     : str(section_type or "").upper().strip(),
                "duration_minutes" : int(duration_minutes or 0),
                "sort_order"       : int(sort_order or 0),
            }}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def delete_section_template(pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_toefl_section_template.update_one(
            {"pkey": pkey},
            {"$set": {"is_deleted": True}}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def get_test_names():
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        rows  = list(
            mgdDB.db_test_name.find({"is_deleted": False}).sort("sort_order", 1)
        )
        return {"status": "OK", "data": rows}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def create_test_name(label, sort_order=0):
    try:
        label = (label or "").strip()
        if not label:
            return {"status": "ERROR", "message": "Nama tes wajib diisi"}
        # end if
        mgdDB = database.get_db_conn(config.mainDB)
        rec   = database.new(mgdDB, "db_test_name")
        rec.put("code",       _code_from_label(mgdDB, label, "db_test_name"))
        rec.put("label",      label)
        rec.put("sort_order", int(sort_order or 0))
        rec.put("status",     "ACTIVE")
        rec.insert()
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal menambah nama tes"}
    # end try
# end def


def update_test_name(pkey, label, sort_order=0):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_test_name.update_one(
            {"pkey": pkey, "is_deleted": False},
            {"$set": {
                "label"     : (label or "").strip(),
                "sort_order": int(sort_order or 0),
            }}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def delete_test_name(pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_test_name.update_one(
            {"pkey": pkey},
            {"$set": {"is_deleted": True}}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def get_type_tests():
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        rows  = list(
            mgdDB.db_test_type.find({"is_deleted": False}).sort("sort_order", 1)
        )
        return {"status": "OK", "data": rows}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def create_type_test(label, description="", sort_order=0):
    try:
        label = (label or "").strip()
        if not label:
            return {"status": "ERROR", "message": "Nama bagian ujian wajib diisi"}
        # end if
        mgdDB = database.get_db_conn(config.mainDB)
        rec   = database.new(mgdDB, "db_test_type")
        rec.put("code",        _code_from_label(mgdDB, label, "db_test_type"))
        rec.put("label",       label)
        rec.put("description", (description or "").strip())
        rec.put("sort_order",  int(sort_order or 0))
        rec.put("status",      "ACTIVE")
        rec.insert()
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal menambah bagian ujian"}
    # end try
# end def


def update_type_test(pkey, label, description="", sort_order=0):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_test_type.update_one(
            {"pkey": pkey, "is_deleted": False},
            {"$set": {
                "label"      : (label or "").strip(),
                "description": (description or "").strip(),
                "sort_order" : int(sort_order or 0),
            }}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def delete_type_test(pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_test_type.update_one(
            {"pkey": pkey},
            {"$set": {"is_deleted": True}}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def get_type_test_by_pkey(pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        row   = mgdDB.db_test_type.find_one({"pkey": pkey, "is_deleted": False})
        return {"status": "OK", "data": row}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": None}
    # end try
# end def


def _plain(html_value):
    text = re.sub(r"<[^>]+>", " ", str(html_value or ""))
    return re.sub(r"\s+", " ", text).strip()
# end def


DUMP_JENIS = {
    "single"      : ("single",  "mc",    ""),
    "grouped"     : ("grouped", "mc",    ""),
    "rf_single"   : ("single",  "rf",    ""),
    "rf_grouped"  : ("grouped", "rf",    ""),
    "cloze"       : ("grouped", "cloze", "mc"),      # kartu soal A–D
    "cloze_select": ("grouped", "cloze", "select"),  # dropdown inline di teks
    "cloze_input" : ("grouped", "cloze", "input"),   # ketik jawaban (isian)
    "sprechen"    : ("sprechen", "speak", ""),       # bicara: rekam suara siswa
}

DUMP_JENIS_LABELS = [
    ("single",      "Soal Mandiri"),
    ("grouped",     "Kelompok Soal"),
    ("rf_single",   "Richtig/Falsch — Mandiri"),
    ("rf_grouped",  "Richtig/Falsch — Kelompok"),
    ("cloze",       "Lückentext (Pilihan Ganda)"),
    ("cloze_select", "Lückentext — Pilihan di Teks (dropdown)"),
    ("cloze_input",  "Lückentext — Ketik Jawaban (isian)"),
    ("sprechen",    "Sprechen — Soal Bicara (rekam suara)"),
]


def parse_dump_jenis(value):
    """Return (jenis, question_mode, answer_type, cloze_mode); tak dikenal jatuh ke 'single'."""
    jenis = str(value or "").lower().strip()
    if jenis not in DUMP_JENIS:
        jenis = "single"
    # end if
    mode, answer_type, cloze_mode = DUMP_JENIS[jenis]
    return jenis, mode, answer_type, cloze_mode
# end def


def dump_jenis_key(question_mode, answer_type, cloze_mode=""):
    answer_type = answer_type or "mc"
    if answer_type == "cloze":
        cloze_mode = cloze_mode or "mc"
        # end if
        for jenis, triple in DUMP_JENIS.items():
            if triple == (question_mode, answer_type, cloze_mode):
                return jenis
            # end if
        # end for
        return "cloze"
    # end if
    for jenis, triple in DUMP_JENIS.items():
        if triple[:2] == (question_mode, answer_type) and not triple[2]:
            return jenis
        # end if
    # end for
    return "grouped" if question_mode == "grouped" else "single"
# end def


def _answer_type_query(answer_type):
    # dump lama tidak punya field answer_type → dianggap mc
    return {"$in": ["mc", None]} if answer_type == "mc" else answer_type
# end def


def _cloze_mode_query(cloze_mode):
    # dump cloze lama tidak punya field cloze_mode → dianggap mc (kartu A–D)
    return {"$in": ["mc", None]} if cloze_mode in ("", "mc") else cloze_mode
# end def


def _validate_dump_item(item, question_mode, answer_type="mc", cloze_mode=""):
    if not isinstance(item, dict):
        return "bukan objek JSON"
    # end if
    nested = item.get("questions")
    if question_mode == "sprechen":
        # Soal bicara: instruksi (Aufgabe) ATAU teks soal wajib; gambar & Musterantwort opsional
        if nested:
            return "Soal Sprechen tidak memakai questions[]"
        # end if
        if not _plain(item.get("instruction")) and not _plain(item.get("question_text")):
            return "Sprechen wajib punya instruction (Aufgabe) atau question_text"
        # end if
        return ""
    # end if
    if question_mode == "grouped":
        if not isinstance(nested, list) or not nested:
            return "Kelompok Soal wajib punya questions[]"
        # end if
        for idx, q in enumerate(nested, start=1):
            if not isinstance(q, dict):
                return "questions[%s] bukan objek" % idx
            # end if
            if answer_type == "cloze" and cloze_mode == "input":
                if not str(q.get("answer_text") or "").strip():
                    return "questions[%s]: Lückentext isian wajib punya answer_text" % idx
                # end if
            elif answer_type == "cloze":
                if not all(str(q.get("option_" + k) or "").strip() for k in "abcd"):
                    return "questions[%s]: Lückentext wajib punya option_a–option_d" % idx
                # end if
            elif not _plain(q.get("question_text")):
                return "questions[%s] tidak punya question_text" % idx
            # end if
            if answer_type == "rf" and str(q.get("correct_answer") or "A").upper() not in ("A", "B"):
                return "questions[%s]: correct_answer Richtig/Falsch harus A (Richtig) atau B (Falsch)" % idx
            # end if
        # end for
        if answer_type == "cloze" and not _plain(item.get("content_text")):
            return "Lückentext wajib punya content_text berisi rumpang [1], [2], …"
        # end if
    else:
        if nested:
            return "Soal Mandiri tidak boleh punya questions[] (pilih jenis Kelompok)"
        # end if
        if not _plain(item.get("question_text")):
            return "question_text kosong"
        # end if
        if answer_type == "rf" and str(item.get("correct_answer") or "A").upper() not in ("A", "B"):
            return "correct_answer Richtig/Falsch harus A (Richtig) atau B (Falsch)"
        # end if
    # end if
    return ""
# end def


def _dump_title(item, question_mode):
    if question_mode == "sprechen":
        title = (item.get("title") or "").strip() or _plain(item.get("instruction")) or _plain(item.get("question_text"))
    elif question_mode == "grouped":
        title = (item.get("title") or "").strip() or _plain(item.get("content_text"))
    else:
        title = _plain(item.get("question_text"))
    # end if
    return (title or "Dump")[:80]
# end def


def get_type_test_dumps(test_type_code, question_mode="", limit=0, answer_type=None, cloze_mode=""):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        query = {"fk_test_type_code": str(test_type_code or "").upper().strip(), "is_deleted": False}
        if question_mode in ("single", "grouped"):
            query["question_mode"] = question_mode
        # end if
        if answer_type:
            query["answer_type"] = _answer_type_query(answer_type)
        # end if
        if answer_type == "cloze" and cloze_mode:
            query["cloze_mode"] = _cloze_mode_query(cloze_mode)
        # end if
        cursor = mgdDB.db_test_type_dump.find(query).sort([("sort_order", 1), ("rec_timestamp", 1)])
        if limit and int(limit) > 0:
            cursor = cursor.limit(int(limit))
        # end if
        return {"status": "OK", "data": list(cursor)}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def count_type_test_dumps():
    """Return {CODE: {jenis: n}} — jenis: single, grouped, rf_*, cloze, cloze_select, cloze_input."""
    counts = {}
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        rows  = mgdDB.db_test_type_dump.aggregate([
            {"$match": {"is_deleted": False}},
            {"$group": {
                "_id": {"code": "$fk_test_type_code", "mode": "$question_mode",
                        "atype": "$answer_type", "cmode": "$cloze_mode"},
                "n"  : {"$sum": 1},
            }},
        ])
        for row in rows:
            code  = row["_id"].get("code") or ""
            jenis = dump_jenis_key(
                row["_id"].get("mode") or "single",
                row["_id"].get("atype") or "mc",
                row["_id"].get("cmode") or "",
            )
            bucket = counts.setdefault(code, {key: 0 for key in DUMP_JENIS})
            bucket[jenis] = bucket.get(jenis, 0) + row["n"]
        # end for
    except Exception:
        print(traceback.format_exc())
    # end try
    return counts
# end def


def get_type_test_dump_by_pkey(dump_pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        row   = mgdDB.db_test_type_dump.find_one({"pkey": dump_pkey, "is_deleted": False})
        return {"status": "OK", "data": row}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": None}
    # end try
# end def


def create_type_test_dumps(test_type_code, question_mode, raw_json):
    """question_mode = jenis (single, grouped, rf_single, rf_grouped, cloze, cloze_select, cloze_input).
    raw_json boleh satu objek atau array objek — tiap objek jadi satu dump."""
    try:
        code = str(test_type_code or "").upper().strip()
        _jenis, mode, answer_type, cloze_mode = parse_dump_jenis(question_mode)
        try:
            data = json.loads(raw_json or "")
        except Exception as err:
            return {"status": "ERROR", "message": "JSON tidak valid: " + str(err)}
        # end try
        items = data if isinstance(data, list) else [data]
        if not items:
            return {"status": "ERROR", "message": "JSON kosong"}
        # end if
        for idx, item in enumerate(items, start=1):
            err = _validate_dump_item(item, mode, answer_type, cloze_mode)
            if err:
                return {"status": "ERROR", "message": "Item %s: %s" % (idx, err)}
            # end if
        # end for
        mgdDB = database.get_db_conn(config.mainDB)
        next_order = mgdDB.db_test_type_dump.count_documents({
            "fk_test_type_code": code, "question_mode": mode,
            "answer_type": _answer_type_query(answer_type), "is_deleted": False,
        }) + 1
        for item in items:
            rec = database.new(mgdDB, "db_test_type_dump")
            rec.put("fk_test_type_code", code)
            rec.put("question_mode",     mode)
            rec.put("answer_type",       answer_type)
            rec.put("cloze_mode",        cloze_mode)
            rec.put("title",             _dump_title(item, mode))
            rec.put("dump_json",         json.dumps(item, ensure_ascii=False))
            rec.put("sort_order",        next_order)
            rec.put("status",            "ACTIVE")
            rec.insert()
            next_order += 1
        # end for
        return {"status": "OK", "created": len(items)}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal menyimpan dump"}
    # end try
# end def


def update_type_test_dump(pkey, question_mode, raw_json):
    try:
        _jenis, mode, answer_type, cloze_mode = parse_dump_jenis(question_mode)
        try:
            item = json.loads(raw_json or "")
        except Exception as err:
            return {"status": "ERROR", "message": "JSON tidak valid: " + str(err)}
        # end try
        if isinstance(item, list):
            if len(item) != 1:
                return {"status": "ERROR", "message": "Ubah dump hanya untuk satu objek"}
            # end if
            item = item[0]
        # end if
        err = _validate_dump_item(item, mode, answer_type, cloze_mode)
        if err:
            return {"status": "ERROR", "message": err}
        # end if
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_test_type_dump.update_one(
            {"pkey": pkey, "is_deleted": False},
            {"$set": {
                "question_mode": mode,
                "answer_type"  : answer_type,
                "cloze_mode"   : cloze_mode,
                "title"        : _dump_title(item, mode),
                "dump_json"    : json.dumps(item, ensure_ascii=False),
            }}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal mengubah dump"}
    # end try
# end def


def delete_type_test_dump(pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_test_type_dump.update_one(
            {"pkey": pkey},
            {"$set": {"is_deleted": True}}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def ensure_default_sub_plans():
    try:
        defaults = getattr(config, "G_SUB_PLAN_DEFAULTS", None) or FALLBACK_SUB_PLANS
        mgdDB    = database.get_db_conn(config.mainDB)
        existing = mgdDB.db_subscription_plan.count_documents({"is_deleted": False})
        if existing > 0:
            _backfill_plan_duration_fields(mgdDB, defaults)
            return {"status": "OK", "seeded": False}
        # end if
        for item in defaults:
            rec = database.new(mgdDB, "db_subscription_plan")
            rec.put("code",                  str(item.get("code", "")).upper().strip())
            rec.put("label",                 item.get("label", "") or item.get("code", ""))
            rec.put("tagline",               item.get("tagline", "") or "")
            rec.put("price_idr",             int(item.get("price_idr", 0) or 0))
            rec.put("price_quarterly_idr",   int(item.get("price_quarterly_idr", 0) or 0))
            rec.put("price_yearly_idr",      int(item.get("price_yearly_idr", 0) or 0))
            rec.put("discount_monthly_pct",  float(item.get("discount_monthly_pct", 0) or 0))
            rec.put("discount_quarterly_pct", float(item.get("discount_quarterly_pct", 0) or 0))
            rec.put("discount_yearly_pct",   float(item.get("discount_yearly_pct", 0) or 0))
            rec.put("ai_credits_monthly",    int(item.get("ai_credits_monthly", 0) or 0))
            rec.put("sort_order",            int(item.get("sort_order", 0) or 0))
            rec.put("status",                "ACTIVE")
            rec.insert()
        # end for
        return {"status": "OK", "seeded": True}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


# field durasi baru yang di-backfill ke record lama (hanya jika belum ada — nilai admin tak pernah ditimpa)
_PLAN_DURATION_FIELDS = [
    "tagline",
    "price_quarterly_idr",
    "price_yearly_idr",
    "discount_monthly_pct",
    "discount_quarterly_pct",
    "discount_yearly_pct",
]


def _backfill_plan_duration_fields(mgdDB, defaults):
    try:
        for item in defaults:
            code = str(item.get("code", "")).upper().strip()
            row  = mgdDB.db_subscription_plan.find_one({"code": code, "is_deleted": False})
            if not row:
                continue
            # end if
            missing = [f for f in _PLAN_DURATION_FIELDS if f not in row]
            if not missing:
                continue
            # end if
            patch = {}
            for f in missing:
                if f == "tagline":
                    patch[f] = item.get("tagline", "") or ""
                elif f.startswith("price_"):
                    patch[f] = int(item.get(f, 0) or 0)
                else:
                    patch[f] = float(item.get(f, 0) or 0)
                # end if
            # end for
            mgdDB.db_subscription_plan.update_one({"pkey": row.get("pkey")}, {"$set": patch})
        # end for
    except Exception:
        print(traceback.format_exc())
    # end try
# end def


def get_sub_plans():
    try:
        ensure_default_sub_plans()
        mgdDB = database.get_db_conn(config.mainDB)
        rows  = list(
            mgdDB.db_subscription_plan.find({"is_deleted": False}).sort("sort_order", 1)
        )
        return {"status": "OK", "data": rows}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def get_public_sub_plans():
    """Paket langganan ACTIVE lengkap dengan matrix harga per siklus — untuk landing & siswa."""
    try:
        rows = get_sub_plans().get("data", [])
        public = []
        for plan in rows:
            if str(plan.get("status", "ACTIVE")).upper() != "ACTIVE":
                continue
            # end if
            plan["pricing"] = build_pricing_matrix(plan)
            public.append(plan)
        # end for
        return {"status": "OK", "data": public}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def _clean_pct(value):
    try:
        pct = float(value or 0)
    except Exception:
        pct = 0.0
    # end try
    if pct < 0:
        pct = 0.0
    # end if
    if pct > 90:
        pct = 90.0
    # end if
    return pct
# end def


def create_sub_plan(
    code, label, tagline="",
    price_idr=0, price_quarterly_idr=0, price_yearly_idr=0,
    discount_monthly_pct=0, discount_quarterly_pct=0, discount_yearly_pct=0,
    ai_credits_monthly=0, sort_order=0, status="ACTIVE",
):
    try:
        code = str(code or "").upper().strip()
        if not code:
            return {"status": "ERROR", "message": "Kode paket wajib diisi"}
        # end if
        clean_status = str(status or "ACTIVE").upper().strip()
        if clean_status not in ("ACTIVE", "INACTIVE"):
            clean_status = "ACTIVE"
        # end if
        mgdDB = database.get_db_conn(config.mainDB)
        found = mgdDB.db_subscription_plan.find_one({"code": code, "is_deleted": False})
        if found:
            return {"status": "ERROR", "message": "Kode paket sudah ada"}
        # end if
        rec = database.new(mgdDB, "db_subscription_plan")
        rec.put("code",                  code)
        rec.put("label",                 (label or code).strip())
        rec.put("tagline",               (tagline or "").strip())
        rec.put("price_idr",             int(price_idr or 0))
        rec.put("price_quarterly_idr",   int(price_quarterly_idr or 0))
        rec.put("price_yearly_idr",      int(price_yearly_idr or 0))
        rec.put("discount_monthly_pct",  _clean_pct(discount_monthly_pct))
        rec.put("discount_quarterly_pct", _clean_pct(discount_quarterly_pct))
        rec.put("discount_yearly_pct",   _clean_pct(discount_yearly_pct))
        rec.put("ai_credits_monthly",    int(ai_credits_monthly or 0))
        rec.put("sort_order",            int(sort_order or 0))
        rec.put("status",                clean_status)
        rec.insert()
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal menambah paket"}
    # end try
# end def


def update_sub_plan(
    pkey, label, tagline="",
    price_idr=0, price_quarterly_idr=0, price_yearly_idr=0,
    discount_monthly_pct=0, discount_quarterly_pct=0, discount_yearly_pct=0,
    ai_credits_monthly=0, sort_order=0, status="ACTIVE",
):
    try:
        clean_status = str(status or "ACTIVE").upper().strip()
        if clean_status not in ("ACTIVE", "INACTIVE"):
            clean_status = "ACTIVE"
        # end if
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_subscription_plan.update_one(
            {"pkey": pkey, "is_deleted": False},
            {"$set": {
                "label"                 : (label or "").strip(),
                "tagline"               : (tagline or "").strip(),
                "price_idr"             : int(price_idr or 0),
                "price_quarterly_idr"   : int(price_quarterly_idr or 0),
                "price_yearly_idr"      : int(price_yearly_idr or 0),
                "discount_monthly_pct"  : _clean_pct(discount_monthly_pct),
                "discount_quarterly_pct": _clean_pct(discount_quarterly_pct),
                "discount_yearly_pct"   : _clean_pct(discount_yearly_pct),
                "ai_credits_monthly"    : int(ai_credits_monthly or 0),
                "sort_order"            : int(sort_order or 0),
                "status"                : clean_status,
            }}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def delete_sub_plan(pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_subscription_plan.update_one(
            {"pkey": pkey},
            {"$set": {"is_deleted": True}}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def
