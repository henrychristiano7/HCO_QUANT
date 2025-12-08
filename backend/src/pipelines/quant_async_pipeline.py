# src/pipelines/quant_async_pipeline.py (FINAL COMPLETE VERSION - Syntax Fix)

import asyncio
import random
import datetime
import pandas as pd
from typing import List, Dict, Any, Union
import numpy as np # Added for robust type checking/conversion in HTML rendering

# Import external components from the 'src' package
from src.agents import report_agent
from src.agents import strategy_agent
from src.agents import financial_data_agent 
from src.utils import mock_data 
from src.agents import ai_agent 

# ----------------------------------------------------------------------
# Async Pipeline Step: Process Single Asset
# ----------------------------------------------------------------------

async def process_asset_pipeline(symbol: str, use_mock_data: bool = False, include_commentary: bool = False) -> Dict[str, Any]:
    """
    Asynchronously executes the full quantitative analysis pipeline for one symbol.
    """
    
    # Simulate network/database latency if using real data
    if not use_mock_data:
        await asyncio.sleep(random.uniform(0.05, 0.25))
    
    # 1. FETCH Data (Conditional Logic)
    if use_mock_data:
        historical_df_result = mock_data.generate_mock_ohlcv(symbol, days=60, interval_hours=6)
    else:
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

    # 3. GENERATE LLM Commentary (Concurrency Fix applied)
    if include_commentary:
        
        # Extract primitive arguments for the thread-safe synchronous call
        symbol_arg = signal_data.get('Symbol')
        signal_arg = signal_data.get('action') # Use 'action' for the signal value
        confidence_arg = signal_data.get('AI_Confidence') 
        rationale_arg = signal_data.get('ai_comment')
        close_arg = signal_data.get('latest_close')
        
        try:
            # FIX: Use asyncio.to_thread to run the synchronous ai_agent function.
            llm_commentary = await asyncio.to_thread(
                ai_agent.generate_trade_comment, 
                symbol_arg,
                signal_arg,
                confidence_arg,
                rationale_arg,
                close_arg
            )
            signal_data['llm_commentary'] = llm_commentary
            
        except Exception as e:
            # Capture the error gracefully
            signal_data['llm_commentary_error'] = f"LLM generation failed: {e.__class__.__name__}"
    
    # 4. LOG Decision (using the Report Agent)
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
    """Creates the HTML string from the analysis results, applying necessary formatting."""
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
        # PULL CORRECT SIGNAL: Fixes the 'stuck on HOLD' bug
        signal = d.get('action', 'HOLD')
        color_class = get_color(signal)
        
        # Pull data
        symbol = d.get('Symbol', 'N/A')
        confidence = d.get('AI_Confidence', '0%')
        
        # CRITICAL FIX: Robustly format the 'Close' price
        close_value = d.get('latest_close') # Use 'latest_close' key from the strategy agent output
        try:
            # Use float() to convert ANY numeric type (Python or NumPy) to a standard float
            close = f"{float(close_value):.2f}"
        except Exception:
            close = 'N/A' # Default if conversion fails
            
        # Display either the full LLM commentary or the error message/empty
        llm_text = d.get('llm_commentary', '') or d.get('llm_commentary_error', '') or 'N/A (Not Requested)'
        
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
