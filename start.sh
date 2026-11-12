#!/bin/bash
export FLASK_APP=server.py
export FLASK_ENV=development
export LC_ALL=en_US.utf8
export LANG=en_US.utf8

# Aktifkan virtualenv (sesuaikan nama folder venv jika berbeda)
if [ -d "venv3810" ]; then
    source venv3810/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "[start.sh] WARNING: virtual env tidak ditemukan. Jalankan: python3 -m venv venv && pip install -r requirements.txt"
fi

# Seed users & test types (idempoten – aman dijalankan berulang)
python seed_users.py

python -m flask run --host=0.0.0.0 --port=50042

