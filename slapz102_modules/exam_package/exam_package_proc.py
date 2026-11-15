import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import traceback

import database
import config
import idgen


def _section_templates_for(test_type):
    from app_settings import app_settings_proc
    return app_settings_proc.get_sections_for_test_type(test_type).get("data", [])
# end def


def ensure_package_numbers(mgdDB=None):
    """Beri package_no berurutan ke paket lama yang belum punya nomor."""
    if mgdDB is None:
        mgdDB = database.get_db_conn(config.mainDB)
    # end if
    missing = list(mgdDB.db_toefl_package.find(
        {"$or": [{"package_no": {"$exists": False}}, {"package_no": {"$in": [0, None]}}]},
        {"pkey": 1}
    ).sort("rec_timestamp", 1))
    if not missing:
        return
    # end if
    last = mgdDB.db_toefl_package.find_one({"package_no": {"$gt": 0}}, sort=[("package_no", -1)])
    next_no = (last.get("package_no", 0) if last else 0) + 1
    for row in missing:
        mgdDB.db_toefl_package.update_one({"pkey": row.get("pkey")}, {"$set": {"package_no": next_no}})
        next_no += 1
    # end for
# end def


def _next_package_no(mgdDB):
    ensure_package_numbers(mgdDB)
    last = mgdDB.db_toefl_package.find_one({"package_no": {"$gt": 0}}, sort=[("package_no", -1)])
    return (last.get("package_no", 0) if last else 0) + 1
# end def


def get_package_by_ref(package_ref):
    """package_ref boleh nomor urut ("3") atau pkey lama."""
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        ensure_package_numbers(mgdDB)
        ref   = str(package_ref or "").strip()
        if ref.isdigit():
            query = {"package_no": int(ref), "is_deleted": False}
        else:
            query = {"pkey": ref, "is_deleted": False}
        # end if
        return {"status": "OK", "data": mgdDB.db_toefl_package.find_one(query)}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": None}
    # end try
# end def


def get_all_packages(status=None):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        ensure_package_numbers(mgdDB)
        query = {"is_deleted": False}
        if status:
            query["status"] = status
        # end if
        packages = list(mgdDB.db_toefl_package.find(query).sort("rec_timestamp", -1))
        for package in packages:
            package["total_questions"] = recount_package(mgdDB, package.get("pkey"))
        # end for
        return {"status": "OK", "data": packages}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def get_package_by_id(package_pkey):
    try:
        mgdDB   = database.get_db_conn(config.mainDB)
        package = mgdDB.db_toefl_package.find_one({"pkey": package_pkey, "is_deleted": False})
        return {"status": "OK", "data": package}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": None}
    # end try
# end def


def create_package(title, test_type, description, price_basic=0, price_premium=0, expert_id="",
                   level_code="", test_name_code=""):
    """Seksi tidak lagi dibuat otomatis — expert menambah seksi sendiri di halaman paket."""
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        level_code = str(level_code or test_type or "").upper().strip()

        rec = database.new(mgdDB, "db_toefl_package")
        rec.put("package_id",       idgen._get_unique_id())
        rec.put("package_no",       _next_package_no(mgdDB))
        rec.put("title",            title)
        rec.put("test_type",        level_code)
        rec.put("level_code",       level_code)
        rec.put("test_name_code",   str(test_name_code or "").upper().strip())
        rec.put("description",      description)
        rec.put("price_basic",      int(price_basic or 0))
        rec.put("price_premium",    int(price_premium or 0))
        rec.put("status",           "DRAFT")
        rec.put("fk_expert_id",     expert_id)
        rec.put("total_questions",  0)
        rec.put("duration_minutes", 0)
        rec.put("cover_image",      "")
        package_pkey = rec._mongo_record.get("pkey", "")
        package_no   = rec._mongo_record.get("package_no", 0)
        rec.insert()

        return {"status": "OK", "package_pkey": package_pkey, "package_no": package_no}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal membuat paket"}
    # end try
# end def


