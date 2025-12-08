// src/components/Dashboard/Dashboard.js

import React, { useState } from 'react';
import Controls from '../Controls/Controls';
import QuantTable from '../QuantTable/QuantTable';
import ThreatChecker from '../ThreatChecker/ThreatChecker';
import HistoryExport from '../HistoryExport/HistoryExport';
import { fetchMultiAnalysis } from '../../utils/api';

function Dashboard() {
    // State to hold analysis results for the table
    const [analysisResults, setAnalysisResults] = useState([]);
    // State for controls/input
    const [symbols, setSymbols] = useState('AAPL, TSLA, MSFT');
    const [useMockData, setUseMockData] = useState(true); // Default to mock for fast demo
    const [includeCommentary, setIncludeCommentary] = useState(true);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleRunAnalysis = async () => {
        if (!symbols.trim()) {
            setError("Please enter at least one stock symbol.");
            return;
        }

        setLoading(true);
        setError(null);
        setAnalysisResults([]);

        try {
            // Call the backend API
            const data = await fetchMultiAnalysis({ 
                symbols, 
                useMockData, 
                includeCommentary 
            });
            setAnalysisResults(data);
        } catch (err) {
            setError(err.message || "An unknown error occurred during analysis.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="dashboard">
            {/* 1. Controls Section */}
            <Controls
                symbols={symbols}
                setSymbols={setSymbols}
                useMockData={useMockData}
                setUseMockData={setUseMockData}
                includeCommentary={includeCommentary}
                setIncludeCommentary={setIncludeCommentary}
                handleRunAnalysis={handleRunAnalysis}
                loading={loading}
            />

            {/* 2. Results and Error Display */}
            <div style={{ marginTop: '20px' }}>
                {loading && <p style={{ color: '#0074D9', fontWeight: 'bold' }}>Running analysis... Please wait. (Timeout is 180s for real data)</p>}
                {error && <p style={{ color: 'red', fontWeight: 'bold' }}>Error: {error}</p>}
                
                {analysisResults.length > 0 && (
                    <QuantTable results={analysisResults} />
                )}
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: '30px', marginTop: '40px' }}>
                {/* 3. Threat Intelligence Checker */}
                <div style={{ width: '45%' }}>
                    <ThreatChecker />
                </div>
                
                {/* 4. History Export */}
                <div style={{ width: '45%' }}>
                    <HistoryExport />
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
