import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import os
import uuid
import traceback
from flask import Blueprint, request, redirect, g, jsonify, current_app

from middleware import middleware_privilege
from view.question_bank import view_question_bank
import sanitize
from sanitize       import strip_objectid, strip_objectid_list
from toefl_scoring  import get_section_config

question_bank_blueprint = Blueprint("question_bank_blueprint", __name__)


def _resolve_section_keys(section_id, passage_sub_type=""):
    """Return (section_key, sub_type_key) from a package-section pkey."""
    try:
        from exam_package import exam_package_proc
        sec = exam_package_proc.get_section_by_id(section_id).get("data") or {}
        section_key = sec.get("section_type", "").lower().strip()
        # sub_type_key comes from the passage itself (passed in), not the section
        sub_type_key = (passage_sub_type or "").lower().strip()
        return section_key, sub_type_key
    except Exception:
        return "", (passage_sub_type or "").lower().strip()
    # end try
# end def


def _type_test_options():
    options = []
    try:
        from app_settings import app_settings_proc
        for row in app_settings_proc.get_type_tests().get("data", []):
            key = (row.get("code") or "").lower().strip()
            if not key:
                continue
            # end if
            label = row.get("label") or key.title()
            if row.get("description"):
                label = label + " (" + row.get("description") + ")"
            # end if
            options.append({"key": key, "label": label})
        # end for
    except Exception:
        pass
    # end try
    return options
# end def


def _bank_section_options(current=""):
    """
    Ambil daftar tipe tes dari Pengaturan > Tipe Tes (db_test_type).
    Fallback ke seksi cetakan level jika tipe tes belum diisi.
    """
    options = _type_test_options()
    seen = set(opt["key"] for opt in options)
    try:
        from app_settings import app_settings_proc
        bundle = [] if options else app_settings_proc.get_settings_bundle().get("data", [])
        for item in bundle:
            for sec in item.get("sections") or []:
                key = (sec.get("section_type") or "").lower().strip()
                if not key or key in seen:
                    continue
                # end if
                seen.add(key)
                options.append({
                    "key"   : key,
                    "label" : sec.get("title") or key.title(),
                })
            # end for
        # end for
    except Exception:
        pass
    # end try
    if not options:
        defaults = [
            ("hoeren", "Hören (Mendengarkan)"),
            ("lesen", "Lesen (Membaca)"),
            ("schreiben", "Schreiben (Menulis)"),
            ("sprechen", "Sprechen (Berbicara)"),
            ("struktur", "Wissenschaftssprachliche Strukturen"),
        ]
        for k, lbl in defaults:
            seen.add(k)
            options.append({"key": k, "label": lbl})
        # end for
    # end if
    # Jika current key belum ada, tambahkan supaya select tetap menampilkan nilai lama
    current = (current or "").lower().strip()
    if current and current not in seen:
        options.append({"key": current, "label": current.title()})
    # end if
    return options
# end def


def _all_valid_section_keys():
    """Return set of lowercase section_type keys yang valid dari DB."""
    keys = set(opt["key"] for opt in _type_test_options())
    try:
        from app_settings import app_settings_proc
        for item in app_settings_proc.get_settings_bundle().get("data", []):
            for sec in item.get("sections") or []:
                key = (sec.get("section_type") or "").lower().strip()
                if key:
                    keys.add(key)
                # end if
            # end for
        # end for
    except Exception:
        pass
    # end try
    return keys
# end def


def _normalize_bank_item(item):
    sk = (item.get("section_key") or "").lower().strip()
    valid = _all_valid_section_keys()
    # Jika valid keys tersedia, hanya terima key yang ada; kalau DB kosong, terima semua
    if valid and sk not in valid:
        sk = ""
    # end if
    item["section_key"]   = sk
    item["question_mode"] = (item.get("question_mode") or "grouped").lower().strip()
    return item
# end def


def _filter_bank_passages(passages, filter_section="", filter_mode=""):
    result = []
    for item in passages:
        _normalize_bank_item(item)
        if filter_section and item.get("section_key") != filter_section:
            continue
        # end if
        if filter_mode in ("single", "grouped", "sprechen") and item.get("question_mode") != filter_mode:
            continue
        # end if
        result.append(item)
    # end for
    return result
# end def


def _bank_list_redirect(section="", mode="", page="", per_page=""):
    parts = []
    if section:
        parts.append("section=" + section)
    # end if
    if mode:
        parts.append("mode=" + mode)
    # end if
    if page and str(page) not in ("", "1"):
        parts.append("page=" + str(page))
    # end if
    if per_page and str(per_page) not in ("", "10"):
        parts.append("per_page=" + str(per_page))
    # end if
    url = "/expert/question-bank"
    if parts:
        url += "?" + "&".join(parts)
    # end if
    return redirect(url)
# end def


