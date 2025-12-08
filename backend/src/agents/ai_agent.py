# src/agents/ai_agent.py (FINAL COMPLETE VERSION - Stable and Thread-Safe)

import asyncio
from typing import Dict, Any, List, Union
from byllm.lib import Model, by
from dataclasses import dataclass, field
import json
import logging 

# Configure logging for better debugging in the event of thread pool errors
logging.basicConfig(level=logging.INFO)

# --- Pydantic/Dataclass Schema for Structured Output ---
@dataclass
class FeedbackAnalysis:
    """A structured report summarizing user feedback."""
    sentiment: str = field(metadata={"description": "Overall sentiment: Positive, Negative, or Neutral."})
    category: str = field(metadata={"description": "Classification of the feedback: Bug Report, Feature Request, or General Comment."})
    summary: str = field(metadata={"description": "A brief, 1-sentence summary of the user's main point."})
    urgency_score: int = field(metadata={"description": "A score from 1 (Low) to 5 (High) indicating how quickly this feedback needs attention."})
    suggested_action: str = field(metadata={"description": "A concrete step the development team should take."})

# --- LLM Initialization ---
try:
    # Initialize the synchronous byLLM client
    llm = Model(model_name="gemini/gemini-2.5-flash")
except Exception as e:
    logging.error(f"[ERROR] Could not initialize byLLM Model. Check GEMINI_API_KEY. Detail: {e}")
    llm = None

# ----------------------------------------------------------------------
## Core LLM Agent Functions (Synchronous 'def')
# ----------------------------------------------------------------------

# FIX: Function is defined as 'def' and accepts primitive arguments for stability
def generate_trade_comment(
    symbol: str, 
    signal: str, 
    confidence: str, # Accepts the string form (e.g., "82%")
    rationale: str,
    current_price: float
) -> str:
    """
    Generates a concise, high-level commentary using the synchronous byLLM call.
    This function is designed to be executed safely via asyncio.to_thread.
    """
    if not llm:
        return "LLM service unavailable (Client not initialized)."

    # CRITICAL FIX: Prompt updated for strict output enforcement
    @by(llm)
    def generate_commentary(
        symbol: str, 
        signal: str, 
        confidence: int, # Internal LLM prompt requires int
        rationale: str,
        current_price: float
    ) -> str:
        """
        You are a financial analyst. Write a concise, professional 3-sentence market commentary 
        on the trading decision below. The commentary must ONLY be the text and must NOT 
        include JSON, code blocks, bullet points, or any other formatting.

        Focus on the asset: {symbol}
        Current Price: ${current_price}
        Trading Signal: {signal}
        AI Confidence: {confidence}%
        Quant Rationale: {rationale}
        """
        pass

    # Extract and Convert Fields (CRITICAL TYPE CONVERSION)
    
    # Robustly convert confidence string ("82%") to integer (82)
    try:
        confidence_str = str(confidence).strip()
        confidence_int = int(confidence_str.replace('%', ''))
    except (ValueError, TypeError):
        # If conversion fails (e.g., if the value is None or corrupt), default to 0
        confidence_int = 0
        
    try:
        # EXECUTE SYNCHRONOUS BYLLM CALL
        commentary = generate_commentary(
            symbol, signal, confidence_int, rationale, current_price
        )
        # CRITICAL POST-PROCESSING: Strip common LLM filler characters and code block wrappers
        commentary = commentary.strip().strip('`').strip()
        
        return commentary
    except Exception as e:
        # Catches the concurrency/AttributeError and returns a graceful message
        logging.error(f"byLLM Commentary execution crashed: {e}")
        return f"LLM generation failed: Thread pool error ({e.__class__.__name__})."


# FIX: This function remains synchronous ('def')
def analyze_feedback(feedback_text: str) -> Dict[str, Any]:
    """
    Analyzes user feedback text and returns a structured, categorized report.
    This function is designed to be executed safely via asyncio.to_thread.
    """
    if not llm:
        return {"error": "LLM service unavailable (Client not initialized)."}
        
    @by(llm)
    def categorize_feedback(text_input: str) -> FeedbackAnalysis:
        """Structured output prompt."""
        pass

    try:
        # EXECUTE SYNCHRONOUS BYLLM CALL
        analysis_object = categorize_feedback(feedback_text)
        
        # analysis_object is an instance of FeedbackAnalysis, convert to dict
        return analysis_object.__dict__
    except Exception as e:
        logging.error(f"byLLM Analysis execution crashed: {e}")
        return {"error": f"LLM analysis failed: Thread pool error ({e.__class__.__name__})."}
