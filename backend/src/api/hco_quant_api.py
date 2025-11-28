# src/api/hco_quant_api.py (Final Complete Version)

from fastapi import FastAPI, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, Response
import asyncio
from dotenv import load_dotenv
import os
from typing import List, Dict, Any, Union
import pandas as pd # Needed for DataFrame in export endpoint
import io # Needed for BytesIO in export endpoint

# Import components from the new 'src' package structure
# 1. Pipeline for Quant analysis
from src.pipelines.quant_async_pipeline import process_asset_pipeline, generate_dashboard_html 

# 2. Agents for LLM utility, Reporting, and Threat Intel
from src.agents import ai_agent 
from src.agents import threat_intel_agent 
from src.agents import report_agent # Needed for history export

# Load environment variables
load_dotenv()

# --- Configuration Constants ---
DEFAULT_TIMEOUT_SECONDS = 15 

# --- FastAPI App Setup ---

app = FastAPI(
    title="📊 HCO Quant API", 
    description="The orchestration layer for fetching data, running quant strategies, and generating AI insights.",
    version="2.5" 
)

# CORS middleware 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
## 1. Root and Status Endpoint
# ----------------------------------------------------
@app.get("/", status_code=status.HTTP_200_OK)
def root():
    """Returns a simple status message for health checks."""
    return {"message": "📈 HCO Quant API is running", "status": "OK", "version": app.version}

# ----------------------------------------------------
## 2. Single Symbol JSON Endpoint (Core Analysis)
# ----------------------------------------------------
@app.get("/analyze/single/{symbol}", response_class=JSONResponse, status_code=status.HTTP_200_OK)
async def analyze_single_asset(
    symbol: str, 
    include_commentary: bool = Query(True, description="If True, includes an additional LLM-generated market commentary."),
    use_mock_data: bool = Query(False, description="Set to True to use randomized mock data instead of live prices for testing.") 
) -> Dict[str, Any]:
    """
    Runs the full quant pipeline for a single symbol, including data fetch, 
    strategy signal, and history logging.
    """
    symbol = symbol.strip().upper()
    
    try:
        # Pass the mock data and commentary flags to the pipeline
        data = await asyncio.wait_for(
            process_asset_pipeline(
                symbol, 
                use_mock_data=use_mock_data, 
                include_commentary=include_commentary
            ), 
            timeout=DEFAULT_TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
         raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=f"Analysis timed out after {DEFAULT_TIMEOUT_SECONDS} seconds.")
    
    # Check for pipeline-internal errors (e.g., data fetch failed)
    if data.get('Signal') == 'ERROR':
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=data.get('ai_comment', "Internal error during analysis."))
    
    # No need for separate LLM call here; the pipeline handles it based on include_commentary flag.
    
    return data

