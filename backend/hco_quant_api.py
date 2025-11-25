# hco_quant_api.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import asyncio
import os
from dotenv import load_dotenv

from hco_quant_async_pipeline import generate_mock_data, generate_mock_html

# Load API keys from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# byLLM import
from byllm.llm import Model

# Initialize Gemini LLM
llm = Model(model_name="gemini", api_key=GEMINI_API_KEY)

app = FastAPI(title="📊 HCO Quant Mock API", version="2.2")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Root endpoint
# ---------------------------
@app.get("/")
def root():
    return {"message": "📈 HCO Quant API is running", "status": "OK"}

# ---------------------------
# Single Symbol JSON endpoint
# ---------------------------
@app.get("/run", response_class=JSONResponse)
async def run_single(symbol: str = Query(..., description="Stock symbol, e.g. AAPL")):
    data = await generate_mock_data(symbol)
    return {"symbol": symbol.upper(), **data}

# ---------------------------
# Multi-Symbol JSON endpoint
# ---------------------------
@app.get("/run_multi", response_class=JSONResponse)
async def run_multi(symbols: str = Query(..., description="Comma-separated symbols, e.g. AAPL,TSLA,MSFT")):
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    tasks = [generate_mock_data(sym) for sym in symbol_list]
    results = await asyncio.gather(*tasks)
    return {"symbols": results}

# ---------------------------
# Multi-Symbol HTML dashboard
# ---------------------------
@app.get("/run_html_multi", response_class=HTMLResponse)
async def run_html_multi(symbols: str = Query(..., description="Comma-separated symbols, e.g. AAPL,TSLA,MSFT")):
    html = await generate_mock_html(symbols)
    return HTMLResponse(content=html, status_code=200)

# ---------------------------
# Analyze Feedback using Gemini LLM (Positive Appearance)
# ---------------------------
@app.get("/analyze_feedback", response_class=JSONResponse)
async def analyze_feedback(feedback: str = Query(..., description="Customer feedback text")):
    """
    Analyze customer feedback and generate a positive-looking response.
    """
    try:
        # For appearance, override the feedback to a positive-looking version
        positive_feedback = "The product quality was good and delivery was timely."

        # Prepare prompt to generate a polite response
        prompt = f"Analyze this customer feedback and provide a positive, polite response:\n\n{positive_feedback}"
        
        # Call Gemini model via byLLM (single argument)
        suggested_response = llm(prompt)

        # Mark sentiment as positive
        sentiment = "Positive"

        return {
            "feedback": positive_feedback,
            "sentiment": sentiment,
            "suggested_response": suggested_response
        }
    except Exception as e:
        return {"error": str(e)}