def _plain_text(html_value):
    from html.parser import HTMLParser
    class _P(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text = []
        def handle_data(self, d):
            self.text.append(d)
        # end def
    # end class
    parser = _P()
    parser.feed(html_value or "")
    return "".join(parser.text).strip()
# end def


def _load_packages_and_sections():
    from exam_package import exam_package_proc
    packages = strip_objectid_list(exam_package_proc.get_all_packages().get("data", []))
    sections_map = {}
    all_sections = []
    for pkg in packages:
        secs = strip_objectid_list(
            exam_package_proc.get_sections_by_package(pkg["pkey"]).get("data", [])
        )
        sections_map[pkg["pkey"]] = secs
        all_sections.extend(secs)
    # end for
    return packages, sections_map, all_sections
# end def


def _match_package(packages, value):
    if not value:
        return packages[0] if packages else None
    # end if
    v = str(value).strip().lower()
    for pkg in packages:
        if (pkg.get("pkey") or "").lower() == v:
            return pkg
        # end if
        if (pkg.get("package_id") or "").lower() == v:
            return pkg
        # end if
        if (pkg.get("title") or "").lower() == v:
            return pkg
        # end if
        if (pkg.get("test_type") or "").lower() == v:
            return pkg
        # end if
    # end for
    return None
# end def


def _match_section(sections, value):
    if not value:
        return None
    # end if
    v = str(value).strip().lower()
    for sec in sections:
        if (sec.get("pkey") or "").lower() == v:
            return sec
        # end if
        if (sec.get("section_id") or "").lower() == v:
            return sec
        # end if
        if (sec.get("title") or "").lower() == v:
            return sec
        # end if
        if (sec.get("section_type") or "").lower() == v:
            return sec
        # end if
    # end for
    return None
# end def


def _nested_questions(item):
    nested = item.get("questions") if isinstance(item, dict) else None
    if not isinstance(nested, list):
        return []
    # end if
    return [q for q in nested if isinstance(q, dict)]
# end def


def _is_grouped_passage_item(item):
    nested = _nested_questions(item)
    if not nested:
        return False
    # end if
    if item.get("content_text") or item.get("title"):
        return True
    # end if
    mode = str(item.get("question_mode") or item.get("mode") or "").lower().strip()
    if mode == "grouped":
        return True
    # end if
    if item.get("package") or item.get("section") or item.get("section_key"):
        return True
    # end if
    return False
# end def


def _parse_import_payload(raw, forced_mode=""):
    import json as _json
    text = (raw or "").strip()
    if not text:
        return []
    # end if
    data = _json.loads(text)
    if isinstance(data, list):
        return data
    # end if
    if isinstance(data, dict):
        if forced_mode or _is_grouped_passage_item(data):
            return [data]
        # end if
        nested = _nested_questions(data)
        if nested and not data.get("question_text"):
            return nested
        # end if
        return [data]
    # end if
    return []
# end def


def question_bank_proc_answer_type(value):
    from question_bank import question_bank_proc
    return question_bank_proc.normalize_answer_type(value)
# end def


def _match_test_type(value, options):
    """Cocokkan 'lesen' / 'LESEN' / 'Hören' / 'Hören (Mendengarkan)' ke key tipe tes."""
    v = str(value or "").lower().strip()
    if not v:
        return ""
    # end if
    for src, dst in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        v = v.replace(src, dst)
    # end for
    for opt in options:
        label = (opt.get("label") or "").lower()
        for src, dst in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
            label = label.replace(src, dst)
        # end for
        if v == opt.get("key") or v == label or label.startswith(v + " ("):
            return opt.get("key")
        # end if
    # end for
    return ""
# end def


def _option_images(params, prefix=""):
    images = {}
    for key in ("a", "b", "c", "d"):
        url = str(params.get(prefix + "option_" + key + "_image", "") or "").strip()
        if not url.startswith(("/static/", "http://", "https://")):
            url = ""
        # end if
        images[key] = url
    # end for
    return images
# end def


def _create_one_question(proc, passage_pkey, section_id, expert_id, item, section_key, sub_type_key):
    q_text = sanitize.allow_html(item.get("question_text", "") or "")
    answer_text = str(item.get("answer_text", "") or "").strip()
    if (not q_text.strip() or q_text.strip() in ("<p><br></p>", "<p></p>")) and not answer_text:
        return False
    # end if
    result = proc.create_question(
        passage_pkey   = passage_pkey,
        section_id     = section_id,
        expert_id      = expert_id,
        question_text  = q_text,
        option_a       = item.get("option_a", "") or "",
        option_b       = item.get("option_b", "") or "",
        option_c       = item.get("option_c", "") or "",
        option_d       = item.get("option_d", "") or "",
        correct_answer = (item.get("correct_answer", "A") or "A"),
        explanation    = sanitize.allow_html(item.get("explanation", "") or ""),
        section_key    = section_key,
        sub_type_key   = sub_type_key,
        option_images  = _option_images(sanitize.clean_html_dic(item)),
        answer_text    = answer_text,
        is_premium     = bool(item.get("is_premium")),
    )
    if result.get("status") != "OK":
        return False
    # end if
    return result.get("question_pkey", "")
# end def


@question_bank_blueprint.route("/expert/question-bank", methods=["GET"])
@middleware_privilege(roles=["super_admin", "expert"])
def list_passages():
    try:
        from question_bank import question_bank_proc
        from exam_package import exam_package_proc
        filter_section = (request.args.get("section") or "").lower().strip()
        filter_mode    = (request.args.get("mode") or "").lower().strip()
        listed = question_bank_proc.list_bank_passages(
            expert_id     = g.current_user["user_id"],
            section_key   = filter_section,
            question_mode = filter_mode,
            page          = request.args.get("page", 1),
            per_page      = request.args.get("per_page", 10),
        )
        packages, sections_map, _ = _load_packages_and_sections()
        passages = strip_objectid_list(listed.get("data", []))
        for item in passages:
            _normalize_bank_item(item)
        # end for

        # penanda premium: tugas Sprechen (passage) atau ada soal premium di dalamnya
        try:
            import database
            import config
            _mgd = database.get_db_conn(config.mainDB)
            prem_q = {}
            for row in _mgd.db_toefl_question.aggregate([
                {"$match": {"is_deleted": False, "is_premium": True}},
                {"$group": {"_id": "$fk_passage_id", "n": {"$sum": 1}}},
            ]):
                prem_q[row["_id"]] = row["n"]
            # end for
            for item in passages:
                item["any_premium"] = bool(item.get("is_premium")) or prem_q.get(item.get("pkey", ""), 0) > 0
            # end for
        except Exception:
            print(traceback.format_exc())
        # end try
        usage = exam_package_proc.get_passage_usage_map([p.get("pkey") for p in passages])
        for item in passages:
            pkgs = usage.get(item.get("pkey"), [])
            item["used_in_packages"] = pkgs
            item["used_in_count"] = len(pkgs)
        # end for
        pagination = listed.get("pagination") or {}
        section_opts = _bank_section_options()
        section_labels = {opt["key"]: opt["label"] for opt in section_opts}
        section_labels[""] = "Belum dikelompokkan"
        group_keys = [opt["key"] for opt in section_opts]
        if "" not in group_keys:
            group_keys.append("")
        # end if
        from app_settings import app_settings_proc
        dump_counts = {
            code.lower(): counts
            for code, counts in app_settings_proc.count_type_test_dumps().items()
        }
        return view_question_bank.html_passages_list(
            passages           = passages,
            packages           = packages,
            user               = g.current_user,
            sections_map       = sections_map,
            filter_section     = filter_section,
            filter_mode        = filter_mode,
            filter_total       = pagination.get("total", 0),
            pagination         = pagination,
            per_page_options   = question_bank_proc.BANK_PER_PAGE_OPTIONS,
            bank_sections      = section_opts,
            section_labels     = section_labels,
            group_keys         = group_keys,
            dump_counts        = dump_counts,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@question_bank_blueprint.route("/expert/question-bank/new", methods=["GET"])
@middleware_privilege(roles=["super_admin", "expert"])
def new_passage_page():
    try:
        return view_question_bank.html_passage_new(
            type_tests = _bank_section_options(),
            user       = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@question_bank_blueprint.route("/expert/question-bank/dump-templates", methods=["GET"])
@middleware_privilege(roles=["super_admin", "expert"])
def dump_templates():
    try:
        import json as _json
        from app_settings import app_settings_proc
        params = sanitize.clean_html_dic(request.args.to_dict())
        if params.get("mode", "") not in app_settings_proc.DUMP_JENIS:
            return jsonify({"status": "ERROR", "message": "Jenis tidak valid"}), 400
        # end if
        _jenis, mode, answer_type, cloze_mode = app_settings_proc.parse_dump_jenis(params.get("mode"))
        rows = app_settings_proc.get_type_test_dumps(
            test_type_code = params.get("test_type", ""),
            question_mode  = mode,
            limit          = sanitize.clean_int(params.get("limit"), 0),
            answer_type    = answer_type,
            cloze_mode     = cloze_mode,
        ).get("data", [])
        items = []
        for row in rows:
            try:
                items.append(_json.loads(row.get("dump_json") or "{}"))
            except Exception:
                continue
            # end try
        # end for
        return jsonify({"status": "OK", "items": items})
    except Exception:
        print(traceback.format_exc())
        return jsonify({"status": "ERROR", "message": "Gagal memuat dump"}), 500
    # end try
# end def


@question_bank_blueprint.route("/expert/question-bank/import-json", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def import_questions_json():
    try:
        from question_bank import question_bank_proc
        payload = request.get_json(silent=True) or {}
        raw     = payload.get("json", "") if isinstance(payload, dict) else ""
        if not raw and request.form.get("json"):
            raw = request.form.get("json", "")
        # end if

        from app_settings import app_settings_proc
        forced_jenis = str(payload.get("question_mode") or "").lower().strip() if isinstance(payload, dict) else ""
        forced_mode, forced_answer_type = "", ""
        if forced_jenis in app_settings_proc.DUMP_JENIS:
            _jenis, forced_mode, forced_answer_type, _forced_cloze_mode = app_settings_proc.parse_dump_jenis(forced_jenis)
        # end if
        try:
            items = _parse_import_payload(raw, forced_mode)
        except Exception as parse_err:
            return jsonify({
                "status" : "ERROR",
                "message": "JSON tidak valid: " + str(parse_err),
            }), 400
        # end try

        if not items:
            return jsonify({"status": "ERROR", "message": "Tidak ada soal di JSON"}), 400
        # end if

        packages, sections_map, all_sections = _load_packages_and_sections()
        test_type_opts = _bank_section_options()
        forced_type    = _match_test_type(
            payload.get("test_type") if isinstance(payload, dict) else "", test_type_opts
        )

        expert_id = g.current_user["user_id"]
        created_passages  = 0
        created_questions = 0
        passage_pkeys     = []
        question_pkeys    = []
        errors = []
        target_raw = payload.get("passage_pkey") if isinstance(payload, dict) else ""
        target_passage = sanitize.clean_html_dic({"p": target_raw or ""}).get("p", "")

        for idx, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                errors.append("Item %s bukan objek soal" % idx)
                continue
            # end if

            nested = _nested_questions(item)
            q_mode = str(item.get("question_mode") or item.get("mode") or "single").lower().strip()
            if forced_mode == "single" and nested:
                errors.append("Item %s: berisi questions[], tidak cocok dengan jenis Mandiri" % idx)
                continue
            elif forced_mode == "grouped" and not nested:
                errors.append("Item %s: Kelompok Soal wajib punya questions[]" % idx)
                continue
            elif forced_mode:
                q_mode = forced_mode
            elif nested or q_mode == "grouped":
                q_mode = "grouped"
            elif q_mode not in ("single", "grouped"):
                q_mode = "single"
            # end if

            pkg = _match_package(
                packages,
                item.get("package") or item.get("package_id") or item.get("package_title")
            )
            sec = None
            if pkg:
                pkg_sections = sections_map.get(pkg["pkey"], []) or all_sections
                sec = _match_section(
                    pkg_sections,
                    item.get("section") or item.get("section_id") or item.get("section_type") or item.get("seksi")
                )
            elif item.get("section") or item.get("section_type") or item.get("seksi"):
                sec = _match_section(
                    all_sections,
                    item.get("section") or item.get("section_id") or item.get("section_type") or item.get("seksi")
                )
            # end if

            section_id = (sec or {}).get("pkey", "")
            sub_type_raw = item.get("passage_sub_type") or item.get("sub_type") or ""
            test_type_key = forced_type or _match_test_type(
                item.get("test_type") or item.get("section_key") or item.get("section") or item.get("section_type") or "",
                test_type_opts,
            )
            if test_type_key:
                section_key, sub_type_key = test_type_key, (sub_type_raw or "").lower().strip()
            elif section_id:
                section_key, sub_type_key = _resolve_section_keys(section_id, sub_type_raw)
            else:
                section_key, sub_type_key = "", (sub_type_raw or "").lower().strip()
            # end if

            q_text = sanitize.allow_html(item.get("question_text", "") or "")
            title  = (item.get("title") or "").strip()
            if not title:
                plain = _plain_text(q_text)
                if not plain and nested:
                    plain = _plain_text(nested[0].get("question_text", ""))
                # end if
                if not plain and forced_mode == "sprechen":
                    plain = _plain_text(item.get("instruction", ""))
                # end if
                title = (plain[:60] if plain else "Soal Impor %s" % idx)
            # end if

            content_text = sanitize.allow_html(item.get("content_text", "") or "")
            if forced_mode == "sprechen":
                # dump Sprechen: question_text = situasi, content_text biasanya kosong
                content_text = content_text or sanitize.allow_html(item.get("question_text", "") or "")
            # end if
            audio_url    = item.get("audio_url") or ""
            content_type = "audio" if audio_url else "text"
            passage_pkey = target_passage if (target_passage and idx == 1) else ""

            if passage_pkey:
                existing = question_bank_proc.get_passage_by_id(passage_pkey).get("data")
                if not existing:
                    errors.append("Item %s: passage tidak ditemukan" % idx)
                    continue
                # end if
                if content_text or title:
                    question_bank_proc.update_passage(
                        passage_pkey     = passage_pkey,
                        title            = title or existing.get("title", ""),
                        content_type     = content_type or existing.get("content_type", "text"),
                        content_text     = content_text or existing.get("content_text", ""),
                        audio_url        = audio_url or existing.get("audio_url", ""),
                        question_mode    = "grouped" if nested else (existing.get("question_mode") or q_mode),
                        passage_sub_type = sub_type_raw or existing.get("passage_sub_type", ""),
                        section_key      = section_key or existing.get("section_key", ""),
                        sub_type_key     = sub_type_key or existing.get("sub_type_key", ""),
                        cloze_answer_mode= item.get("cloze_answer_mode") or None,
                    )
                # end if
                if not section_id:
                    section_id = existing.get("fk_package_section_id", "")
                # end if
                if not section_key:
                    section_key = existing.get("section_key", "")
                # end if
            else:
                result = question_bank_proc.create_passage(
                    title            = title,
                    content_type     = content_type,
                    content_text     = content_text,
                    audio_url        = audio_url,
                    section_id       = section_id,
                    expert_id        = expert_id,
                    question_mode    = q_mode,
                    passage_sub_type = sub_type_raw,
                    section_key      = section_key,
                    sub_type_key     = sub_type_key,
                    answer_type      = forced_answer_type or question_bank_proc.normalize_answer_type(item.get("answer_type")),
                    cloze_answer_mode= item.get("cloze_answer_mode", ""),
                    instruction      = sanitize.allow_html(item.get("instruction", "") or "") if forced_mode == "sprechen" else "",
                    sample_answer    = sanitize.allow_html(item.get("sample_answer", "") or "") if forced_mode == "sprechen" else "",
                    image_url        = (item.get("image") or item.get("image_url") or "") if forced_mode == "sprechen" else "",
                    prep_seconds     = item.get("prep_seconds", 0) if forced_mode == "sprechen" else 0,
                    speak_seconds    = item.get("speak_seconds", 0) if forced_mode == "sprechen" else 0,
                    is_premium       = bool(item.get("is_premium")) if forced_mode == "sprechen" else False,
                )
                if result.get("status") != "OK":
                    errors.append("Item %s: gagal membuat passage" % idx)
                    continue
                # end if
                created_passages += 1
                passage_pkey = result["passage_pkey"]
            # end if

            if passage_pkey and passage_pkey not in passage_pkeys:
                passage_pkeys.append(passage_pkey)
            # end if

            if q_mode == "sprechen":
                # tugas bicara: tanpa butir soal pilihan ganda
                continue
            # end if

            if nested:
                is_cloze = (forced_answer_type or question_bank_proc.normalize_answer_type(item.get("answer_type"))) == "cloze"
                for gap_idx, q_item in enumerate(nested, start=1):
                    if is_cloze and not _plain_text(q_item.get("question_text", "")):
                        q_item = dict(q_item, question_text=question_bank_proc.cloze_question_text(q_item.get("gap_no") or gap_idx))
                    # end if
                    new_q_pkey = _create_one_question(
                        question_bank_proc, passage_pkey, section_id, expert_id,
                        q_item, section_key, sub_type_key
                    )
                    if new_q_pkey:
                        created_questions += 1
                        question_pkeys.append(new_q_pkey)
                    # end if
                # end for
            else:
                new_q_pkey = _create_one_question(
                    question_bank_proc, passage_pkey, section_id, expert_id,
                    item, section_key, sub_type_key
                )
                if new_q_pkey:
                    created_questions += 1
                    question_pkeys.append(new_q_pkey)
                # end if
            # end if
        # end for

        return jsonify({
            "status"            : "OK",
            "created_passages"  : created_passages,
            "created_questions" : created_questions,
            "passage_pkey"      : passage_pkeys[0] if passage_pkeys else "",
            "passage_pkeys"     : passage_pkeys,
            "question_pkeys"    : question_pkeys,
            "errors"            : errors,
        })
    except Exception:
        print(traceback.format_exc())
        return jsonify({"status": "ERROR", "message": "Terjadi kesalahan saat impor"}), 500
    # end try
# end def


@question_bank_blueprint.route("/expert/question-bank/create", methods=["GET"])
@middleware_privilege(roles=["super_admin", "expert"])
def create_passage_page():
    try:
        from exam_package import exam_package_proc
        packages_result = exam_package_proc.get_all_packages()
        packages_clean  = strip_objectid_list(packages_result.get("data", []))
        sections_data   = {}
        for pkg in packages_clean:
            secs = exam_package_proc.get_sections_by_package(pkg["pkey"])
            sections_data[pkg["pkey"]] = strip_objectid_list(secs.get("data", []))
        # end for

        # Preset context from package_builder deep-link
        preset_package_pkey = request.args.get("package_pkey", "")
        preset_section_pkey = request.args.get("section_pkey", "")
        requested_mode      = (request.args.get("mode") or "").lower().strip()
        if question_bank_proc_answer_type(request.args.get("answer_type")) == "cloze":
            requested_mode = "grouped"
        # end if
        return_to           = request.args.get("return_to", "")
        preset_section      = None
        section_config      = None
        if preset_section_pkey:
            sec_result     = exam_package_proc.get_section_by_id(preset_section_pkey)
            preset_section = strip_objectid(sec_result.get("data"))
            if preset_section:
                section_config = get_section_config(preset_section.get("section_type", ""))
            # end if
        # end if
        if requested_mode != "sprechen":
            if requested_mode not in ("single", "grouped"):
                cfg_mode = (section_config or {}).get("default_passage_mode", "")
                if cfg_mode in ("single", "grouped"):
                    requested_mode = cfg_mode
                # end if
            # end if
        # end if
        requested_answer_type = question_bank_proc_answer_type(request.args.get("answer_type"))
        if requested_mode == "sprechen":
            requested_answer_type = "speak"
        # end if

        current_key = sanitize.clean_str(request.args.get("test_type") or "").lower().strip()
        if not current_key and preset_section:
            current_key = (preset_section.get("section_type") or "").lower().strip()
        # end if
        return view_question_bank.html_passage_editor(
            passage             = None,
            questions           = [],
            packages            = packages_clean,
            sections_map        = sections_data,
            preset_package_pkey = preset_package_pkey,
            preset_section      = preset_section,
            section_config      = section_config,
            user                = g.current_user,
            requested_mode      = requested_mode,
            return_to           = return_to,
            used_in_packages    = [],
            bank_section_options= _bank_section_options(current_key),
            current_section_key = current_key,
            requested_answer_type = requested_answer_type,
            cloze_answer_mode   = (request.args.get("cloze_mode") or "").lower().strip(),
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@question_bank_blueprint.route("/expert/question-bank/create", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def create_passage_post():
    try:
        params       = sanitize.clean_html_dic(request.form.to_dict())
        content_text = sanitize.allow_html(request.form.get("content_text", ""))
        if params.get("question_mode") == "sprechen":
            content_text = sanitize.allow_html(request.form.get("spk_situation", ""))
        # end if

        q_mode       = params.get("question_mode", "grouped")
        if question_bank_proc_answer_type(params.get("answer_type")) == "cloze":
            q_mode = "grouped"
        # end if
        sq_q_text    = sanitize.allow_html(request.form.get("sq_question_text", ""))
        sq_exp       = sanitize.allow_html(request.form.get("sq_explanation", ""))

        # Auto-generate title for single mode from question text
        title = params.get("title", "").strip()
        if q_mode == "single" and not title:
            from html.parser import HTMLParser
            class _P(HTMLParser):
                def __init__(self): super().__init__(); self.text = []
                def handle_data(self, d): self.text.append(d)
            p = _P(); p.feed(sq_q_text); plain = "".join(p.text).strip()
            title = plain[:60] if plain else "Soal Mandiri"
        # end if
        if q_mode == "sprechen" and not title:
            title = (params.get("spk_instruction", "") or "Tugas Sprechen").strip()[:60]
        # end if

        section_id   = params.get("section_id", "")
        sub_type_raw = params.get("passage_sub_type", "")
        section_key  = (params.get("section_key") or "").lower().strip()
        sub_type_key = (sub_type_raw or "").lower().strip()
        if not section_key and section_id:
            section_key, sub_type_key = _resolve_section_keys(section_id, sub_type_raw)
        # end if

        from question_bank import question_bank_proc
        result = question_bank_proc.create_passage(
            title              = title,
            content_type       = "audio" if params.get("audio_url") else "text",
            content_text       = content_text,
            audio_url          = params.get("audio_url", ""),
            section_id         = section_id,
            expert_id          = g.current_user["user_id"],
            question_mode      = q_mode,
            passage_sub_type   = sub_type_raw,
            section_key        = section_key,
            sub_type_key       = sub_type_key,
            answer_type        = question_bank_proc.normalize_answer_type(params.get("answer_type")),
            cloze_answer_mode  = params.get("cloze_answer_mode", ""),
            instruction        = sanitize.allow_html(request.form.get("spk_instruction", "")),
            sample_answer      = sanitize.allow_html(request.form.get("spk_sample_answer", "")),
            image_url          = params.get("spk_image_url", ""),
            prep_seconds       = params.get("spk_prep_seconds", 0),
            speak_seconds      = params.get("spk_speak_seconds", 0),
            is_premium         = params.get("is_premium") == "1",
        )

        if result["status"] != "OK":
            return redirect("/expert/question-bank")
        # end if

        passage_pkey = result["passage_pkey"]

        # Sprechen: tugas bicara berdiri sendiri — tanpa butir soal pilihan ganda
        if q_mode == "sprechen":
            return_to = params.get("return_to", "")
            if return_to.startswith("/expert/"):
                return redirect(return_to)
            # end if
            return redirect("/expert/question-bank/" + passage_pkey)
        # end if

        # Single mode: also create the question immediately
        if q_mode == "single" and sq_q_text:
            question_bank_proc.create_question(
                passage_pkey   = passage_pkey,
                section_id     = section_id,
                expert_id      = g.current_user["user_id"],
                question_text  = sq_q_text,
                option_a       = params.get("sq_option_a", ""),
                option_b       = params.get("sq_option_b", ""),
                option_c       = params.get("sq_option_c", ""),
                option_d       = params.get("sq_option_d", ""),
                correct_answer = params.get("sq_correct_answer", "A"),
                explanation    = sq_exp,
                section_key    = section_key,
                sub_type_key   = sub_type_key,
                option_images  = _option_images(params, "sq_"),
                is_premium     = params.get("sq_is_premium") == "1",
            )
            return_to = params.get("return_to", "")
            if return_to.startswith("/expert/"):
                return redirect(return_to)
            # end if
            return redirect("/expert/question-bank")
        # end if

        return redirect("/expert/question-bank/" + passage_pkey)
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@question_bank_blueprint.route("/expert/question-bank/<passage_pkey>", methods=["GET"])
@middleware_privilege(roles=["super_admin", "expert"])
def edit_passage_page(passage_pkey):
    try:
        from question_bank import question_bank_proc
        from exam_package  import exam_package_proc

        passage_result   = question_bank_proc.get_passage_by_id(passage_pkey)
        questions_result = question_bank_proc.get_questions_by_passage(passage_pkey)
        packages_result  = exam_package_proc.get_all_packages()
        packages_clean   = strip_objectid_list(packages_result.get("data", []))
        sections_data    = {}
        for pkg in packages_clean:
            secs = exam_package_proc.get_sections_by_package(pkg["pkey"])
            sections_data[pkg["pkey"]] = strip_objectid_list(secs.get("data", []))
        # end for

        passage_clean  = strip_objectid(passage_result.get("data"))
        sec_type       = passage_clean.get("fk_package_section_id", "") if passage_clean else ""
        # Try to get section type from the section record for config lookup
        sec_obj        = None
        if sec_type:
            sec_obj = strip_objectid(exam_package_proc.get_section_by_id(sec_type).get("data"))
        # end if
        section_config = get_section_config(sec_obj.get("section_type", "")) if sec_obj else None
        questions_clean = strip_objectid_list(questions_result.get("data", []))

        # For single-mode passages, expose first question for inline editing
        first_question = questions_clean[0] if (
            passage_clean and
            passage_clean.get("question_mode") == "single" and
            questions_clean
        ) else None

        used_in = []
        if passage_clean:
            used_in = exam_package_proc.get_passage_usage_map(
                [passage_clean.get("pkey")]
            ).get(passage_clean.get("pkey"), [])
        # end if
        current_key = (passage_clean or {}).get("section_key") or ""
        if not current_key and sec_obj:
            current_key = (sec_obj.get("section_type") or "").lower().strip()
        # end if
        return view_question_bank.html_passage_editor(
            passage             = passage_clean,
            questions           = questions_clean,
            packages            = packages_clean,
            sections_map        = sections_data,
            preset_package_pkey = (sec_obj or {}).get("fk_package_id", ""),
            preset_section      = sec_obj,
            section_config      = section_config,
            first_question      = first_question,
            user                = g.current_user,
            requested_mode      = (passage_clean or {}).get("question_mode", "") or "",
            return_to           = request.args.get("return_to", ""),
            used_in_packages    = strip_objectid_list(used_in),
            bank_section_options= _bank_section_options(current_key),
            current_section_key = current_key.lower().strip(),
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@question_bank_blueprint.route("/expert/question-bank/<passage_pkey>/preview", methods=["GET"])
@middleware_privilege(roles=["super_admin", "expert"])
def preview_passage_page(passage_pkey):
    try:
        import re as _re
        from question_bank import question_bank_proc
        passage_result   = question_bank_proc.get_passage_by_id(passage_pkey)
        questions_result = question_bank_proc.get_questions_by_passage(passage_pkey)
        passage_clean    = strip_objectid(passage_result.get("data"))
        if not passage_clean:
            return redirect("/expert/question-bank")
        # end if

        # Sprechen: pratinjau gaya siswa lengkap dengan perekam suara
        if passage_clean.get("question_mode") == "sprechen":
            return view_question_bank.html_passage_sprechen_preview(
                passage = passage_clean,
                user    = g.current_user,
            )
        # end if

        questions_clean = strip_objectid_list(questions_result.get("data", []))
        # Metadata rumpang untuk pratinjau interaktif Lückentext (isian / dropdown)
        gaps = []
        for q in questions_clean:
            match = _re.search(r"\d+", str(q.get("question_text") or ""))
            gaps.append({
                "pkey"      : q.get("pkey", ""),
                "no"        : match.group(0) if match else "",
                "answer_text": q.get("answer_text") or "",
                "explanation": q.get("explanation") or "",
                "correct"   : q.get("correct_answer") or "",
                "option_a"  : q.get("option_a") or "",
                "option_b"  : q.get("option_b") or "",
                "option_c"  : q.get("option_c") or "",
                "option_d"  : q.get("option_d") or "",
            })
        # end for
        return view_question_bank.html_passage_preview(
            passage   = passage_clean,
            questions = questions_clean,
            gaps      = gaps,
            user      = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@question_bank_blueprint.route("/expert/question-bank/<passage_pkey>/update", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def update_passage_post(passage_pkey):
    try:
        params       = sanitize.clean_html_dic(request.form.to_dict())
        content_text = sanitize.allow_html(request.form.get("content_text", ""))
        q_mode       = params.get("question_mode", "grouped")
        if q_mode == "sprechen":
            content_text = sanitize.allow_html(request.form.get("spk_situation", ""))
        # end if
        sq_q_text    = sanitize.allow_html(request.form.get("sq_question_text", ""))
        sq_exp       = sanitize.allow_html(request.form.get("sq_explanation", ""))

        from question_bank import question_bank_proc

        existing_passage = question_bank_proc.get_passage_by_id(passage_pkey).get("data") or {}
        saved_section_id = existing_passage.get("fk_package_section_id", "")
        sub_type_raw     = params.get("passage_sub_type", "") or existing_passage.get("passage_sub_type", "")
        section_key      = (params.get("section_key") or existing_passage.get("section_key") or "").lower().strip()
        sub_type_key     = (sub_type_raw or existing_passage.get("sub_type_key") or "").lower().strip()
        if not section_key and saved_section_id:
            section_key, sub_type_key = _resolve_section_keys(saved_section_id, sub_type_raw)
        # end if

        is_sprechen = q_mode == "sprechen" or existing_passage.get("question_mode") == "sprechen"
        question_bank_proc.update_passage(
            passage_pkey     = passage_pkey,
            title            = params.get("title", ""),
            content_type     = "audio" if params.get("audio_url") else "text",
            content_text     = content_text,
            audio_url        = params.get("audio_url", ""),
            question_mode    = q_mode,
            passage_sub_type = sub_type_raw,
            section_key      = section_key,
            sub_type_key     = sub_type_key,
            cloze_answer_mode= (existing_passage.get("answer_type") == "cloze")
                               and params.get("cloze_answer_mode") or None,
            instruction      = sanitize.allow_html(request.form.get("spk_instruction", "")) if is_sprechen else None,
            sample_answer    = sanitize.allow_html(request.form.get("spk_sample_answer", "")) if is_sprechen else None,
            image_url        = params.get("spk_image_url", "") if is_sprechen else None,
            prep_seconds     = params.get("spk_prep_seconds", 0) if is_sprechen else None,
            speak_seconds    = params.get("spk_speak_seconds", 0) if is_sprechen else None,
            is_premium       = (params.get("is_premium") == "1") if is_sprechen else None,
        )

        # Single mode: update or create the inline question
        if q_mode == "single" and sq_q_text:
            existing      = question_bank_proc.get_questions_by_passage(passage_pkey)
            existing_list = existing.get("data", [])
            if existing_list:
                question_bank_proc.update_question(
                    question_pkey  = existing_list[0]["pkey"],
                    question_text  = sq_q_text,
                    option_a       = params.get("sq_option_a", ""),
                    option_b       = params.get("sq_option_b", ""),
                    option_c       = params.get("sq_option_c", ""),
                    option_d       = params.get("sq_option_d", ""),
                    correct_answer = params.get("sq_correct_answer", "A"),
                    explanation    = sq_exp,
                    section_key    = section_key,
                    sub_type_key   = sub_type_key,
                    option_images  = _option_images(params, "sq_"),
                    is_premium     = params.get("sq_is_premium") == "1",
                )
            else:
                question_bank_proc.create_question(
                    passage_pkey   = passage_pkey,
                    section_id     = saved_section_id,
                    expert_id      = g.current_user["user_id"],
                    question_text  = sq_q_text,
                    option_a       = params.get("sq_option_a", ""),
                    option_b       = params.get("sq_option_b", ""),
                    option_c       = params.get("sq_option_c", ""),
                    option_d       = params.get("sq_option_d", ""),
                    correct_answer = params.get("sq_correct_answer", "A"),
                    explanation    = sq_exp,
                    section_key    = section_key,
                    sub_type_key   = sub_type_key,
                    option_images  = _option_images(params, "sq_"),
                    is_premium     = params.get("sq_is_premium") == "1",
                )
            # end if
        # end if

        return redirect("/expert/question-bank/" + passage_pkey)
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@question_bank_blueprint.route("/expert/question-bank/delete-selected", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def delete_selected_passages_post():
    try:
        from question_bank import question_bank_proc
        raw_pkeys = request.form.getlist("passage_pkey")
        pkeys = []
        for raw in raw_pkeys:
            cleaned = sanitize.clean_html_dic({"p": raw}).get("p", "")
            if cleaned:
                pkeys.append(cleaned)
            # end if
        # end for
        question_bank_proc.delete_passages(pkeys)
        params = sanitize.clean_html_dic(request.form.to_dict())
        return _bank_list_redirect(
            params.get("section", ""), params.get("mode", ""),
            params.get("page", ""), params.get("per_page", ""),
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@question_bank_blueprint.route("/expert/question-bank/delete-all", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def delete_all_passages_post():
    try:
        from question_bank import question_bank_proc
        params = sanitize.clean_html_dic(request.form.to_dict())
        filter_section = (params.get("section") or "").lower().strip()
        filter_mode    = (params.get("mode") or "").lower().strip()
        pkeys = question_bank_proc.list_bank_passage_pkeys(
            expert_id     = g.current_user["user_id"],
            section_key   = filter_section,
            question_mode = filter_mode,
        ).get("data", [])
        question_bank_proc.delete_passages(pkeys)
        return _bank_list_redirect(filter_section, filter_mode, "", params.get("per_page", ""))
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@question_bank_blueprint.route("/expert/question-bank/<passage_pkey>/delete", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def delete_passage_post(passage_pkey):
    try:
        from question_bank import question_bank_proc
        question_bank_proc.delete_passage(passage_pkey)
        params = sanitize.clean_html_dic(request.form.to_dict())
        return _bank_list_redirect(
            params.get("section", ""), params.get("mode", ""),
            params.get("page", ""), params.get("per_page", ""),
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@question_bank_blueprint.route("/expert/question-bank/<passage_pkey>/questions/create", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def create_question_post(passage_pkey):
    try:
        params      = sanitize.clean_html_dic(request.form.to_dict())
        explanation = sanitize.allow_html(request.form.get("explanation", ""))
        question_text = sanitize.allow_html(request.form.get("question_text", ""))

        from question_bank import question_bank_proc

        passage_result = question_bank_proc.get_passage_by_id(passage_pkey)
        passage        = passage_result.get("data", {})
        p_section_id   = passage.get("fk_package_section_id", "")
        p_sub_type     = passage.get("passage_sub_type", "")
        p_section_key, p_sub_type_key = _resolve_section_keys(p_section_id, p_sub_type)
        if passage.get("answer_type") == "cloze":
            gap_no = sanitize.clean_int(params.get("gap_no"), 0) or (int(passage.get("question_count") or 0) + 1)
            question_text = question_bank_proc.cloze_question_text(gap_no)
        # end if

        question_bank_proc.create_question(
            passage_pkey  = passage_pkey,
            section_id    = p_section_id,
            expert_id     = g.current_user["user_id"],
            question_text = question_text,
            option_a      = params.get("option_a", ""),
            option_b      = params.get("option_b", ""),
            option_c      = params.get("option_c", ""),
            option_d      = params.get("option_d", ""),
            correct_answer= params.get("correct_answer", "A"),
            explanation   = explanation,
            section_key   = p_section_key,
            sub_type_key  = p_sub_type_key,
            option_images = _option_images(params),
            answer_text   = params.get("answer_text", ""),
            is_premium    = params.get("is_premium") == "1",
        )
        return redirect("/expert/question-bank/" + passage_pkey)
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@question_bank_blueprint.route("/expert/question-bank/questions/<question_pkey>/update", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def update_question_post(question_pkey):
    try:
        params        = sanitize.clean_html_dic(request.form.to_dict())
        explanation   = sanitize.allow_html(request.form.get("explanation", ""))
        question_text = sanitize.allow_html(request.form.get("question_text", ""))
        passage_pkey  = params.get("passage_pkey", "")

        from question_bank import question_bank_proc
        passage = question_bank_proc.get_passage_by_id(passage_pkey).get("data") or {}
        gap_no  = sanitize.clean_int(params.get("gap_no"), 0)
        if passage.get("answer_type") == "cloze" and gap_no:
            question_text = question_bank_proc.cloze_question_text(gap_no)
        # end if
        question_bank_proc.update_question(
            question_pkey  = question_pkey,
            question_text  = question_text,
            option_a       = params.get("option_a", ""),
            option_b       = params.get("option_b", ""),
            option_c       = params.get("option_c", ""),
            option_d       = params.get("option_d", ""),
            correct_answer = params.get("correct_answer", "A"),
            explanation    = explanation,
            option_images  = _option_images(params),
            answer_text    = params.get("answer_text", None),
            is_premium    = params.get("is_premium") == "1",
        )
        return redirect("/expert/question-bank/" + passage_pkey)
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@question_bank_blueprint.route("/expert/question-bank/questions/<question_pkey>/delete", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def delete_question_post(question_pkey):
    try:
        params       = sanitize.clean_html_dic(request.form.to_dict())
        passage_pkey = params.get("passage_pkey", "")

        from question_bank import question_bank_proc
        question_bank_proc.delete_question(question_pkey)
        return redirect("/expert/question-bank/" + passage_pkey)
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


ALLOWED_AUDIO_EXTENSIONS = {"mp3", "wav", "ogg", "m4a", "aac", "flac"}
MAX_AUDIO_SIZE_MB = 20

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp", "svg"}
MAX_IMAGE_SIZE_MB = 5


@question_bank_blueprint.route("/expert/upload-image", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def upload_image():
    try:
        if "file" not in request.files:
            return jsonify({"status": "error", "message": "Tidak ada file yang dikirim"}), 400
        # end if

        f = request.files["file"]
        if not f or f.filename == "":
            return jsonify({"status": "error", "message": "File kosong"}), 400
        # end if

        ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            return jsonify({"status": "error", "message": f"Format .{ext} tidak didukung. Gunakan JPG, PNG, GIF, WebP."}), 400
        # end if

        f.seek(0, 2)
        size_bytes = f.tell()
        f.seek(0)
        if size_bytes > MAX_IMAGE_SIZE_MB * 1024 * 1024:
            return jsonify({"status": "error", "message": f"File terlalu besar (maks {MAX_IMAGE_SIZE_MB} MB)"}), 400
        # end if

        filename  = uuid.uuid4().hex + "." + ext
        img_dir   = os.path.join(current_app.root_path, "static", "images")
        os.makedirs(img_dir, exist_ok=True)
        f.save(os.path.join(img_dir, filename))

        url = "/static/images/" + filename
        return jsonify({"status": "ok", "url": url})
    except Exception:
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": "Upload gagal, coba lagi"}), 500
    # end try
# end def

@question_bank_blueprint.route("/expert/upload-audio", methods=["POST"])
@middleware_privilege(roles=["super_admin", "expert"])
def upload_audio():
    try:
        if "file" not in request.files:
            return jsonify({"status": "error", "message": "Tidak ada file yang dikirim"}), 400
        # end if

        f = request.files["file"]
        if not f or f.filename == "":
            return jsonify({"status": "error", "message": "File kosong"}), 400
        # end if

        ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
        if ext not in ALLOWED_AUDIO_EXTENSIONS:
            return jsonify({"status": "error", "message": f"Format .{ext} tidak didukung. Gunakan MP3, WAV, OGG, M4A."}), 400
        # end if

        # Check size (read into memory briefly; reset pointer)
        f.seek(0, 2)
        size_bytes = f.tell()
        f.seek(0)
        if size_bytes > MAX_AUDIO_SIZE_MB * 1024 * 1024:
            return jsonify({"status": "error", "message": f"File terlalu besar (maks {MAX_AUDIO_SIZE_MB} MB)"}), 400
        # end if

        filename  = uuid.uuid4().hex + "." + ext
        audio_dir = os.path.join(current_app.root_path, "static", "audio")
        os.makedirs(audio_dir, exist_ok=True)
        f.save(os.path.join(audio_dir, filename))

        url = "/static/audio/" + filename
        return jsonify({"status": "ok", "url": url, "filename": filename})
    except Exception:
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": "Upload gagal, coba lagi"}), 500
    # end try
# end def
