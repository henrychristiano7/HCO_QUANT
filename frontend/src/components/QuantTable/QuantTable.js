// src/components/QuantTable/QuantTable.js

import React from 'react';
import './QuantTable.css'; // We'll assume a dedicated CSS file for table styles

function QuantTable({ results }) {
    if (results.length === 0) return null;

    return (
        <div className="quant-table-container">
            <h3 style={{ color: '#0074D9', marginBottom: '15px' }}>
                Multi-Symbol Quant Dashboard ({results[0].data_source} Data)
            </h3>
            
            <table className="quant-table">
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Close ($)</th>
                        <th>Signal</th>
                        <th>Confidence</th>
                        <th>Quant Rationale</th>
                        <th>LLM Commentary</th>
                        <th>Data Source</th>
                    </tr>
                </thead>
                <tbody>
                    {results.map((data, index) => {
                        // Determine the CSS class based on the actual signal value
                        const signalClass = data.Signal === 'BUY' ? 'green' : data.Signal === 'SELL' ? 'red' : 'gray';

                        // Check for LLM errors to display a warning
                        const llmText = data.llm_commentary || data.llm_commentary_error || 'N/A';
                        
                        // Safely format the Close Price (React will handle this, but ensuring string conversion for safety)
                        const closePrice = data.Close !== 'N/A' && data.Close !== 0 ? data.Close.toFixed(2) : 'N/A';
                        
                        return (
                            <tr key={index}>
                                <td><strong>{data.Symbol}</strong></td>
                                <td>{closePrice}</td>
                                <td className={`signal-cell ${signalClass}`}>
                                    <strong>{data.Signal}</strong>
                                </td>
                                <td>{data.AI_Confidence}%</td>
                                <td className="rationale-cell">{data.ai_comment}</td>
                                <td className="commentary-cell">
                                    {data.llm_commentary_error ? 
                                        <span style={{ color: 'orange', fontStyle: 'italic' }}>{llmText}</span> :
                                        llmText
                                    }
                                </td>
                                <td>{data.data_source}</td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
}

export default QuantTable;
