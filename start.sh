#!/bin/bash
# Botni 24/7 ishlatish uchun start script

cd "$(dirname "$0")"
source venv/bin/activate
python run_both.py

