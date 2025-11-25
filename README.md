```
# HCO-Quant

📊 **HCO-Quant** is a full-stack AI-powered financial analysis platform that provides real-time stock signals, insights, and dashboards. The backend uses FastAPI and byLLM for AI-powered analysis, while the frontend uses React with Jac Client integration for seamless interaction.

---

## Features

- **Single Symbol Dashboard** – View AI-generated signals, confidence levels, and rationale for a single stock.
- **Multi-Symbol Dashboard** – Monitor multiple stocks in one view with AI commentary and visual insights.
- **Jac Client Integration** – Enables frontend to communicate with backend walkers via Spawn().
- **byLLM-powered AI** – Provides sentiment analysis, rationale, and signal generation.
- **Real-time Updates** – Automatic data refresh every 10 seconds for live trading signals.
- **Structured Code** – Organized React components, hooks, and services for maintainability.

---

## Folder Structure

```

HCO-Quant/
├── backend/               # FastAPI backend and AI pipelines
├── frontend/              # React frontend with Jac Client
│   ├── src/
│   │   ├── components/
│   │   │   ├── MultiSymbol.js
│   │   │   ├── SingleSymbol.js
│   │   │   └── TradeDashboard.js
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.js
│   │   └── index.js
├── .env                   # API keys
├── README.md
└── requirements.txt       # Python dependencies

````

---

## Setup Instructions

### Backend

1. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
````

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables in `.env` (e.g., `GEMINI_API_KEY`).
4. Start the FastAPI server:

   ```bash
   uvicorn hco_quant_api:app --reload
   ```

### Frontend

1. Navigate to frontend folder:

   ```bash
   cd frontend
   ```
2. Install dependencies:

   ```bash
   npm install
   ```
3. Start React development server:

   ```bash
   npm start
   ```
4. Open browser at `http://localhost:3000` to view the dashboard.

---

## Contributing

Feel free to open issues, submit pull requests, or improve documentation. Please follow standard Git workflow and commit message conventions.

---

## License

MIT License

---

## Contact

Henry Christian – [GitHub](https://github.com/henrychristiano7)

```

