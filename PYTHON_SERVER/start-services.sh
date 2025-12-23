#!/bin/bash
python -m uvicorn app.api_main:app --host 0.0.0.0 --port 8000 &

python3 -u app/main.py