def update_package(package_pkey, title, description, price_basic=None, price_premium=None,
                   level_code=None, test_name_code=None):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        fields = {"title": title, "description": description}
        if price_basic is not None:
            fields["price_basic"] = int(price_basic or 0)
        # end if
        if price_premium is not None:
            fields["price_premium"] = int(price_premium or 0)
        # end if
        if level_code is not None:
            fields["level_code"] = str(level_code or "").upper().strip()
            fields["test_type"]  = fields["level_code"]
        # end if
        if test_name_code is not None:
            fields["test_name_code"] = str(test_name_code or "").upper().strip()
        # end if
        mgdDB.db_toefl_package.update_one({"pkey": package_pkey}, {"$set": fields})
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def publish_package(package_pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        section_pkeys = [
            s.get("pkey") for s in mgdDB.db_toefl_package_section.find(
                {"fk_package_id": package_pkey, "is_deleted": False}, {"pkey": 1}
            ) if s.get("pkey")
        ]
        passage_pkeys = []
        seen = set()
        for section_pkey in section_pkeys:
            for pk in get_passage_pkeys_for_section(section_pkey, mgdDB):
                if pk and pk not in seen:
                    seen.add(pk)
                    passage_pkeys.append(pk)
                # end if
            # end for
        # end for
        total = 0
        if passage_pkeys:
            total = mgdDB.db_toefl_question.count_documents({
                "fk_passage_id": {"$in": passage_pkeys},
                "is_deleted": False,
            })
        # end if
        mgdDB.db_toefl_package.update_one(
            {"pkey": package_pkey},
            {"$set": {"status": "PUBLISHED", "total_questions": total}}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def unpublish_package(package_pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_toefl_package.update_one(
            {"pkey": package_pkey},
            {"$set": {"status": "DRAFT"}}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def delete_package(package_pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        section_pkeys = [
            s.get("pkey") for s in mgdDB.db_toefl_package_section.find(
                {"fk_package_id": package_pkey}, {"pkey": 1}
            ) if s.get("pkey")
        ]
        mgdDB.db_toefl_package.update_one({"pkey": package_pkey}, {"$set": {"is_deleted": True}})
        mgdDB.db_toefl_package_section.update_many({"fk_package_id": package_pkey}, {"$set": {"is_deleted": True}})
        mgdDB.db_toefl_package_part.update_many({"fk_package_id": package_pkey}, {"$set": {"is_deleted": True}})
        if section_pkeys:
            mgdDB.db_toefl_section_item.update_many(
                {"fk_package_section_id": {"$in": section_pkeys}},
                {"$set": {"is_deleted": True}}
            )
        # end if
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def get_sections_by_package(package_pkey):
    try:
        mgdDB    = database.get_db_conn(config.mainDB)
        sections = list(
            mgdDB.db_toefl_package_section.find(
                {"fk_package_id": package_pkey, "is_deleted": False}
            ).sort("sort_order", 1)
        )
        return {"status": "OK", "data": sections}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def get_section_by_id(section_pkey):
    try:
        mgdDB   = database.get_db_conn(config.mainDB)
        section = mgdDB.db_toefl_package_section.find_one({"pkey": section_pkey, "is_deleted": False})
        return {"status": "OK", "data": section}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": None}
    # end try
# end def


def get_package_with_sections_and_questions(package_pkey):
    try:
        mgdDB   = database.get_db_conn(config.mainDB)
        package = mgdDB.db_toefl_package.find_one({"pkey": package_pkey, "is_deleted": False})
        if not package:
            return {"status": "ERROR", "data": None}
        # end if

        sections = list(
            mgdDB.db_toefl_package_section.find(
                {"fk_package_id": package_pkey, "is_deleted": False}
            ).sort("sort_order", 1)
        )

        all_passage_pkeys = []
        for section in sections:
            passages = load_passages_for_section(section["pkey"], mgdDB)
            qcount = 0
            for passage in passages:
                qcount += len(passage.get("questions") or [])
                all_passage_pkeys.append(passage.get("pkey"))
            # end for
            section["passages"] = passages
            section["question_count"] = qcount
        # end for
        usage = get_passage_usage_map(all_passage_pkeys, mgdDB)
        for section in sections:
            for passage in section.get("passages") or []:
                pkgs = usage.get(passage.get("pkey"), [])
                passage["used_in_packages"] = pkgs
                passage["used_in_other"] = [x for x in pkgs if x.get("pkey") != package_pkey]
            # end for
            parts = get_parts_for_section(section["pkey"], mgdDB)
            for part in parts:
                part["passages"] = [
                    p for p in section.get("passages") or [] if p.get("part_pkey") == part.get("pkey")
                ]
                part["question_count"] = sum(len(p.get("questions") or []) for p in part["passages"])
            # end for
            section["parts"] = parts
            section["unassigned_passages"] = [
                p for p in section.get("passages") or [] if not p.get("part_pkey")
            ]
        # end for

        package["sections"] = sections
        package["total_questions"] = sum(s.get("question_count", 0) for s in sections)
        return {"status": "OK", "data": package}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": None}
    # end try
# end def


def _live_passage_pkeys(mgdDB, pkeys):
    wanted = []
    seen = set()
    for pk in pkeys or []:
        if pk and pk not in seen:
            seen.add(pk)
            wanted.append(pk)
        # end if
    # end for
    if not wanted:
        return []
    # end if
    live = set(
        p.get("pkey") for p in mgdDB.db_toefl_passage.find(
            {"pkey": {"$in": wanted}, "is_deleted": False},
            {"pkey": 1}
        ) if p.get("pkey")
    )
    return [pk for pk in wanted if pk in live]
# end def


def _detach_deleted_passages(mgdDB, section_pkey, pkeys):
    if not section_pkey or not pkeys:
        return
    # end if
    mgdDB.db_toefl_section_item.update_many(
        {
            "fk_package_section_id": section_pkey,
            "fk_passage_id": {"$in": list(pkeys)},
            "is_deleted": False,
        },
        {"$set": {"is_deleted": True}}
    )
# end def


def get_passage_pkeys_for_section(section_pkey, mgdDB=None):
    if not section_pkey:
        return []
    # end if
    if mgdDB is None:
        mgdDB = database.get_db_conn(config.mainDB)
    # end if
    uses_items = mgdDB.db_toefl_section_item.count_documents(
        {"fk_package_section_id": section_pkey}
    ) > 0
    if uses_items:
        items = list(
            mgdDB.db_toefl_section_item.find(
                {"fk_package_section_id": section_pkey, "is_deleted": False}
            ).sort("sort_order", 1)
        )
        raw_pkeys = []
        seen = set()
        for item in items:
            pk = item.get("fk_passage_id")
            if pk and pk not in seen:
                seen.add(pk)
                raw_pkeys.append(pk)
            # end if
        # end for
        live_pkeys = _live_passage_pkeys(mgdDB, raw_pkeys)
        stale = [pk for pk in raw_pkeys if pk not in live_pkeys]
        _detach_deleted_passages(mgdDB, section_pkey, stale)
        return live_pkeys
    # end if
    passages = list(
        mgdDB.db_toefl_passage.find(
            {"fk_package_section_id": section_pkey, "is_deleted": False}
        ).sort("sort_order", 1)
    )
    return [p.get("pkey") for p in passages if p.get("pkey")]
# end def


def load_passages_for_section(section_pkey, mgdDB=None):
    if mgdDB is None:
        mgdDB = database.get_db_conn(config.mainDB)
    # end if
    pkeys = get_passage_pkeys_for_section(section_pkey, mgdDB)
    if not pkeys:
        return []
    # end if
    found = list(
        mgdDB.db_toefl_passage.find(
            {"pkey": {"$in": pkeys}, "is_deleted": False}
        )
    )
    by_id = {p.get("pkey"): p for p in found}
    passages = [by_id[pk] for pk in pkeys if pk in by_id]
    for passage in passages:
        passage["questions"] = list(
            mgdDB.db_toefl_question.find(
                {"fk_passage_id": passage["pkey"], "is_deleted": False}
            ).sort("sort_order", 1)
        )
    # end for
    _apply_parts(mgdDB, section_pkey, passages)
    return passages
# end def


def get_parts_for_section(section_pkey, mgdDB=None):
    if mgdDB is None:
        mgdDB = database.get_db_conn(config.mainDB)
    # end if
    return list(
        mgdDB.db_toefl_package_part.find(
            {"fk_package_section_id": section_pkey, "is_deleted": False}
        ).sort([("sort_order", 1), ("rec_timestamp", 1)])
    )
# end def


def _apply_parts(mgdDB, section_pkey, passages):
    """Isi part_pkey/part_name di tiap passage lalu urutkan: tanpa bagian dulu, lalu per bagian."""
    parts = get_parts_for_section(section_pkey, mgdDB)
    if not parts:
        for passage in passages:
            passage["part_pkey"] = ""
            passage["part_name"] = ""
        # end for
        return passages
    # end if
    part_by_id = {p.get("pkey"): p for p in parts}
    part_rank  = {p.get("pkey"): idx for idx, p in enumerate(parts, start=1)}
    item_part  = {}
    for item in mgdDB.db_toefl_section_item.find(
        {"fk_package_section_id": section_pkey, "is_deleted": False},
        {"fk_passage_id": 1, "fk_part_id": 1}
    ):
        item_part[item.get("fk_passage_id")] = item.get("fk_part_id") or ""
    # end for
    for passage in passages:
        part_pkey = item_part.get(passage.get("pkey"), "")
        if part_pkey not in part_by_id:
            part_pkey = ""
        # end if
        passage["part_pkey"] = part_pkey
        passage["part_name"] = part_by_id[part_pkey].get("name", "") if part_pkey else ""
    # end for
    passages.sort(key=lambda p: part_rank.get(p.get("part_pkey"), 0))
    return passages
# end def


def _ensure_section_items(mgdDB, section_pkey):
    existing = mgdDB.db_toefl_section_item.count_documents(
        {"fk_package_section_id": section_pkey}
    )
    if existing > 0:
        return
    # end if
    legacy = list(
        mgdDB.db_toefl_passage.find(
            {"fk_package_section_id": section_pkey, "is_deleted": False}
        ).sort("sort_order", 1)
    )
    for idx, passage in enumerate(legacy, start=1):
        rec = database.new(mgdDB, "db_toefl_section_item")
        rec.put("fk_package_section_id", section_pkey)
        rec.put("fk_passage_id",         passage.get("pkey", ""))
        rec.put("sort_order",            idx)
        rec.insert()
    # end for
# end def


def _refresh_section_and_package_counts(mgdDB, package_pkey, section_pkey):
    pkeys = get_passage_pkeys_for_section(section_pkey, mgdDB)
    qcount = 0
    if pkeys:
        qcount = mgdDB.db_toefl_question.count_documents({
            "fk_passage_id": {"$in": pkeys},
            "is_deleted": False,
        })
    # end if
    mgdDB.db_toefl_package_section.update_one(
        {"pkey": section_pkey},
        {"$set": {"question_count": qcount}}
    )
    if not package_pkey:
        return
    # end if
    section_pkeys = [
        s.get("pkey") for s in mgdDB.db_toefl_package_section.find(
            {"fk_package_id": package_pkey, "is_deleted": False}, {"pkey": 1}
        ) if s.get("pkey")
    ]
    all_pkeys = []
    seen = set()
    for spk in section_pkeys:
        for pk in get_passage_pkeys_for_section(spk, mgdDB):
            if pk and pk not in seen:
                seen.add(pk)
                all_pkeys.append(pk)
            # end if
        # end for
    # end for
    total = 0
    if all_pkeys:
        total = mgdDB.db_toefl_question.count_documents({
            "fk_passage_id": {"$in": all_pkeys},
            "is_deleted": False,
        })
    # end if
    mgdDB.db_toefl_package.update_one(
        {"pkey": package_pkey},
        {"$set": {"total_questions": total}}
    )
    return total
# end def


def recount_package(mgdDB, package_pkey):
    if not package_pkey:
        return 0
    # end if
    if mgdDB is None:
        mgdDB = database.get_db_conn(config.mainDB)
    # end if
    sections = list(
        mgdDB.db_toefl_package_section.find(
            {"fk_package_id": package_pkey, "is_deleted": False},
            {"pkey": 1}
        )
    )
    all_pkeys = []
    seen = set()
    for section in sections:
        section_pkey = section.get("pkey")
        pkeys = get_passage_pkeys_for_section(section_pkey, mgdDB)
        qcount = 0
        if pkeys:
            qcount = mgdDB.db_toefl_question.count_documents({
                "fk_passage_id": {"$in": pkeys},
                "is_deleted": False,
            })
        # end if
        mgdDB.db_toefl_package_section.update_one(
            {"pkey": section_pkey},
            {"$set": {"question_count": qcount}}
        )
        for pk in pkeys:
            if pk and pk not in seen:
                seen.add(pk)
                all_pkeys.append(pk)
            # end if
        # end for
    # end for
    total = 0
    if all_pkeys:
        total = mgdDB.db_toefl_question.count_documents({
            "fk_passage_id": {"$in": all_pkeys},
            "is_deleted": False,
        })
    # end if
    mgdDB.db_toefl_package.update_one(
        {"pkey": package_pkey},
        {"$set": {"total_questions": total}}
    )
    return total
# end def


def recount_packages_for_passages(passage_pkeys):
    pkeys = [pk for pk in (passage_pkeys or []) if pk]
    if not pkeys:
        return
    # end if
    mgdDB = database.get_db_conn(config.mainDB)
    section_ids = set()
    for item in mgdDB.db_toefl_section_item.find(
        {"fk_passage_id": {"$in": pkeys}},
        {"fk_package_section_id": 1}
    ):
        if item.get("fk_package_section_id"):
            section_ids.add(item.get("fk_package_section_id"))
        # end if
    # end for
    for passage in mgdDB.db_toefl_passage.find(
        {"pkey": {"$in": pkeys}},
        {"fk_package_section_id": 1}
    ):
        if passage.get("fk_package_section_id"):
            section_ids.add(passage.get("fk_package_section_id"))
        # end if
    # end for
    if not section_ids:
        return
    # end if
    package_ids = set()
    for section in mgdDB.db_toefl_package_section.find(
        {"pkey": {"$in": list(section_ids)}},
        {"fk_package_id": 1}
    ):
        if section.get("fk_package_id"):
            package_ids.add(section.get("fk_package_id"))
        # end if
    # end for
    for package_pkey in package_ids:
        recount_package(mgdDB, package_pkey)
    # end for
# end def


def attach_passage_to_section(section_pkey, passage_pkey, package_pkey="", part_pkey=None):
    """part_pkey=None: biarkan bagian apa adanya; "" = tanpa bagian; pkey = pindah/masuk ke bagian itu."""
    try:
        if not section_pkey or not passage_pkey:
            return {"status": "ERROR"}
        # end if
        mgdDB = database.get_db_conn(config.mainDB)
        _ensure_section_items(mgdDB, section_pkey)
        existing = mgdDB.db_toefl_section_item.find_one({
            "fk_package_section_id": section_pkey,
            "fk_passage_id":         passage_pkey,
            "is_deleted":            False,
        })
        if existing:
            if part_pkey is not None and (existing.get("fk_part_id") or "") != part_pkey:
                mgdDB.db_toefl_section_item.update_one(
                    {"pkey": existing.get("pkey")},
                    {"$set": {"fk_part_id": part_pkey}}
                )
            # end if
            return {"status": "OK"}
        # end if
        deleted = mgdDB.db_toefl_section_item.find_one({
            "fk_package_section_id": section_pkey,
            "fk_passage_id":         passage_pkey,
            "is_deleted":            True,
        })
        if deleted:
            mgdDB.db_toefl_section_item.update_one(
                {"pkey": deleted.get("pkey")},
                {"$set": {"is_deleted": False, "fk_part_id": part_pkey or ""}}
            )
        else:
            max_doc = mgdDB.db_toefl_section_item.find_one(
                {"fk_package_section_id": section_pkey, "is_deleted": False},
                sort=[("sort_order", -1)]
            )
            next_order = (max_doc.get("sort_order", 0) + 1) if max_doc else 1
            rec = database.new(mgdDB, "db_toefl_section_item")
            rec.put("fk_package_section_id", section_pkey)
            rec.put("fk_passage_id",         passage_pkey)
            rec.put("fk_part_id",            part_pkey or "")
            rec.put("sort_order",            next_order)
            rec.insert()
        # end if
        if package_pkey:
            _refresh_section_and_package_counts(mgdDB, package_pkey, section_pkey)
        # end if
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def detach_passage_from_section(section_pkey, passage_pkey, package_pkey=""):
    try:
        if not section_pkey or not passage_pkey:
            return {"status": "ERROR"}
        # end if
        mgdDB = database.get_db_conn(config.mainDB)
        _ensure_section_items(mgdDB, section_pkey)
        mgdDB.db_toefl_section_item.update_many(
            {
                "fk_package_section_id": section_pkey,
                "fk_passage_id":         passage_pkey,
            },
            {"$set": {"is_deleted": True}}
        )
        if package_pkey:
            _refresh_section_and_package_counts(mgdDB, package_pkey, section_pkey)
        # end if
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def sync_section_passages(package_pkey, section_pkey, passage_pkeys, part_pkey=None):
    """part_pkey=None: sinkron seluruh seksi; selain itu hanya item di bagian tsb ("" = tanpa bagian)."""
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        section = mgdDB.db_toefl_package_section.find_one({
            "pkey": section_pkey,
            "fk_package_id": package_pkey,
            "is_deleted": False,
        })
        if not section:
            return {"status": "ERROR"}
        # end if
        _ensure_section_items(mgdDB, section_pkey)
        wanted = []
        seen = set()
        for pk in passage_pkeys or []:
            if pk and pk not in seen:
                seen.add(pk)
                wanted.append(pk)
            # end if
        # end for
        current_items = list(
            mgdDB.db_toefl_section_item.find(
                {"fk_package_section_id": section_pkey, "is_deleted": False}
            )
        )
        current = set()
        for item in current_items:
            pk = item.get("fk_passage_id")
            if part_pkey is not None and (item.get("fk_part_id") or "") != part_pkey:
                continue
            # end if
            if pk:
                current.add(pk)
            # end if
        # end for
        for pk in wanted:
            if pk not in current:
                attach_passage_to_section(section_pkey, pk, part_pkey=part_pkey)
            # end if
        # end for
        for pk in current:
            if pk not in seen:
                detach_passage_from_section(section_pkey, pk)
            # end if
        # end for
        _refresh_section_and_package_counts(mgdDB, package_pkey, section_pkey)
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def get_bank_candidates_for_section(section, expert_id=None, part_pkey=None):
    """part_pkey diisi: 'attached' = sudah di bagian ini, 'in_part_name' = ada di bagian lain seksi ini."""
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        query = {"is_deleted": False}
        passages = list(mgdDB.db_toefl_passage.find(query).sort("rec_timestamp", -1))
        section_key = (section.get("section_type") or "").lower().strip()
        in_section = set(get_passage_pkeys_for_section(section.get("pkey"), mgdDB))
        attached = in_section
        other_part_name = {}
        if part_pkey is not None:
            part_names = {p.get("pkey"): p.get("name", "") for p in get_parts_for_section(section.get("pkey"), mgdDB)}
            item_part = {}
            for item in mgdDB.db_toefl_section_item.find(
                {"fk_package_section_id": section.get("pkey"), "is_deleted": False},
                {"fk_passage_id": 1, "fk_part_id": 1}
            ):
                fk_part = item.get("fk_part_id") or ""
                item_part[item.get("fk_passage_id")] = fk_part if fk_part in part_names else ""
            # end for
            attached = set(pk for pk in in_section if item_part.get(pk, "") == part_pkey)
            for pk in in_section - attached:
                other_part_name[pk] = part_names.get(item_part.get(pk, ""), "") or "Tanpa bagian"
            # end for
        # end if
        result = []
        for passage in passages:
            questions = list(
                mgdDB.db_toefl_question.find(
                    {"fk_passage_id": passage.get("pkey"), "is_deleted": False}
                ).sort("sort_order", 1)
            )
            is_sprechen = (passage.get("question_mode") or "") == "sprechen"
            if not questions and not is_sprechen:
                continue
            # end if
            sk = (passage.get("section_key") or "").lower().strip()
            is_attached = passage.get("pkey") in attached
            if not (is_attached or passage.get("pkey") in in_section or sk == section_key or sk == ""):
                continue
            # end if
            passage["questions"] = questions
            passage["attached"] = is_attached
            passage["in_part_name"] = other_part_name.get(passage.get("pkey"), "")
            passage["question_count"] = len(questions)
            result.append(passage)
        # end for
        usage = get_passage_usage_map([p.get("pkey") for p in result], mgdDB)
        current_pkg = section.get("fk_package_id", "")
        for passage in result:
            pkgs = usage.get(passage.get("pkey"), [])
            passage["used_in_packages"] = pkgs
            passage["used_in_count"] = len(pkgs)
            passage["used_in_other"] = [x for x in pkgs if x.get("pkey") != current_pkg]
        # end for
        result.sort(key=lambda p: (0 if p.get("attached") else 1, (p.get("title") or "").lower()))
        return {"status": "OK", "data": result}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": []}
    # end try
# end def


def add_section(package_pkey, test_type_code, duration_minutes=0):
    """Tambah seksi dari Pengaturan > Tipe Tes; satu tipe tes hanya sekali per paket."""
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        code  = str(test_type_code or "").upper().strip()
        type_test = mgdDB.db_test_type.find_one({"code": code, "is_deleted": False})
        if not type_test:
            return {"status": "ERROR", "message": "Tipe tes tidak ditemukan"}
        # end if
        if mgdDB.db_toefl_package_section.find_one(
            {"fk_package_id": package_pkey, "section_type": code, "is_deleted": False}
        ):
            return {"status": "ERROR", "message": "Tipe tes sudah ada di paket ini"}
        # end if
        title = type_test.get("label") or code
        if type_test.get("description"):
            title = title + " (" + type_test.get("description") + ")"
        # end if
        max_doc = mgdDB.db_toefl_package_section.find_one(
            {"fk_package_id": package_pkey, "is_deleted": False}, sort=[("sort_order", -1)]
        )
        sec = database.new(mgdDB, "db_toefl_package_section")
        sec.put("section_id",       idgen._get_unique_id())
        sec.put("fk_package_id",    package_pkey)
        sec.put("title",            title)
        sec.put("section_type",     code)
        sec.put("duration_minutes", int(duration_minutes or 0))
        sec.put("sort_order",       (max_doc.get("sort_order", 0) + 1) if max_doc else 1)
        sec.put("question_count",   0)
        sec.insert()
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal menambah seksi"}
    # end try
# end def


def update_section(section_pkey, duration_minutes=0):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_toefl_package_section.update_one(
            {"pkey": section_pkey, "is_deleted": False},
            {"$set": {"duration_minutes": int(duration_minutes or 0)}}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def delete_section(package_pkey, section_pkey):
    """Hapus seksi dari paket; soal tetap ada di Bank Soal."""
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_toefl_package_section.update_one(
            {"pkey": section_pkey, "fk_package_id": package_pkey}, {"$set": {"is_deleted": True}}
        )
        mgdDB.db_toefl_section_item.update_many(
            {"fk_package_section_id": section_pkey}, {"$set": {"is_deleted": True}}
        )
        mgdDB.db_toefl_package_part.update_many(
            {"fk_package_section_id": section_pkey}, {"$set": {"is_deleted": True}}
        )
        recount_package(mgdDB, package_pkey)
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def get_part_by_id(part_pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        part  = mgdDB.db_toefl_package_part.find_one({"pkey": part_pkey, "is_deleted": False})
        return {"status": "OK", "data": part}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": None}
    # end try
# end def


def add_part(package_pkey, section_pkey, name, after_pkey=""):
    try:
        name = (name or "").strip()
        if not name:
            return {"status": "ERROR", "message": "Nama bagian wajib diisi"}
        # end if
        mgdDB = database.get_db_conn(config.mainDB)
        order = 0
        if after_pkey:
            after = mgdDB.db_toefl_package_part.find_one(
                {"pkey": after_pkey, "fk_package_section_id": section_pkey, "is_deleted": False}
            )
            if after:
                order = (after.get("sort_order", 0) or 0) + 0.5
            # end if
        # end if
        if not order:
            max_doc = mgdDB.db_toefl_package_part.find_one(
                {"fk_package_section_id": section_pkey, "is_deleted": False}, sort=[("sort_order", -1)]
            )
            order = (max_doc.get("sort_order", 0) + 1) if max_doc else 1
        # end if
        rec = database.new(mgdDB, "db_toefl_package_part")
        rec.put("fk_package_id",         package_pkey)
        rec.put("fk_package_section_id", section_pkey)
        rec.put("name",                  name)
        rec.put("sort_order",            order)
        rec.insert()
        part_pkey = rec._mongo_record.get("pkey", "")
        # rapikan urutan agar selalu 1..n
        parts = list(
            mgdDB.db_toefl_package_part.find(
                {"fk_package_section_id": section_pkey, "is_deleted": False}
            ).sort("sort_order", 1)
        )
        for idx, part in enumerate(parts, start=1):
            mgdDB.db_toefl_package_part.update_one(
                {"pkey": part.get("pkey")}, {"$set": {"sort_order": idx}}
            )
        # end for
        return {"status": "OK", "part_pkey": part_pkey}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal menambah bagian"}
    # end try
# end def


def create_part_from_passages(package_pkey, section_pkey, name, passage_pkeys):
    """Buat sub-bagian baru lalu pindahkan soal-soal terpilih (biasanya dari
    'Tanpa sub-bagian') ke dalamnya."""
    try:
        name = (name or "").strip()
        if not name:
            return {"status": "ERROR", "message": "Nama sub-bagian wajib diisi"}
        # end if
        created = add_part(package_pkey, section_pkey, name)
        if created.get("status") != "OK" or not created.get("part_pkey"):
            return {"status": "ERROR", "message": "Gagal membuat sub-bagian"}
        # end if
        part_pkey = created["part_pkey"]
        moved = 0
        for passage_pkey in passage_pkeys or []:
            result = attach_passage_to_section(
                section_pkey, passage_pkey, package_pkey, part_pkey=part_pkey
            )
            if result.get("status") == "OK":
                moved += 1
            # end if
        # end for
        return {"status": "OK", "part_pkey": part_pkey, "moved": moved}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal membuat sub-bagian"}
    # end try
# end def


def reorder_parts(section_pkey, part_pkeys):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        for idx, part_pkey in enumerate(part_pkeys or [], start=1):
            mgdDB.db_toefl_package_part.update_one(
                {"pkey": part_pkey, "fk_package_section_id": section_pkey, "is_deleted": False},
                {"$set": {"sort_order": idx}}
            )
        # end for
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def reorder_section_items(section_pkey, passage_pkeys):
    """Urutan global se-items dalam satu seksi; fk_part_id tidak berubah."""
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        for idx, passage_pkey in enumerate(passage_pkeys or [], start=1):
            mgdDB.db_toefl_section_item.update_many(
                {"fk_package_section_id": section_pkey, "fk_passage_id": passage_pkey, "is_deleted": False},
                {"$set": {"sort_order": idx}}
            )
        # end for
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def reorder_sections(package_pkey, section_pkeys):
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        for idx, section_pkey in enumerate(section_pkeys or [], start=1):
            mgdDB.db_toefl_package_section.update_one(
                {"pkey": section_pkey, "fk_package_id": package_pkey, "is_deleted": False},
                {"$set": {"sort_order": idx}}
            )
        # end for
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def rename_part(part_pkey, name):
    try:
        name = (name or "").strip()
        if not name:
            return {"status": "ERROR", "message": "Nama bagian wajib diisi"}
        # end if
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_toefl_package_part.update_one(
            {"pkey": part_pkey, "is_deleted": False}, {"$set": {"name": name}}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def delete_part(part_pkey):
    """Hapus bagian; soal di dalamnya tetap di seksi sebagai 'tanpa bagian'."""
    try:
        mgdDB = database.get_db_conn(config.mainDB)
        mgdDB.db_toefl_package_part.update_one({"pkey": part_pkey}, {"$set": {"is_deleted": True}})
        mgdDB.db_toefl_section_item.update_many(
            {"fk_part_id": part_pkey, "is_deleted": False}, {"$set": {"fk_part_id": ""}}
        )
        return {"status": "OK"}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def get_passage_usage_map(passage_pkeys, mgdDB=None):
    usage = {pk: [] for pk in (passage_pkeys or []) if pk}
    if not usage:
        return usage
    # end if
    if mgdDB is None:
        mgdDB = database.get_db_conn(config.mainDB)
    # end if
    pkeys = list(usage.keys())
    seen_pair = set()

    def _add(passage_pk, package, section=None):
        if not passage_pk or not package or passage_pk not in usage:
            return
        # end if
        pkg_pk = package.get("pkey")
        sec_pk = (section or {}).get("pkey", "")
        pair = (passage_pk, pkg_pk, sec_pk)
        if not pkg_pk or pair in seen_pair:
            return
        # end if
        seen_pair.add(pair)
        usage[passage_pk].append({
            "pkey"          : pkg_pk,
            "title"         : package.get("title") or "(Tanpa judul)",
            "section_pkey"  : sec_pk,
            "section_title" : (section or {}).get("title") or "",
            "section_type"  : (section or {}).get("section_type") or "",
        })
    # end def

    items = list(mgdDB.db_toefl_section_item.find({
        "fk_passage_id": {"$in": pkeys},
        "is_deleted": False,
    }))
    passages = list(mgdDB.db_toefl_passage.find(
        {"pkey": {"$in": pkeys}, "is_deleted": False},
        {"pkey": 1, "fk_package_section_id": 1}
    ))
    section_ids = set()
    for item in items:
        if item.get("fk_package_section_id"):
            section_ids.add(item.get("fk_package_section_id"))
        # end if
    # end for
    for passage in passages:
        if passage.get("fk_package_section_id"):
            section_ids.add(passage.get("fk_package_section_id"))
        # end if
    # end for
    if not section_ids:
        return usage
    # end if
    sections = list(mgdDB.db_toefl_package_section.find({
        "pkey": {"$in": list(section_ids)},
        "is_deleted": False,
    }))
    section_by_id = {s.get("pkey"): s for s in sections}
    pkg_ids = [s.get("fk_package_id") for s in sections if s.get("fk_package_id")]
    packages = []
    if pkg_ids:
        packages = list(mgdDB.db_toefl_package.find({
            "pkey": {"$in": pkg_ids},
            "is_deleted": False,
        }))
    # end if
    pkg_by_id = {p.get("pkey"): p for p in packages}

    for item in items:
        sec = section_by_id.get(item.get("fk_package_section_id"))
        if not sec:
            continue
        # end if
        _add(item.get("fk_passage_id"), pkg_by_id.get(sec.get("fk_package_id")), sec)
    # end for
    for passage in passages:
        sec = section_by_id.get(passage.get("fk_package_section_id"))
        if not sec:
            continue
        # end if
        _add(passage.get("pkey"), pkg_by_id.get(sec.get("fk_package_id")), sec)
    # end for
    return usage
# end def
