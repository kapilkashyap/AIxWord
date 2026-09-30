/**
 * Utility functions for input validation and data sanitization.
 */

/**
 * Validate that a string is a single uppercase letter.
 * 
 * @param input - Input string to validate
 * @returns True if input is a single uppercase letter
 */
export function isValidLetter(input: string): boolean {
  return /^[A-Z]$/.test(input);
}

/**
 * Sanitize user input to uppercase letter or null.
 * 
 * @param input - Raw input string
 * @returns Uppercase letter or null if invalid
 */
export function sanitizeLetter(input: string): string | null {
  const trimmed = input.trim().toUpperCase();
  return isValidLetter(trimmed) ? trimmed : null;
}

/**
 * Validate topic string for puzzle generation.
 * 
 * @param topic - Topic string to validate
 * @returns Object with isValid flag and error message
 */
export function validateTopic(topic: string): { isValid: boolean; error: string | null } {
  const trimmed = topic.trim();

  if (trimmed.length === 0) {
    return { isValid: false, error: 'Topic cannot be empty' };
  }

  if (trimmed.length < 2) {
    return { isValid: false, error: 'Topic must be at least 2 characters' };
  }

  if (trimmed.length > 100) {
    return { isValid: false, error: 'Topic must be less than 100 characters' };
  }

  // Check for valid characters (letters, numbers, spaces, basic punctuation)
  if (!/^[a-zA-Z0-9\s\-_,.'&]+$/.test(trimmed)) {
    return { isValid: false, error: 'Topic contains invalid characters' };
  }

  return { isValid: true, error: null };
}

/**
 * Validate grid size.
 * 
 * @param size - Grid size to validate
 * @returns Object with isValid flag and error message
 */
export function validateGridSize(size: number): { isValid: boolean; error: string | null } {
  if (!Number.isInteger(size)) {
    return { isValid: false, error: 'Grid size must be an integer' };
  }

  if (size < 4) {
    return { isValid: false, error: 'Grid size must be at least 4' };
  }

  if (size > 20) {
    return { isValid: false, error: 'Grid size must be at most 20' };
  }

  return { isValid: true, error: null };
}

/**
 * Validate word count range.
 * 
 * @param minWords - Minimum word count
 * @param maxWords - Maximum word count
 * @returns Object with isValid flag and error message
 */
export function validateWordCount(
  minWords: number,
  maxWords: number
): { isValid: boolean; error: string | null } {
  if (!Number.isInteger(minWords) || !Number.isInteger(maxWords)) {
    return { isValid: false, error: 'Word counts must be integers' };
  }

  if (minWords < 4) {
    return { isValid: false, error: 'Minimum words must be at least 4' };
  }

  if (minWords > maxWords) {
    return { isValid: false, error: 'Minimum words cannot exceed maximum words' };
  }

  return { isValid: true, error: null };
}

/**
 * Check if a key press is a letter key.
 * 
 * @param key - Key from keyboard event
 * @returns True if key is a letter
 */
export function isLetterKey(key: string): boolean {
  return /^[a-zA-Z]$/.test(key);
}

/**
 * Check if a key press is a navigation key.
 * 
 * @param key - Key from keyboard event
 * @returns True if key is a navigation key
 */
export function isNavigationKey(key: string): boolean {
  return ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Tab', 'Enter'].includes(key);
}

/**
 * Check if a key press is a deletion key.
 * 
 * @param key - Key from keyboard event
 * @returns True if key is a deletion key
 */
export function isDeletionKey(key: string): boolean {
  return ['Backspace', 'Delete'].includes(key);
}

/**
 * Sanitize and validate puzzle generation request.
 * 
 * @param topic - Topic string
 * @param gridSize - Grid size
 * @param minWords - Minimum words
 * @param maxWords - Maximum words
 * @returns Object with isValid flag, sanitized values, and error message
 */
export function validatePuzzleRequest(
  topic: string,
  gridSize: number,
  minWords: number,
  maxWords: number
): {
  isValid: boolean;
  error: string | null;
  sanitized: {
    topic: string;
    gridSize: number;
    minWords: number;
    maxWords: number;
  };
} {
  const topicValidation = validateTopic(topic);
  if (!topicValidation.isValid) {
    return {
      isValid: false,
      error: topicValidation.error,
      sanitized: { topic: '', gridSize: 8, minWords: 8, maxWords: 15 },
    };
  }

  const sizeValidation = validateGridSize(gridSize);
  if (!sizeValidation.isValid) {
    return {
      isValid: false,
      error: sizeValidation.error,
      sanitized: { topic: topic.trim(), gridSize: 8, minWords: 8, maxWords: 15 },
    };
  }

  const wordCountValidation = validateWordCount(minWords, maxWords);
  if (!wordCountValidation.isValid) {
    return {
      isValid: false,
      error: wordCountValidation.error,
      sanitized: { topic: topic.trim(), gridSize, minWords: 8, maxWords: 15 },
    };
  }

  return {
    isValid: true,
    error: null,
    sanitized: {
      topic: topic.trim(),
      gridSize,
      minWords,
      maxWords,
    },
  };
}
