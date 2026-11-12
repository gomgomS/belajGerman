#!/usr/bin/env python3
"""
seed_users.py
─────────────
Script seed: inject default dev users ke MongoDB german_platform.
Jalankan dari root project di WSL:

    source venv3810/bin/activate
    python seed_users.py

atau langsung:
    python3 seed_users.py

Idempoten: kalau user sudah ada, password & role diperbarui.
"""

import sys
import os

# Pastikan path tersedia
sys.path.insert(0, "slapz102_core")
sys.path.insert(0, "slapz102_modules")
sys.path.insert(0, "slapz102_stdlib")
sys.path.insert(0, "slapz102_settings")
sys.path.insert(0, "slapz102_storage")

import database
import config

# ── sambung DB ────────────────────────────────────────────────────────────────
print(f"[seed] Menghubungkan ke: {config.mainDB_string}")
database.connect_db()
mgdDB = database.get_db_conn(config.mainDB)
print(f"[seed] Terhubung ke database: {config.mainDB}")

# ── import auth setelah path siap ─────────────────────────────────────────────
from auth.auth_proc import ensure_dev_user
from app_settings.app_settings_proc import ensure_default_test_settings

# ── seed users ────────────────────────────────────────────────────────────────
users_to_seed = [
    {
        "full_name" : "Admin Utama",
        "email"     : config.G_ADMIN_EMAIL,
        "password"  : config.G_ADMIN_PASSWORD,
        "role"      : "super_admin",
    },
    {
        "full_name" : "Expert Pengajar",
        "email"     : config.G_EXPERT_EMAIL,
        "password"  : config.G_EXPERT_PASSWORD,
        "role"      : "expert",
    },
    {
        "full_name" : "Siswa Demo",
        "email"     : config.G_SISWA_EMAIL,
        "password"  : config.G_SISWA_PASSWORD,
        "role"      : "peserta",
    },
]

print("\n── Seed Users ──────────────────────────────────────────────")
for u in users_to_seed:
    result = ensure_dev_user(
        full_name = u["full_name"],
        email     = u["email"],
        password  = u["password"],
        role      = u["role"],
    )
    icon = "✓" if result["status"] == "OK" else "✗"
    print(f"  {icon} [{u['role']:12s}] {u['email']}  → {result.get('message', result['status'])}")
# end for

# ── seed test types German ────────────────────────────────────────────────────
print("\n── Seed Test Types (German) ─────────────────────────────────")
german_codes = ["A1", "A2", "B1", "B2", "C1", "TESTDAF", "DSH"]
german_count = mgdDB.db_level.count_documents({"code": {"$in": german_codes}, "is_deleted": False})

if german_count == 0:
    # Hapus tipe tes lama bahasa Inggris jika ada
    mgdDB.db_level.delete_many({"code": {"$in": ["ITP", "IBT", "IELTS"]}})
    mgdDB.db_toefl_section_template.delete_many({"fk_test_type_code": {"$in": ["ITP", "IBT", "IELTS"]}})
    print("  · Membersihkan tipe tes lama (ITP/IBT/IELTS)...")

seed_result = ensure_default_test_settings()
if seed_result.get("seeded") or german_count == 0:
    print("  ✓ Tipe tes German (A1–C2, TestDaF, DSH) berhasil di-seed!")
elif seed_result["status"] == "OK":
    print("  · Tipe tes German sudah ada di database.")
else:
    print("  ✗ Gagal seed tipe tes:", seed_result)
# end if

print("\n[seed] Selesai!\n")
print("── Credentials ─────────────────────────────────────────────")
for u in users_to_seed:
    print(f"  {u['role']:12s}  {u['email']}  /  {u['password']}")
print("────────────────────────────────────────────────────────────\n")

