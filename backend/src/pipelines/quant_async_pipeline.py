# src/pipelines/quant_async_pipeline.py

import asyncio
import random
import datetime
import pandas as pd
from typing import List, Dict, Any, Union

# Import external components from the 'src' package
from src.agents import report_agent
from src.agents import strategy_agent
from src.agents import financial_data_agent 
from src.utils import mock_data 
from src.agents import ai_agent # CRITICAL: Need AI Agent here to generate commentary

# ----------------------------------------------------------------------
# Async Pipeline Step: Process Single Asset
# ----------------------------------------------------------------------

async def process_asset_pipeline(symbol: str, use_mock_data: bool = False, include_commentary: bool = False) -> Dict[str, Any]:
    """
    Asynchronously executes the full quantitative analysis pipeline for one symbol.
    1. Fetches data (real or mock).
    2. Computes the signal.
    3. Generates LLM commentary (if requested).
    4. Saves the complete entry to history.
    
    Args:
        symbol: The stock ticker symbol.
        use_mock_data: If True, uses randomized mock data.
        include_commentary: If True, calls the AI agent for detailed commentary.
        
    Returns:
        A dictionary containing the complete signal data.
    """
    
    # Simulate network/database latency if using real data
    if not use_mock_data:
        await asyncio.sleep(random.uniform(0.05, 0.25))
    
    # 1. FETCH Data (Conditional Logic)
    if use_mock_data:
        # Use mock data utility for dynamic, randomized testing. 
        historical_df_result = mock_data.generate_mock_ohlcv(symbol, days=60, interval_hours=6)
    else:
        # Use the real financial data agent
        historical_df_result = financial_data_agent.get_historical_data(symbol)

    # Handle data fetching errors
    if isinstance(historical_df_result, dict):
        return {
            "Symbol": symbol.upper(),
            "Close": 0.0,
            "Signal": "ERROR",
            "AI_Confidence": "0%",
            "ai_comment": historical_df_result.get('error', 'Data Fetch Failed.'),
            "Last_Updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_source": "MOCK" if use_mock_data else "REAL_FAIL",
        }

    historical_df = historical_df_result

    # 2. COMPUTE Signal (using the Strategy Agent)
    signal_data = strategy_agent.generate_latest_signal(historical_df)

    # Assemble base data fields
    symbol_upper = symbol.upper()
    signal_data['Symbol'] = symbol_upper
    signal_data['data_source'] = "MOCK" if use_mock_data else "REAL"

    # 3. GENERATE LLM Commentary (CRITICAL STEP)
    if include_commentary:
        # The AI agent is called here, ensuring the data is added before reporting
        try:
            llm_commentary = await ai_agent.generate_trade_comment(signal_data)
            signal_data['llm_commentary'] = llm_commentary
        except Exception as e:
            signal_data['llm_commentary_error'] = f"LLM generation failed: {e.__class__.__name__}"
    
    # 4. LOG Decision (using the Report Agent)
    # The signal_data dictionary now contains ALL fields (including llm_commentary, if generated)
    history_entry = report_agent.process_latest_signal(symbol_upper, signal_data)
    report_agent.save_history_entry(history_entry)

    # 5. Return the enriched data
    return signal_data 

# ----------------------------------------------------------------------
# Main HTML Generation Pipeline Function
# ----------------------------------------------------------------------

async def generate_dashboard_html(symbols: str, use_mock_data: bool = False, include_commentary: bool = False) -> str:
    """
    Orchestrates the asynchronous execution for multiple symbols and formats 
    the results into an HTML dashboard.
    """
    # 1. Setup Tasks
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    
    # Pass all flags to the individual asset tasks
    tasks = [process_asset_pipeline(
        sym, 
        use_mock_data=use_mock_data, 
        include_commentary=include_commentary
    ) for sym in symbol_list]
    
    # 2. Execute Tasks Concurrently
    results = await asyncio.gather(*tasks)

    # 3. Generate HTML
    html = generate_html_template(results)
    return html

# ----------------------------------------------------------------------
# HTML Rendering Function (Decoupled for clarity)
# ----------------------------------------------------------------------

def generate_html_template(results: List[Dict[str, Any]]) -> str:
    """Creates the HTML string from the analysis results."""
    def get_color(signal):
        if signal == "BUY": return "green"
        if signal == "SELL": return "red"
        return "gray"

    html = f"""
    <html>
    <head>
        <title>📊 Multi-Symbol Quant Dashboard</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #f4f7fb; color:#333; text-align:center; padding:30px; }}
            h1 {{ color:#0074D9; margin-bottom:20px; }}
            table {{ border-collapse: separate; border-spacing: 0; margin:20px auto; width:95%; box-shadow:0 5px 15px rgba(0,0,0,0.1); border-radius:12px; overflow:hidden; }}
            th, td {{ padding:12px 15px; border:1px solid #ddd; text-align:center; }}
            th {{ background-color:#0074D9; color:white; text-shadow:0 0 4px rgba(0,255,255,0.4); }}
            tr:nth-child(even) {{ background-color:#f9f9f9; }}
            .green {{ color:#00c853; font-weight:bold; text-shadow:0 0 6px rgba(0,200,83,0.5); }}
            .red {{ color:#d50000; font-weight:bold; text-shadow:0 0 6px rgba(213,0,0,0.5); }}
            .gray {{ color:#888; font-weight:bold; }}
            .ai-comment {{ font-style:italic; font-size:0.9rem; margin-top:5px; }}
            .timestamp {{ margin-top:10px; font-size:14px; color:#555; }}
            tr:hover {{ background-color: rgba(0, 120, 255, 0.05); }}
        </style>
    </head>
    <body>
        <h1>📊 Multi-Symbol Quant Dashboard (AI-powered)</h1>
        <div class="timestamp">Last Run: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        <table>
            <tr>
                <th>Symbol</th>
                <th>Close ($)</th>
                <th>Signal</th>
                <th>AI Confidence</th>
                <th>Quant Rationale</th>
                <th>LLM Commentary</th>
                <th>Data Source</th>
            </tr>
    """

    for d in results:
        color_class = get_color(d.get('Signal'))
        
        # Pull data, defaulting to ensure no NameErrors in the HTML loop
        symbol = d.get('Symbol', 'N/A')
        close = d.get('Close', 'N/A')
        signal = d.get('Signal', 'HOLD')
        confidence = d.get('AI_Confidence', '0%')
        
        # Display either the full LLM commentary or the error message/empty
        llm_text = d.get('llm_commentary', '') or d.get('llm_commentary_error', '') or 'N/A (Not Requested)'
        
        # Use the shorter, emoji-based quant rationale for the table display
        quant_rationale = d.get('ai_comment', 'No Comment')
        source = d.get('data_source', 'N/A')

        html += f"""
            <tr>
                <td>{symbol}</td>
                <td>{close}</td>
                <td class="{color_class}">{signal}</td>
                <td>{confidence}</td>
                <td class="ai-comment">{quant_rationale}</td>
                <td class="ai-comment">{llm_text}</td>
                <td>{source}</td>
            </tr>
        """

    html += "</table></body></html>"
    return html
