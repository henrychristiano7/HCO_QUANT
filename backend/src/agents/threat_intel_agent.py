# src/agents/threat_intel_agent.py

import os
import requests
import base64
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# --- Configuration & Setup ---
load_dotenv()
VT_API_KEY = os.getenv("VT_API_KEY")

# Use a specific exception for clearer error handling
class VTAPIError(Exception):
    pass

def _get_vt_headers() -> Dict[str, str]:
    """Ensures API key is available and returns standard headers."""
    if not VT_API_KEY:
        # Use the custom exception
        raise VTAPIError("VirusTotal API key not configured (VT_API_KEY missing).")
    return {"x-apikey": VT_API_KEY}

def _handle_vt_response(response: requests.Response) -> Dict[str, Any]:
    """Standardized handler for VirusTotal API response."""
    if response.status_code == 200:
        return response.json()
    
    # Raise an exception instead of returning an error dictionary
    raise VTAPIError(f"VirusTotal API error (Status {response.status_code}): {response.text}")

# --- Core VirusTotal Functions ---

def get_vt_file_report(file_hash: str) -> Dict[str, Any]:
    """
    Queries VirusTotal for a file hash report (MD5, SHA1, or SHA256).
    
    Args:
        file_hash: The hash of the file to check.
    Returns:
        The full JSON report from VirusTotal.
    """
    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    headers = _get_vt_headers()
    response = requests.get(url, headers=headers)
    return _handle_vt_response(response)

def get_vt_url_report(url_to_check: str) -> Dict[str, Any]:
    """
    Queries VirusTotal for a URL report.
    
    Args:
        url_to_check: The URL string to analyze.
    Returns:
        The full JSON report from VirusTotal.
    """
    # VirusTotal API uses a base64-encoded URL ID for GET requests
    url_id = base64.urlsafe_b64encode(url_to_check.encode()).decode().strip("=")
    
    vt_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
    headers = _get_vt_headers()
    response = requests.get(vt_url, headers=headers)
    
    return _handle_vt_response(response)

# --- Example Usage ---
if __name__ == '__main__':
    print("\n--- Threat Intel Agent Test (Requires VT_API_KEY in .env) ---")
    
    # Example Hash (A non-malicious Google hash)
    test_hash = "275a560c50f83737b027d1421a71fb981f9b9dae" 
    
    try:
        file_report = get_vt_file_report(test_hash)
        print(f"Report for hash {test_hash[:10]}...: Success (Status: {file_report['data']['attributes']['last_analysis_stats']['malicious']} malicious)")
        
        # Example URL
        url_report = get_vt_url_report("https://www.google.com")
        print(f"Report for URL: Success (Status: {url_report['data']['attributes']['last_analysis_stats']['malicious']} malicious)")
        
    except VTAPIError as e:
        print(f"VT API Configuration/Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
