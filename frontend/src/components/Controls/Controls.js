// src/components/Controls/Controls.js

import React from 'react';

function Controls({
    symbols,
    setSymbols,
    useMockData,
    setUseMockData,
    includeCommentary,
    setIncludeCommentary,
    handleRunAnalysis,
    loading
}) {
    return (
        <div className="controls-container" style={{ marginBottom: '30px', border: '1px solid #ddd', padding: '20px', borderRadius: '8px', backgroundColor: '#fafafa' }}>
            
            {/* Symbol Input */}
            <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '8px' }}>
                    Stock Symbols (Comma Separated)
                </label>
                <input
                    type="text"
                    className="input-field"
                    value={symbols}
                    onChange={(e) => setSymbols(e.target.value)}
                    placeholder="e.g., AAPL, TSLA, MSFT"
                    disabled={loading}
                />
            </div>
            
            {/* Toggles (Critical for Hackathon Demo) */}
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: '15px', marginBottom: '20px' }}>
                
                {/* Mock Data Toggle */}
                <div className="toggle-group" style={{ flex: 1 }}>
                    <input
                        type="checkbox"
                        id="mockDataToggle"
                        checked={useMockData}
                        onChange={() => setUseMockData(!useMockData)}
                        disabled={loading}
                    />
                    <label htmlFor="mockDataToggle" style={{ marginLeft: '8px', fontWeight: 'bold' }}>
                        Use Mock Data (Rapid Test Signals)
                    </label>
                </div>

                {/* LLM Commentary Toggle */}
                <div className="toggle-group" style={{ flex: 1 }}>
                    <input
                        type="checkbox"
                        id="commentaryToggle"
                        checked={includeCommentary}
                        onChange={() => setIncludeCommentary(!includeCommentary)}
                        disabled={loading}
                    />
                    <label htmlFor="commentaryToggle" style={{ marginLeft: '8px', fontWeight: 'bold' }}>
                        Include LLM Commentary (byLLM)
                    </label>
                </div>
            </div>

            {/* Run Button */}
            <button
                className="btn-primary"
                onClick={handleRunAnalysis}
                disabled={loading}
                style={{ width: '100%', padding: '12px', fontSize: '1.1em' }}
            >
                {loading ? 'ANALYZING...' : 'RUN QUANT ANALYSIS'}
            </button>
        </div>
    );
}

export default Controls;
