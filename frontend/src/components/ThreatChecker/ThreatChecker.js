// src/components/ThreatChecker/ThreatChecker.js

import React, { useState } from 'react';
import { fetchThreatReport } from '../../utils/api';

function ThreatChecker() {
    const [checkValue, setCheckValue] = useState('');
    const [checkType, setCheckType] = useState('url');
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleCheckThreat = async () => {
        if (!checkValue.trim()) return;

        setLoading(true);
        setError(null);
        setReport(null);

        try {
            const reportData = await fetchThreatReport({ checkValue, checkType });
            setReport(reportData);
        } catch (err) {
            setError(err.message || 'Threat check failed.');
        } finally {
            setLoading(false);
        }
    };

    const StatusDisplay = ({ isMalicious, maliciousCount, reportUrl }) => {
        const color = isMalicious ? '#d50000' : '#00c853';
        const statusText = isMalicious 
            ? `⚠️ DANGER: ${maliciousCount} scanner(s) flagged this.` 
            : `✅ SAFE: No malicious detections found.`;

        return (
            <div style={{ padding: '15px', border: `2px solid ${color}`, borderRadius: '6px', marginTop: '15px' }}>
                <p style={{ color, fontWeight: 'bold', margin: '0' }}>{statusText}</p>
                <a href={reportUrl} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.9em', color: '#0074D9' }}>View Full VirusTotal Report</a>
            </div>
        );
    };

    return (
        <div style={{ border: '1px solid #ddd', padding: '20px', borderRadius: '8px', backgroundColor: '#fafafa' }}>
            <h3 style={{ color: '#0074D9', marginTop: 0 }}>🛡️ Threat Intelligence Check</h3>
            <p style={{ fontSize: '0.9em', color: '#555' }}>Query hashes or URLs against VirusTotal (Free Tier).</p>

            {/* Input and Type Selector */}
            <div style={{ marginBottom: '15px', display: 'flex', gap: '10px' }}>
                <select 
                    value={checkType} 
                    onChange={(e) => setCheckType(e.target.value)}
                    className="input-field"
                    style={{ width: '30%', minWidth: '100px' }}
                    disabled={loading}
                >
                    <option value="url">URL</option>
                    <option value="hash">Hash (SHA256/MD5)</option>
                </select>
                <input
                    type="text"
                    className="input-field"
                    value={checkValue}
                    onChange={(e) => setCheckValue(e.target.value)}
                    placeholder={`Enter ${checkType.toUpperCase()} or file hash...`}
                    style={{ flexGrow: 1 }}
                    disabled={loading}
                />
            </div>

            <button 
                className="btn-primary" 
                onClick={handleCheckThreat}
                disabled={loading}
                style={{ width: '100%' }}
            >
                {loading ? 'SCANNING...' : 'RUN SECURITY SCAN'}
            </button>

            {/* Report Output */}
            {error && <p style={{ color: 'red', marginTop: '15px' }}>{error}</p>}
            {report && (
                <StatusDisplay 
                    isMalicious={report.isMalicious}
                    maliciousCount={report.maliciousCount}
                    reportUrl={report.reportUrl}
                />
            )}
        </div>
    );
}

export default ThreatChecker;
