"""
german_ai_proc.py
-----------------
Menghasilkan feedback AI (Gemini / OpenAI) setelah peserta menyelesaikan ujian bahasa Jerman.
Dipanggil oleh exam_engine_proc.submit_exam() setelah skor dihitung.

Jika API key tidak dikonfigurasi atau terjadi error, fungsi ini gagal secara graceful
(tidak melempar exception ke luar) sehingga flow ujian tetap berjalan.
"""

import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_stdlib")

import traceback
import time
import json

import database
import config
import idgen


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _build_prompt(result_doc, sections):
    """Buat prompt bahasa Indonesia + konteks ujian bahasa Jerman."""
    test_type   = result_doc.get("test_type_code", "")
    total_score = result_doc.get("total_score", 0)
    breakdown   = result_doc.get("section_breakdown", {})

    sec_lines = []
    for sec_pkey, info in breakdown.items():
        title   = info.get("title", sec_pkey)
        correct = info.get("correct", 0)
        total   = info.get("total", 0)
        score   = info.get("score", 0)
        sec_lines.append(f"  - {title}: {correct}/{total} benar ({score:.1f}%)")
    # end for
    sec_text = "\n".join(sec_lines) if sec_lines else "  (tidak ada rincian seksi)"

    prompt = f"""Kamu adalah tutor bahasa Jerman berpengalaman yang memberikan feedback setelah ujian.

Peserta baru saja menyelesaikan ujian *{test_type or 'Bahasa Jerman'}* dengan hasil berikut:
- Skor total: {total_score:.1f}%
- Rincian per seksi:
{sec_text}

Berikan feedback yang:
1. Mengapresiasi usaha peserta
2. Menyebutkan kekuatan (Stärken) berdasarkan hasil seksi
3. Menyebutkan area yang perlu diperbaiki (Verbesserungsbereiche)
4. Estimasi level CEFR saat ini (A1/A2/B1/B2/C1/C2) berdasarkan skor
5. 2–3 tips belajar bahasa Jerman yang spesifik

Jawab dalam bahasa Indonesia yang ramah dan memotivasi.
Format jawaban HARUS dalam JSON dengan struktur:
{{
  "feedback_text": "<paragraf feedback utama>",
  "level_estimate": "<A1|A2|B1|B2|C1|C2>",
  "strengths": ["<poin 1>", "<poin 2>"],
  "improvements": ["<poin 1>", "<poin 2>"]
}}
"""
    return prompt
# end def


def _call_gemini(prompt):
    """Panggil Gemini API menggunakan google-generativeai."""
    import google.generativeai as genai  # noqa: F401 — optional dep
    genai.configure(api_key=config.G_GEMINI_API_KEY)
    model    = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    raw      = response.text.strip()

    # Bersihkan markdown code block kalau ada
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    # end if

    return json.loads(raw.strip())
# end def


def _call_openai(prompt):
    """Panggil OpenAI ChatCompletion (fallback)."""
    import openai  # noqa: F401 — optional dep
    openai.api_key = config.G_OPENAI_API_KEY
    resp = openai.chat.completions.create(
        model    = "gpt-4o-mini",
        messages = [{"role": "user", "content": prompt}],
        response_format = {"type": "json_object"},
    )
    raw = resp.choices[0].message.content.strip()
    return json.loads(raw)
# end def


# ─── Public API ───────────────────────────────────────────────────────────────

def generate_and_save_feedback(result_pkey, exam_session_pkey, user_pkey, package_pkey, section_breakdown, total_score, test_type_code=""):
    """
    Generate AI feedback dan simpan ke db_german_ai_feedback.
    Return dict {"status": "OK"|"ERROR", "feedback_id": "..."}.
    Gagal secara graceful — tidak raise exception ke pemanggil.
    """
    try:
        api_key_gemini = getattr(config, "G_GEMINI_API_KEY", "")
        api_key_openai = getattr(config, "G_OPENAI_API_KEY", "")

        if not api_key_gemini and not api_key_openai:
            return {"status": "SKIPPED", "message": "Tidak ada AI API key dikonfigurasi"}
        # end if

        result_doc = {
            "test_type_code" : test_type_code,
            "total_score"    : total_score,
            "section_breakdown": section_breakdown,
        }
        prompt   = _build_prompt(result_doc, [])
        provider = "none"
        parsed   = {}

        if api_key_gemini:
            try:
                parsed   = _call_gemini(prompt)
                provider = "gemini"
            except Exception:
                print("[german_ai_proc] Gemini gagal, coba OpenAI...")
                print(traceback.format_exc())
            # end try
        # end if

        if not parsed and api_key_openai:
            try:
                parsed   = _call_openai(prompt)
                provider = "openai"
            except Exception:
                print("[german_ai_proc] OpenAI juga gagal.")
                print(traceback.format_exc())
                return {"status": "ERROR", "message": "AI tidak tersedia"}
            # end try
        # end if

        if not parsed:
            return {"status": "ERROR", "message": "AI tidak menghasilkan output"}
        # end if

        mgdDB = database.get_db_conn(config.mainDB)
        now   = int(time.time() * 1000)

        rec = database.new(mgdDB, "db_german_ai_feedback")
        rec.put("feedback_id",          idgen._get_unique_id())
        rec.put("fk_result_id",         result_pkey)
        rec.put("fk_exam_session_id",   exam_session_pkey)
        rec.put("fk_user_id",           user_pkey)
        rec.put("fk_package_id",        package_pkey)
        rec.put("ai_provider",          provider)
        rec.put("feedback_text",        parsed.get("feedback_text", ""))
        rec.put("level_estimate",       parsed.get("level_estimate", ""))
        rec.put("strengths",            parsed.get("strengths", []))
        rec.put("improvements",         parsed.get("improvements", []))
        rec.put("status",               "OK")
        rec.put("generated_at",         now)
        feedback_pkey = rec._mongo_record.get("pkey", "")
        rec.insert()

        return {"status": "OK", "feedback_id": feedback_pkey, "data": parsed}

    except Exception:
        print("[german_ai_proc] Unexpected error:")
        print(traceback.format_exc())
        return {"status": "ERROR", "message": "Gagal generate AI feedback"}
    # end try
# end def


def get_feedback_for_result(result_pkey):
    """Ambil AI feedback berdasarkan result_pkey."""
    try:
        mgdDB    = database.get_db_conn(config.mainDB)
        feedback = mgdDB.db_german_ai_feedback.find_one({
            "fk_result_id" : result_pkey,
            "status"       : "OK",
            "is_deleted"   : False,
        })
        return {"status": "OK", "data": feedback}
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "data": None}
    # end try
# end def

