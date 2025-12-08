// src/components/HistoryExport/HistoryExport.js

import React from 'react';
import { downloadHistory } from '../../utils/api';

function HistoryExport() {
    return (
        <div style={{ border: '1px solid #ddd', padding: '20px', borderRadius: '8px', backgroundColor: '#fafafa' }}>
            <h3 style={{ color: '#0074D9', marginTop: 0 }}>💾 Export History</h3>
            <p style={{ fontSize: '0.9em', color: '#555', marginBottom: '20px' }}>
                Download all recorded trade analysis decisions (including rationale) for backtesting or auditing.
            </p>

            <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
                <button 
                    className="btn-primary" 
                    onClick={() => downloadHistory('csv')}
                >
                    Download as CSV
                </button>
                <button 
                    className="btn-primary" 
                    onClick={() => downloadHistory('xlsx')}
                >
                    Download as XLSX
                </button>
            </div>
        </div>
    );
}

export default HistoryExport;
