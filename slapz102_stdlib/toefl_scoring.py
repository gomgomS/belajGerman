import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import json
import os


def _load_json(filename):
    base = os.path.join(os.getcwd(), "static", "json", filename)
    with open(base, "r", encoding="utf-8") as f:
        return json.load(f)
    # end with
# end def


def get_itp_config():
    """Return TOEFL ITP section config (questions, duration, score range)."""
    return _load_json("toefl_itp_config.json")
# end def


def get_section_config(section_type: str) -> dict:
    """Return the config block for a specific section_type.
    Comparison is case-insensitive. Returns None if not found."""
    if not section_type:
        return None
    # end if
    key = section_type.lower().strip()
    alias = {
        "listening": "hoeren",
        "reading"  : "lesen",
        "structure": "struktur",
    }
    key = alias.get(key, key)
    cfg = get_itp_config()
    for sec in cfg.get("sections", []):
        if sec.get("section_type", "").lower() == key or sec.get("key", "").lower() == key:
            return sec
        # end if
    # end for
    return None
# end def


def get_conversion_table():
    """Return raw conversion table rows list."""
    data = _load_json("toefl_itp_score_conversion.json")
    return data["table"]
# end def


def convert_section_score(correct: int, section: str) -> int:
    """
    Look up the converted section score for a given number of correct answers.
    section: 'listening' | 'structure' | 'reading'
    Returns the mapped score, or the minimum score (20/21) if not found.
    """
    section = section.lower()
    table   = get_conversion_table()

    for row in table:
        if row["correct"] == correct:
            score = row.get(section)
            if score is not None:
                return int(score)
            # end if
        # end if
    # end for

    # fallback: closest row below
    lower_rows = [r for r in table if r["correct"] <= correct and r.get(section) is not None]
    if lower_rows:
        closest = max(lower_rows, key=lambda r: r["correct"])
        return int(closest[section])
    # end if

    return 20
# end def


def calculate_itp_total(listening_correct: int, structure_correct: int, reading_correct: int) -> dict:
    """
    Calculate full TOEFL ITP score from raw correct counts.
    Returns dict with per-section converted scores and total.
    Total formula: (sum of 3 section scores) * 10 / 3, rounded to nearest integer.
    """
    l_score = convert_section_score(listening_correct, "listening")
    s_score = convert_section_score(structure_correct, "structure")
    r_score = convert_section_score(reading_correct,   "reading")

    total   = round((l_score + s_score + r_score) * 10 / 3)

    # clamp to official range 310–677
    total   = max(310, min(677, total))

    return {
        "listening_correct" : listening_correct,
        "structure_correct" : structure_correct,
        "reading_correct"   : reading_correct,
        "listening_score"   : l_score,
        "structure_score"   : s_score,
        "reading_score"     : r_score,
        "total_score"       : total,
    }
# end def
