# src/agents/ai_agent.py

import asyncio
from typing import Dict, Any, List, Union
from byllm.lib import Model, by
from dataclasses import dataclass, field
import json

# --- 1. LLM Initialization ---
# NOTE: This assumes GEMINI_API_KEY is correctly set in your environment variables.
try:
    # Initialize the LLM for use with the @by decorator
    llm = Model(model_name="gemini/gemini-2.5-flash")
except Exception as e:
    # Handle the error if the API key isn't found or initialization fails
    print(f"[ERROR] Could not initialize byLLM model: {e}")
    llm = None

# --- 2. Structured Output Definitions ---

@dataclass
class FeedbackAnalysis:
    """A structured report summarizing user feedback."""
    sentiment: str = field(metadata={"description": "Overall sentiment: Positive, Negative, or Neutral."})
    category: str = field(metadata={"description": "Classification of the feedback: Bug Report, Feature Request, or General Comment."})
    summary: str = field(metadata={"description": "A brief, 1-sentence summary of the user's main point."})
    urgency_score: int = field(metadata={"description": "A score from 1 (Low) to 5 (High) indicating how quickly this feedback needs attention."})
    suggested_action: str = field(metadata={"description": "A concrete step the development team should take."})

# --- 3. Core LLM Agent Functions ---

async def generate_trade_comment(analysis_data: Dict[str, Any]) -> str:
    """
    Generates a concise, high-level commentary on a specific trade signal 
    using an LLM.

    Args:
        analysis_data: The structured output from the quant pipeline 
                       (strategy_agent), containing Symbol, Signal, Confidence, etc.

    Returns:
        A natural language string containing the commentary.
    """
    if not llm:
        return "LLM service unavailable for commentary."

    # This function uses byLLM's programmatic prompting.
    @by(llm)
    def generate_commentary(
        symbol: str, 
        signal: str, 
        confidence: int, 
        rationale: str,
        current_price: float
    ) -> str:
        """
        Write a concise, engaging, and professional 3-sentence market commentary 
        on the following trading decision. The commentary should briefly explain 
        the AI's reasoning (rationale) and advise the user on the next steps.

        Focus on the asset: {symbol}
        Current Price: ${current_price}
        Trading Signal: {signal}
        AI Confidence: {confidence}%
        Quant Rationale: {rationale}
        """
        pass

    # Extract required fields from the pipeline data dictionary
    symbol = analysis_data.get('Symbol', 'N/A')
    signal = analysis_data.get('Signal', 'HOLD')
    confidence = analysis_data.get('AI_Confidence', '0%').replace('%', '') # Remove % for int conversion
    rationale = analysis_data.get('ai_comment', 'No specific reason provided.')
    current_price = analysis_data.get('Close', 0.0)

    # ByLLM functions are synchronous, but we treat them as async 
    # for integration with FastAPI's async framework using run_in_executor.
    loop = asyncio.get_event_loop()
    commentary = await loop.run_in_executor(
        None, # Use the default thread pool executor
        generate_commentary,
        symbol,
        signal,
        int(confidence),
        rationale,
        current_price
    )
    
    return commentary


async def analyze_feedback(feedback_text: str) -> Dict[str, Any]:
    """
    Analyzes user feedback text and returns a structured, categorized report.
    
    Args:
        feedback_text: The raw text feedback provided by the user.

    Returns:
        A dictionary matching the FeedbackAnalysis structure.
    """
    if not llm:
        return {"error": "LLM service unavailable for analysis."}
        
    # This function uses byLLM's structured output capability.
    @by(llm)
    def categorize_feedback(text_input: str) -> FeedbackAnalysis:
        """
        Analyze the user's input text and strictly output a structured report 
        in the required JSON format.
        
        Input Text: {text_input}
        """
        pass

    loop = asyncio.get_event_loop()
    try:
        # Run the synchronous byLLM call in the executor
        analysis_object = await loop.run_in_executor(
            None, 
            categorize_feedback, 
            feedback_text
        )
        
        # analysis_object is an instance of FeedbackAnalysis, convert to dict
        return analysis_object.__dict__
        
    except Exception as e:
        # Catch any errors during the LLM call or JSON parsing
        return {"error": f"Failed to analyze feedback: {e}"}

# --- Example Usage (for local testing) ---

if __name__ == '__main__':
    async def main():
        # Example 1: Trade Commentary
        mock_analysis = {
            "Symbol": "MSFT", 
            "Close": 420.50, 
            "Signal": "BUY", 
            "AI_Confidence": "85%", 
            "ai_comment": "SMA Crossover detected with low RSI, indicating strong bullish momentum."
        }
        comment = await generate_trade_comment(mock_analysis)
        print("\n--- Trade Commentary ---")
        print(comment)

        # Example 2: Feedback Analysis
        feedback = "The dashboard is great, but the colors clash and the daily reports are too slow. We need a way to filter stocks by sector."
        analysis = await analyze_feedback(feedback)
        print("\n--- Feedback Analysis ---")
        print(json.dumps(analysis, indent=2))

    if llm:
        # Only run if the LLM successfully initialized
        asyncio.run(main())
    else:
        print("\nSkipping examples because byLLM initialization failed.")
