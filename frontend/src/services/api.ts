/**
 * API client service for communicating with the FastAPI backend.
 * 
 * This module provides a centralized interface for all API calls,
 * with proper error handling, type safety, and response validation.
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  PuzzleGenerateRequest,
  PuzzleGenerateResponse,
  SolvePuzzleRequest,
  SolveResponse,
  SolveWordRequest,
  HintRequest,
  HintResponse,
  ValidateRequest,
  ValidateResponse,
  ErrorResponse,
  ApiConfig,
} from '../types/api';
import type { Puzzle } from '../types/puzzle';

/**
 * Default API configuration.
 */
const DEFAULT_CONFIG: ApiConfig = {
  baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 120000, // 2 minutes for puzzle generation
  headers: {
    'Content-Type': 'application/json',
  },
};

/**
 * API client class for making requests to the backend.
 */
class ApiClient {
  private client: AxiosInstance;

  constructor(config: ApiConfig = DEFAULT_CONFIG) {
    this.client = axios.create({
      baseURL: config.baseUrl,
      timeout: config.timeout,
      headers: config.headers,
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ErrorResponse>) => {
        return Promise.reject(this.handleError(error));
      }
    );
  }

  /**
   * Handle API errors and convert to user-friendly messages.
   */
  private handleError(error: AxiosError<ErrorResponse>): Error {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.message || error.message;
      return new Error(`API Error: ${message}`);
    } else if (error.request) {
      // Request made but no response received
      return new Error('Network Error: Unable to reach the server. Please check your connection.');
    } else {
      // Something else happened
      return new Error(`Request Error: ${error.message}`);
    }
  }

  /**
   * Generate a new crossword puzzle.
   * 
   * @param request - Puzzle generation parameters
   * @returns Promise resolving to puzzle generation response
   */
  async generatePuzzle(request: PuzzleGenerateRequest): Promise<PuzzleGenerateResponse> {
    const response = await this.client.post<PuzzleGenerateResponse>(
      '/api/puzzles/generate',
      request
    );
    return response.data;
  }

  /**
   * Get a puzzle by ID.
   * 
   * @param puzzleId - Unique puzzle identifier
   * @returns Promise resolving to puzzle data
   */
  async getPuzzle(puzzleId: string): Promise<Puzzle> {
    const response = await this.client.get<Puzzle>(`/api/puzzles/${puzzleId}`);
    return response.data;
  }

  /**
   * List all puzzles.
   * 
   * @returns Promise resolving to array of puzzles
   */
  async listPuzzles(): Promise<Puzzle[]> {
    const response = await this.client.get<Puzzle[]>('/api/puzzles/');
    return response.data;
  }

  /**
   * Solve entire puzzle using AI.
   * 
   * @param puzzleId - Unique puzzle identifier
   * @param request - Solve options
   * @returns Promise resolving to solve response
   */
  async solvePuzzle(
    puzzleId: string,
    request: SolvePuzzleRequest = {}
  ): Promise<SolveResponse> {
    const response = await this.client.post<SolveResponse>(
      `/api/puzzles/${puzzleId}/solve`,
      request
    );
    return response.data;
  }

  /**
   * Solve a specific word using AI.
   * 
   * @param puzzleId - Unique puzzle identifier
   * @param request - Word solve request
   * @returns Promise resolving to solve response
   */
  async solveWord(puzzleId: string, request: SolveWordRequest): Promise<SolveResponse> {
    const response = await this.client.post<SolveResponse>(
      `/api/puzzles/${puzzleId}/solve-word`,
      request
    );
    return response.data;
  }

  /**
   * Get a hint for a specific word.
   * 
   * @param puzzleId - Unique puzzle identifier
   * @param request - Hint request
   * @returns Promise resolving to hint response
   */
  async getHint(puzzleId: string, request: HintRequest): Promise<HintResponse> {
    const response = await this.client.post<HintResponse>(
      `/api/puzzles/${puzzleId}/hint`,
      request
    );
    return response.data;
  }

  /**
   * Validate user's solution.
   * 
   * @param puzzleId - Unique puzzle identifier
   * @param request - Validation request with user's cells
   * @returns Promise resolving to validation response
   */
  async validateSolution(
    puzzleId: string,
    request: ValidateRequest
  ): Promise<ValidateResponse> {
    const response = await this.client.post<ValidateResponse>(
      `/api/puzzles/${puzzleId}/validate`,
      request
    );
    return response.data;
  }

  /**
   * Delete a puzzle.
   * 
   * @param puzzleId - Unique puzzle identifier
   * @returns Promise resolving when deletion is complete
   */
  async deletePuzzle(puzzleId: string): Promise<void> {
    await this.client.delete(`/api/puzzles/${puzzleId}`);
  }
}

/**
 * Singleton instance of the API client.
 */
export const apiClient = new ApiClient();

/**
 * Export the ApiClient class for testing purposes.
 */
export { ApiClient };