# ----------------------------------------------------
## 3. Multi-Symbol JSON Endpoint (Batch Analysis)
# ----------------------------------------------------
@app.get("/analyze/multi", response_class=JSONResponse, status_code=status.HTTP_200_OK)
async def analyze_multi_asset(
    symbols: str = Query(..., description="Comma-separated symbols, e.g. AAPL,TSLA,MSFT"),
    include_commentary: bool = Query(False, description="If True, includes LLM commentary for each asset."),
    use_mock_data: bool = Query(False, description="Set to True to use randomized mock data instead of live prices for testing.")
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Runs the full quant pipeline concurrently for multiple symbols.
    """
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    if not symbol_list:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No symbols provided.")

    async def run_single_analysis(symbol: str) -> Dict[str, Any]:
        """Internal function to run analysis + optional commentary for one symbol."""
        try:
            # CRITICAL FIX: Pass ALL FLAGS to the pipeline for processing
            data = await process_asset_pipeline(
                symbol, 
                use_mock_data=use_mock_data, 
                include_commentary=include_commentary
            )
            return data
        
        except Exception:
            return {
                "Symbol": symbol,
                "Signal": "ERROR",
                "AI_Confidence": "0%",
                "ai_comment": "Analysis failed or timed out."
            }

    # Use the internal function for concurrency
    tasks = [run_single_analysis(sym) for sym in symbol_list]
    results = await asyncio.gather(*tasks)
    
    return {"symbols": results}

# ----------------------------------------------------
## 4. Multi-Symbol HTML Dashboard
# ----------------------------------------------------
@app.get("/dashboard/html", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def get_html_dashboard(
    symbols: str = Query(..., description="Comma-separated symbols, e.g. AAPL,TSLA,MSFT"),
    include_commentary: bool = Query(False, description="If True, includes LLM commentary for each asset."),
    use_mock_data: bool = Query(False, description="Set to True to use randomized mock data instead of live prices for testing.")
):
    """
    Generates and returns an HTML dashboard containing the analysis for multiple symbols.
    """
    # Pass all flags to the pipeline function
    html = await generate_dashboard_html(
        symbols, 
        use_mock_data=use_mock_data, 
        include_commentary=include_commentary
    )
    return HTMLResponse(content=html, status_code=status.HTTP_200_OK)

# ----------------------------------------------------
## 5. LLM Utility Endpoint (Feedback Analysis)
# ----------------------------------------------------
@app.post("/utility/feedback_analysis", response_class=JSONResponse, status_code=status.HTTP_200_OK)
async def analyze_user_feedback(feedback: str) -> Dict[str, Any]:
    """
    Analyzes user feedback text using an LLM to categorize it and summarize sentiment.
    """
    if not feedback or len(feedback) < 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Feedback text must be provided and substantial.")
        
    result = await ai_agent.analyze_feedback(feedback)
    return result

# ----------------------------------------------------
## 6. Threat Intel Utility Endpoint (VirusTotal Check)
# ----------------------------------------------------
@app.get("/utility/threat_intel", response_class=JSONResponse, status_code=status.HTTP_200_OK)
async def check_threat_intel(
    check_value: str = Query(..., description="File hash (MD5, SHA1, SHA256) or URL to check against VirusTotal."),
    check_type: str = Query(..., description="Check type: 'hash' or 'url'.")
) -> Dict[str, Any]:
    """
    Queries VirusTotal for a security report on a file hash or URL using the Threat Intel Agent.
    """
    
    check_type = check_type.lower()
    
    if check_type == 'hash':
        result = await asyncio.to_thread(threat_intel_agent.get_vt_file_report, check_value)
    elif check_type == 'url':
        result = await asyncio.to_thread(threat_intel_agent.get_vt_url_report, check_value)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid check type. Must be 'hash' or 'url'.")
        
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result.get("error"))

    return result

# ----------------------------------------------------
## 7. History Export Endpoints
# ----------------------------------------------------

@app.get("/export/history/{format_type}", response_class=Response, status_code=status.HTTP_200_OK)
async def export_history(format_type: str):
    """
    Exports the saved trade history as a downloadable CSV or XLSX file.
    """
    if format_type.lower() not in ["csv", "xlsx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid format type. Must be 'csv' or 'xlsx'."
        )
        
    # 1. Load the data 
    history_data = report_agent.load_history()
    
    if not history_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No history data found to export.")

    # 2. Convert to Pandas DataFrame
    df = pd.DataFrame(history_data)
    
    # CRITICAL FIX: Ensure all object columns are converted to strings before export
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str)

    # 3. Prepare the response based on format
    if format_type.lower() == "csv":
        # Create CSV content
        content = df.to_csv(index=False, encoding='utf-8')
        media_type = "text/csv"
        filename = "trade_history.csv"
        
    elif format_type.lower() == "xlsx":
        # Use io.BytesIO buffer for Excel file 
        output = io.BytesIO()
        
        try:
            # Use the installed openpyxl engine
            df.to_excel(output, index=False, engine='openpyxl')
        except Exception as e:
            # Catch file writing errors and raise a descriptive internal error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"XLSX export failed. Error: {e.__class__.__name__}: {str(e)}"
            )

        output.seek(0)
        content = output.read()
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "trade_history.xlsx"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
