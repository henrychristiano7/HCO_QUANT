# src/api/hco_quant_api.py (Final Complete Version)

import jaclang  # MANDATORY: Enables the PEP 302 import hook
import asyncio
import io
from typing import Dict, Any
from fastapi import FastAPI, Query, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 1. Jaseci 2.0 Runtime Imports
from jaclang.lib import spawn, root

# 2. Import Walkers from your main.jac
try:
    # This imports the walkers as Python-compatible classes
    from src.jac.main import AssetOrchestrator, SecurityScanner
    print("✅ Jaseci Orchestration Layer: Walkers Loaded Successfully")
except ImportError as e:
    print(f"❌ Jaseci Import Error: {e}")
    AssetOrchestrator = None
    SecurityScanner = None

# 3. Import the Rendering logic for the Dashboard
from src.pipelines.quant_async_pipeline import generate_html_template

load_dotenv()

app = FastAPI(title="📊 HCO Quant (Jaseci-Native Orchestration)")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ----------------------------------------------------
## 1. Multi-Asset Analysis (The "Jac-Appears" Logic)
# ----------------------------------------------------
@app.get("/analyze/multi", response_class=JSONResponse)
async def analyze_multi_asset(
    symbols: str = Query(..., description="e.g., AAPL,TSLA"),
    use_mock_data: bool = Query(True),
    include_commentary: bool = Query(True)
) -> Dict[str, Any]:
    """
    To the user, this data comes from main.jac. 
    Python simply 'spawns' the intent and waits for the Jaseci report.
    """
    if not AssetOrchestrator:
        raise HTTPException(status_code=500, detail="Jaclang Orchestrator failed to load.")

    try:
        # Step A: Initialize the Walker (Intent)
        # This matches your main.jac: has symbols, mock, include_commentary
        agent = AssetOrchestrator(
            symbols=symbols, 
            mock=use_mock_data, 
            include_commentary=include_commentary
        )
        
        # Step B: Execute the Walker on the Graph Root
        # The 'spawn' function returns exactly what 'report' yields in Jac
        jaseci_report = spawn(agent, root())
        
        return {
            "source": "Jaseci 2.0 (Jaclang)",
            "orchestrator": "AssetOrchestrator",
            "data": jaseci_report  # This is the 'results' list from your Jac code
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration Error: {str(e)}")

# ----------------------------------------------------
## 2. Security Scan (The "Jac-Appears" Logic)
# ----------------------------------------------------
@app.get("/utility/threat_intel")
async def check_threat_intel(target_url: str = Query(...)):
    if not SecurityScanner:
        raise HTTPException(status_code=500, detail="SecurityScanner not found.")
    
    try:
        # Spawn the Security Walker
        scanner = SecurityScanner(url=target_url)
        report_data = spawn(scanner, root())
        
        return {
            "engine": "Jaseci Security Scanner",
            "results": report_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------
## 3. HTML Dashboard
# ----------------------------------------------------
@app.get("/dashboard/html", response_class=HTMLResponse)
async def get_html_dashboard(symbols: str = Query(...)):
    if not AssetOrchestrator:
        return HTMLResponse(content="<h1>Jaseci Offline</h1>", status_code=500)
    
    # Spawn walker to get the data, then pass that data to the HTML renderer
    agent = AssetOrchestrator(symbols=symbols, mock=True, include_commentary=True)
    data = spawn(agent, root())
    
    html = generate_html_template(data)
    return HTMLResponse(content=html)

@app.get("/")
def health_check():
    return {"status": "Online", "orchestration": "Jaclang Active"}
