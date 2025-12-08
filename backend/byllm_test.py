# byllm_test.py

from byllm.lib import Model, by
from dataclasses import dataclass
import os
import sys

# --- 1. Define Structured Output ---
@dataclass
class TestResult:
    summary: str
    status: str

# --- 2. Define the LLM Function ---
try:
    # Initialize the model client (It requires GEMINI_API_KEY to be set)
    llm_model = Model(model_name="gemini-2.5-flash")

    @by(llm_model)
    def analyze_backend_status(code_language: str) -> TestResult:
        """
        Analyze a backend stack and provide a simple status report. 
        Focus on structure and function confirmation.
        """
        pass

except Exception as e:
    # If initialization fails (e.g., API Key missing)
    print("--- ❌ Initialization FAILED ---")
    print(f"Error: Could not initialize byLLM Model. Check GEMINI_API_KEY.")
    print(f"Detail: {e}")
    sys.exit(1)


# --- 3. Run the Test ---
print("--- ✅ byLLM Initialization SUCCESSFUL ---")
print("Attempting to execute LLM function...")

try:
    # Execute the LLM-powered function call
    result = analyze_backend_status(code_language="Python, FastAPI, and byLLM")
    
    print("\n--- ✅ byLLM Execution SUCCESSFUL ---")
    print(f"Status: {result.status}")
    print(f"Summary: {result.summary}")
    print(f"\nFinal Check: byLLM is fully operational.")

except Exception as e:
    print("\n--- ❌ byLLM Execution FAILED ---")
    print(f"Error: LLM function crashed during execution.")
    print(f"Detail: {e}")
    print("Reason: Often due to concurrency issues or API errors (e.g., rate limit).")
