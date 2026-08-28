#!/usr/bin/env bash
set -e

echo "=== APEX V3 ==="

# 1) تحضير
cp -n .env.example .env || true
mkdir -p data/registry

# 2) تثبيت
pip3 install -r requirements.txt

# 3) تشغيل
python3 scheduler_apex.py
