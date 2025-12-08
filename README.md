📊 HCO Quant AI Platform: Agentic Financial & Threat Intelligence Dashboard
🌟 Project Overview
HCO Quant is a high-performance, agentic platform that provides real-time quantitative trading signals alongside human-readable AI commentary and integrates Threat Intelligence for robust security awareness. Built for speed and modularity, the system uses concurrent processing to analyze multiple stock symbols (ETFs, Stocks, etc.) and generate actionable insights in seconds.

The project demonstrates the stable integration of mandatory hackathon technologies (Jac ecosystem via byLLM) with production-grade backend and frontend frameworks.

🚀 Key Features
Concurrent Quant Analysis: Asynchronously processes signals for multiple symbols simultaneously, drastically reducing latency.

AI Commentary (Powered by byLLM): Generates natural language insights and rationale for every trading signal, providing context beyond raw metrics.

Financial Data Agent: Fetches historical OHLCV data for analysis (or uses Mock Data for testing).

Threat Intelligence Integration: A dedicated API endpoint integrates with VirusTotal via a dedicated agent to check the safety of URLs or file hashes.

Flexible Data Toggles: Frontend switches allow users to easily toggle between Mock Data (for fast testing) and Real Data, and to enable/disable the resource-intensive LLM Commentary.

💻 Tech Stack
Component	Technology	Role	Compliance
Agentic Logic	byLLM (Built on Jac)	Orchestration of complex LLM calls and structured output generation.	MANDATORY
Backend API	FastAPI (Python 3.12)	High-performance, asynchronous server handling concurrency.	
Concurrency	asyncio (Python 3.12)	Enables non-blocking, simultaneous execution of multiple symbol analyses.	
Frontend UI	React & Vite	Fast, modern, and interactive dashboard for visualizing results.	
Database	SQLite	Local database for storing the trade_history log.	

Export to Sheets

⚙️ Installation and Setup
1. Backend Setup
The backend requires Python 3.10+ and uses a virtual environment (venv).

Bash

# Navigate to the backend directory
cd ~/HCO-Quant/backend

# Create and activate the virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (ensure requirements.txt is up-to-date)
pip install -r requirements.txt

# Create the initial database file
python -c 'from src.database import setup_db; setup_db()'
Environment Variables (.env file)
You must create a .env file in the ~/HCO-Quant/backend directory with your API keys:

Bash

# .env
# Required for LLM Commentary
GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"

# Required for Threat Intel Agent
VIRUSTOTAL_API_KEY="YOUR_VIRUSTOTAL_API_KEY_HERE"
2. Run the Backend
Start the FastAPI server using Uvicorn:

Bash

# (Ensure venv is active)
uvicorn src.api.hco_quant_api:app --host 127.0.0.1 --port 8000
3. Frontend Setup
The frontend uses Node.js and npm.

Bash

# Navigate to the frontend directory
cd ~/HCO-Quant/frontend

# Install Node dependencies
npm install

# Run the frontend development server
npm run dev
The application will be accessible at http://localhost:3000.

👨‍💻 Usage and Endpoints
The core interaction happens through the frontend dashboard at http://localhost:3000.

Core API Endpoints (Backend)
Method	Endpoint	Description
GET	/analyze/multi	Runs the full concurrent analysis pipeline for multiple symbols.
GET	/utility/threat_intel	Queries VirusTotal for URL or file hash safety data.
GET	/export/history/xlsx	Downloads the full trade history log as an Excel file.
GET	/docs	OpenAPI documentation (Swagger UI).

Export to Sheets

Demo Instructions
Open the dashboard in your browser.

Initial Run: Ensure "Use Mock Data" and "Include LLM Commentary" are checked. Click "RUN QUANT ANALYSIS". This should complete quickly and demonstrate both the signal generation and the LLM output.

Real Data Showcase: Uncheck "Use Mock Data" and run again. This demonstrates the stability of the concurrent API calls under real-world latency.

Threat Intel: Paste a known malicious hash (e.g., 51a24d8641470e28f352109869a25b290196230f) into the Threat Checker and scan it to show the agent's detection capabilities.
