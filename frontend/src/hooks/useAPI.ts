/**
 * Custom hook for managing API call state.
 * 
 * This hook provides a consistent interface for handling API calls
 * with loading, error, and success states.
 */

import { useState, useCallback } from 'react';
import type { ApiState } from '../types/api';

/**
 * Hook for managing API call state with loading and error handling.
 * 
 * @template T - Type of the API response data
 * @returns Object with state and execute function
 */
export function useAPI<T>() {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  /**
   * Execute an API call and manage its state.
   * 
   * @param apiCall - Async function that makes the API call
   * @returns Promise resolving to the API response data
   */
  const execute = useCallback(async (apiCall: () => Promise<T>): Promise<T | null> => {
    setState({ data: null, loading: true, error: null });

    try {
      const data = await apiCall();
      setState({ data, loading: false, error: null });
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
      setState({ data: null, loading: false, error: errorMessage });
      return null;
    }
  }, []);

  /**
   * Reset the state to initial values.
   */
  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  /**
   * Clear only the error state.
   */
  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    execute,
    reset,
    clearError,
  };
}

/**
 * Hook for managing multiple API calls with individual state tracking.
 * 
 * @template T - Type of the API response data
 * @returns Object with state map and execute function
 */
export function useMultiAPI<T>() {
  const [states, setStates] = useState<Record<string, ApiState<T>>>({});

  /**
   * Execute an API call with a specific key for state tracking.
   * 
   * @param key - Unique key for this API call
   * @param apiCall - Async function that makes the API call
   * @returns Promise resolving to the API response data
   */
  const execute = useCallback(
    async (key: string, apiCall: () => Promise<T>): Promise<T | null> => {
      setStates((prev) => ({
        ...prev,
        [key]: { data: null, loading: true, error: null },
      }));

      try {
        const data = await apiCall();
        setStates((prev) => ({
          ...prev,
          [key]: { data, loading: false, error: null },
        }));
        return data;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
        setStates((prev) => ({
          ...prev,
          [key]: { data: null, loading: false, error: errorMessage },
        }));
        return null;
      }
    },
    []
  );

  /**
   * Get the state for a specific key.
   * 
   * @param key - Key to get state for
   * @returns API state for the key
   */
  const getState = useCallback(
    (key: string): ApiState<T> => {
      return states[key] || { data: null, loading: false, error: null };
    },
    [states]
  );

  /**
   * Reset state for a specific key.
   * 
   * @param key - Key to reset
   */
  const reset = useCallback((key: string) => {
    setStates((prev) => {
      const newStates = { ...prev };
      delete newStates[key];
      return newStates;
    });
  }, []);

  /**
   * Reset all states.
   */
  const resetAll = useCallback(() => {
    setStates({});
  }, []);

  return {
    states,
    execute,
    getState,
    reset,
    resetAll,
  };
}
