#!/bin/bash
source venv/bin/activate
echo "[INFO] Starting HCO_QUANT API..."
uvicorn api:app --reload --host 0.0.0.0 --port 8000
