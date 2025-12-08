// src/hooks/useApi.js

import { useState, useCallback } from 'react';

/**
 * Custom hook to handle the state management for asynchronous API calls.
 * * @param {function} apiFunction - The asynchronous function that calls the backend (e.g., fetchMultiAnalysis).
 * @returns {object} - { data, error, loading, execute }
 */
const useApi = (apiFunction) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [data, setData] = useState(null);

    // useCallback memoizes the execute function, preventing unnecessary re-renders
    const execute = useCallback(async (...args) => {
        setLoading(true);
        setError(null);
        setData(null);
        
        try {
            // Execute the provided API function with its arguments
            const response = await apiFunction(...args);
            setData(response);
            return response; // Return data for components needing immediate access
        } catch (err) {
            const errorMessage = err.message || 'An unknown network error occurred.';
            setError(errorMessage);
            console.error("API Hook Error:", err);
            throw err; // Re-throw the error for component-level handling (e.g., showing alert)
        } finally {
            setLoading(false);
        }
    }, [apiFunction]); // Dependency array ensures the function updates if apiFunction changes

    return { data, error, loading, execute };
};

export default useApi;
