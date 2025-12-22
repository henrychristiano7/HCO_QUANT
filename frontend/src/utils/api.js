// src/utils/api.js

import axios from 'axios';

// IMPORTANT: Ensure this URL matches your Uvicorn host/port configuration!
const API_BASE_URL = 'http://127.0.0.1:8000'; 

/**
 * Fetches multi-symbol analysis data from the backend pipeline.
 * @param {string} symbols - Comma-separated list of symbols (e.g., 'AAPL,TSLA').
 * @param {boolean} useMockData - Whether to use the mock data flag.
 * @param {boolean} includeCommentary - Whether to include LLM commentary.
 * @returns {Promise<Array<Object>>} - Array of analysis results.
 */
export const fetchMultiAnalysis = async ({ symbols, useMockData, includeCommentary }) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/analyze/multi`, {
            params: {
                symbols,
                use_mock_data: useMockData,
                include_commentary: includeCommentary,
            },
        });
        
        // CRITICAL: Extracts the list from the expected backend wrapper: {"symbols": [...]}.
        return response.data.symbols || []; 
        
    } catch (error) {
        console.error('Error fetching multi-analysis:', error.response ? error.response.data : error.message);
        throw new Error('Failed to fetch data. Check API status.');
    }
};

/**
 * Analyzes user feedback text using the LLM agent (POST request).
 * @param {string} feedbackText - The text provided by the user.
 * @returns {Promise<Object>} - Structured analysis (sentiment, category, summary).
 */
export const analyzeUserFeedback = async (feedbackText) => {
    try {
        // Sends the feedback text as a query parameter in a POST request, matching the FastAPI endpoint setup.
        const response = await axios.post(
            `${API_BASE_URL}/utility/feedback_analysis`, 
            null, // Body is null as data is sent via params
            {
                params: {
                    feedback: feedbackText 
                }
            }
        );
        return response.data;
    } catch (error) {
        console.error('Error analyzing feedback:', error.response ? error.response.data : error.message);
        throw new Error('Feedback analysis failed. Check API status and payload.');
    }
};

/**
 * Checks a hash or URL against the Threat Intel Agent (VirusTotal).
 */
export const fetchThreatReport = async ({ checkValue, checkType }) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/utility/threat_intel`, {
            params: {
                check_value: checkValue,
                check_type: checkType,
            },
        });
        
        // Simplification: Extracts security statistics
        const stats = response.data.data.attributes.last_analysis_stats;
        const isMalicious = stats.malicious > 0 || stats.suspicious > 0;
        
        return { 
            isMalicious,
            reportUrl: `https://www.virustotal.com/${checkType}/${checkValue}`,
            maliciousCount: stats.malicious,
        };
    } catch (error) {
        console.error('Error fetching threat report:', error);
        throw new Error('Threat Intel API failed (Key/Quota issue).');
    }
};

/**
 * Triggers a download for the history file.
 */
export const downloadHistory = (formatType) => {
    window.open(`${API_BASE_URL}/export/history/${formatType}`, '_blank');
};
