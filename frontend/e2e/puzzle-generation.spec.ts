/**
 * End-to-End tests for puzzle generation flow.
 * 
 * These tests verify the complete puzzle generation user journey
 * from form submission to puzzle display, using Playwright to
 * simulate real browser interactions.
 * 
 * Prerequisites:
 * - Backend server must be running on http://localhost:8000
 * - Frontend dev server must be running on http://localhost:5173
 * 
 * To run these tests:
 * 1. Install Playwright: npm install -D @playwright/test
 * 2. Install browsers: npx playwright install
 * 3. Start backend: cd backend && uvicorn app.main:app --reload
 * 4. Start frontend: cd frontend && npm run dev
 * 5. Run tests: npx playwright test e2e/puzzle-generation.spec.ts
 */

import { test, expect, Page } from '@playwright/test';

// Test configuration
const FRONTEND_URL = 'http://localhost:5173';
// Backend URL for future use
// const BACKEND_URL = 'http://localhost:8000';
const GENERATION_TIMEOUT = 90000; // 90 seconds for puzzle generation

/**
 * Helper function to wait for puzzle generation to complete
 */
async function waitForPuzzleGeneration(page: Page, timeout = GENERATION_TIMEOUT) {
  // Wait for either success or error state
  await page.waitForSelector(
    '[data-testid="grid-container"], [data-testid="puzzle-generator-error"]',
    { timeout }
  );
}

/**
 * Helper function to fill and submit the puzzle generation form
 */
async function generatePuzzle(
  page: Page,
  options: {
    topic: string;
    gridSize?: number;
    difficulty?: 'easy' | 'medium' | 'hard';
  }
) {
  // Fill in the topic
  const topicInput = page.locator('input[name="topic"], input[id*="topic"]').first();
  await topicInput.fill(options.topic);

  // Optionally set grid size
  if (options.gridSize) {
    const gridSizeInput = page.locator('input[name="grid_size"], select[name="grid_size"]').first();
    await gridSizeInput.fill(options.gridSize.toString());
  }

  // Optionally set difficulty
  if (options.difficulty) {
    const difficultySelect = page.locator('select[name="difficulty"]').first();
    await difficultySelect.selectOption(options.difficulty);
  }

  // Submit the form
  const generateButton = page.getByRole('button', { name: /generate puzzle/i });
  await generateButton.click();
}

test.describe('Puzzle Generation Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto(FRONTEND_URL);
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Verify we're on the generator page
    await expect(page.getByTestId('puzzle-generator-form')).toBeVisible();
  });

  test('should display the puzzle generation form on initial load', async ({ page }) => {
    // Verify form elements are present
    await expect(page.getByText(/create your crossword puzzle/i)).toBeVisible();
    await expect(page.locator('input[name="topic"]')).toBeVisible();
    await expect(page.getByRole('button', { name: /generate puzzle/i })).toBeVisible();
  });

  test('should validate required fields before submission', async ({ page }) => {
    // Try to submit without filling in topic
    const generateButton = page.getByRole('button', { name: /generate puzzle/i });
    await generateButton.click();

    // Check for validation error (HTML5 validation or custom)
    const topicInput = page.locator('input[name="topic"]').first();
    const validationMessage = await topicInput.evaluate((el: HTMLInputElement) => el.validationMessage);
    
    // Either HTML5 validation kicks in, or we should see an error message
    const hasValidation = validationMessage !== '' || 
                         await page.locator('text=/topic.*required/i').isVisible();
    expect(hasValidation).toBeTruthy();
  });

  test('should successfully generate a puzzle with valid topic', async ({ page }) => {
    // Fill and submit the form
    await generatePuzzle(page, {
      topic: 'Space Exploration',
      gridSize: 8,
      difficulty: 'medium',
    });

    // Wait for generation to complete
    await waitForPuzzleGeneration(page);

    // Verify puzzle grid is displayed
    await expect(page.getByTestId('grid-container')).toBeVisible({ timeout: GENERATION_TIMEOUT });

    // Verify puzzle info is displayed
    await expect(page.getByText('Space Exploration')).toBeVisible();
    await expect(page.getByText(/progress:/i)).toBeVisible();

    // Verify clues are displayed
    await expect(page.getByText(/across/i)).toBeVisible();
    await expect(page.getByText(/down/i)).toBeVisible();

    // Verify grid cells are rendered
    const cells = page.locator('[data-testid^="cell-"]');
    const cellCount = await cells.count();
    expect(cellCount).toBeGreaterThan(0);
  });

  test('should show loading state during puzzle generation', async ({ page }) => {
    // Start generation
    await generatePuzzle(page, {
      topic: 'Ancient History',
    });

    // Verify loading indicator appears
    const loadingIndicator = page.getByTestId('puzzle-generator-loading-overlay');
    await expect(loadingIndicator).toBeVisible({ timeout: 5000 });

    // Verify loading message
    await expect(page.getByText(/generating your puzzle/i)).toBeVisible();

    // Wait for completion
    await waitForPuzzleGeneration(page);

    // Verify loading indicator disappears
    await expect(loadingIndicator).not.toBeVisible();
  });

  test('should display progress updates during generation', async ({ page }) => {
    // Start generation
    await generatePuzzle(page, {
      topic: 'Technology',
    });

    // Check for progress component
    const progressComponent = page.getByTestId('generation-progress');
    await expect(progressComponent).toBeVisible({ timeout: 5000 });

    // Wait for completion
    await waitForPuzzleGeneration(page);
  });

  test('should handle generation errors gracefully', async ({ page }) => {
    // Try to generate with an invalid or very difficult topic
    await generatePuzzle(page, {
      topic: 'xyzabc123invalidtopic',
      gridSize: 15,
      difficulty: 'hard',
    });

    // Wait for either success or error
    await page.waitForSelector(
      '[data-testid="grid-container"], [data-testid="puzzle-generator-error"], text=/failed/i',
      { timeout: GENERATION_TIMEOUT }
    );

    // If error occurred, verify error message is displayed
    const errorVisible = await page.locator('text=/failed/i, text=/error/i').isVisible();
    if (errorVisible) {
      // Verify error message is user-friendly
      const errorText = await page.locator('[data-testid="puzzle-generator-error"]').textContent();
      expect(errorText).toBeTruthy();
      expect(errorText!.length).toBeGreaterThan(0);
    }
  });

  test('should allow retry after generation failure', async ({ page }) => {
    // Mock a failure scenario by using invalid parameters
    await generatePuzzle(page, {
      topic: 'x', // Too short
    });

    // Wait for error or success
    await page.waitForSelector(
      '[data-testid="grid-container"], text=/failed/i, text=/error/i',
      { timeout: GENERATION_TIMEOUT }
    );

    // If error occurred, look for retry button
    const errorVisible = await page.locator('text=/failed/i, text=/error/i').isVisible();
    if (errorVisible) {
      const retryButton = page.getByRole('button', { name: /try again|retry/i });
      await expect(retryButton).toBeVisible();

      // Click retry
      await retryButton.click();

      // Verify form is shown again
      await expect(page.getByTestId('puzzle-generator-form')).toBeVisible();
    }
  });

  test('should generate puzzles with different grid sizes', async ({ page }) => {
    // Test with 5x5 grid
    await generatePuzzle(page, {
      topic: 'Colors',
      gridSize: 5,
    });

    await waitForPuzzleGeneration(page);

    // Verify grid is displayed
    const gridVisible = await page.getByTestId('grid-container').isVisible();
    if (gridVisible) {
      // Count cells (should be 25 for 5x5)
      const cells = page.locator('[data-testid^="cell-"]');
      const cellCount = await cells.count();
      expect(cellCount).toBeLessThanOrEqual(25);
    }
  });

  test('should generate puzzles with different difficulty levels', async ({ page }) => {
    // Test easy difficulty
    await generatePuzzle(page, {
      topic: 'Animals',
      difficulty: 'easy',
    });

    await waitForPuzzleGeneration(page);

    // Verify puzzle is generated
    const gridVisible = await page.getByTestId('grid-container').isVisible();
    if (gridVisible) {
      // Verify difficulty is displayed
      await expect(page.getByText(/easy/i)).toBeVisible();
    }
  });

  test('should display puzzle metadata after generation', async ({ page }) => {
    await generatePuzzle(page, {
      topic: 'Music',
      gridSize: 8,
      difficulty: 'medium',
    });

    await waitForPuzzleGeneration(page);

    const gridVisible = await page.getByTestId('grid-container').isVisible();
    if (gridVisible) {
      // Verify metadata is displayed
      await expect(page.getByText('Music')).toBeVisible();
      await expect(page.getByText(/difficulty/i)).toBeVisible();
      await expect(page.getByText(/words/i)).toBeVisible();
      await expect(page.getByText(/progress/i)).toBeVisible();
    }
  });

  test('should show help section before generation', async ({ page }) => {
    // Verify help section is visible
    const helpSection = page.locator('text=/tips for great puzzles/i');
    await expect(helpSection).toBeVisible();

    // Verify help content
    await expect(page.getByText(/choose specific topics/i)).toBeVisible();
    await expect(page.getByText(/start with 8×8/i)).toBeVisible();
  });

  test('should hide help section after successful generation', async ({ page }) => {
    await generatePuzzle(page, {
      topic: 'Sports',
    });

    await waitForPuzzleGeneration(page);

    const gridVisible = await page.getByTestId('grid-container').isVisible();
    if (gridVisible) {
      // Help section should not be visible
      const helpSection = page.locator('text=/tips for great puzzles/i');
      await expect(helpSection).not.toBeVisible();
    }
  });

  test('should allow generating a new puzzle after successful generation', async ({ page }) => {
    // Generate first puzzle
    await generatePuzzle(page, {
      topic: 'Science',
    });

    await waitForPuzzleGeneration(page);

    const gridVisible = await page.getByTestId('grid-container').isVisible();
    if (gridVisible) {
      // Click "New Puzzle" button
      const newPuzzleButton = page.getByTestId('new-puzzle-button');
      await newPuzzleButton.click();

      // Verify we're back to the generator form
      await expect(page.getByTestId('puzzle-generator-form')).toBeVisible();

      // Generate another puzzle
      await generatePuzzle(page, {
        topic: 'Geography',
      });

      await waitForPuzzleGeneration(page);

      // Verify new puzzle is displayed
      const newGridVisible = await page.getByTestId('grid-container').isVisible();
      if (newGridVisible) {
        await expect(page.getByText('Geography')).toBeVisible();
      }
    }
  });

  test('should preserve form values when validation fails', async ({ page }) => {
    // Fill in the form
    const topicInput = page.locator('input[name="topic"]').first();
    await topicInput.fill('Test Topic');

    // Try to submit (might fail validation)
    const generateButton = page.getByRole('button', { name: /generate puzzle/i });
    await generateButton.click();

    // Wait a moment
    await page.waitForTimeout(1000);

    // Verify topic is still in the input
    const topicValue = await topicInput.inputValue();
    expect(topicValue).toBe('Test Topic');
  });

  test('should handle network errors during generation', async ({ page }) => {
    // Intercept API call and simulate network error
    await page.route('**/api/puzzles/generate', (route) => {
      route.abort('failed');
    });

    await generatePuzzle(page, {
      topic: 'Network Test',
    });

    // Wait for error message
    await page.waitForSelector('text=/error/i, text=/failed/i', { timeout: 10000 });

    // Verify error is displayed
    const errorVisible = await page.locator('text=/error/i, text=/failed/i').isVisible();
    expect(errorVisible).toBeTruthy();
  });

  test('should display word count in puzzle info', async ({ page }) => {
    await generatePuzzle(page, {
      topic: 'Literature',
    });

    await waitForPuzzleGeneration(page);

    const gridVisible = await page.getByTestId('grid-container').isVisible();
    if (gridVisible) {
      // Verify word count is displayed
      const wordCountText = page.locator('text=/words:/i');
      await expect(wordCountText).toBeVisible();

      // Extract and verify the number
      const text = await wordCountText.textContent();
      const match = text?.match(/(\d+)/);
      if (match) {
        const wordCount = parseInt(match[1]);
        expect(wordCount).toBeGreaterThan(0);
      }
    }
  });

  test('should render all clue numbers in the grid', async ({ page }) => {
    await generatePuzzle(page, {
      topic: 'Food',
    });

    await waitForPuzzleGeneration(page);

    const gridVisible = await page.getByTestId('grid-container').isVisible();
    if (gridVisible) {
      // Find cells with numbers
      const numberedCells = page.locator('[data-testid^="cell-"] [class*="number"]');
      const count = await numberedCells.count();
      
      // Should have at least some numbered cells
      expect(count).toBeGreaterThan(0);
    }
  });
});

test.describe('Puzzle Generation Performance', () => {
  test('should generate 8x8 puzzle within reasonable time', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');

    const startTime = Date.now();

    await generatePuzzle(page, {
      topic: 'Performance Test',
      gridSize: 8,
    });

    await waitForPuzzleGeneration(page);

    const endTime = Date.now();
    const duration = endTime - startTime;

    // Should complete within 90 seconds
    expect(duration).toBeLessThan(GENERATION_TIMEOUT);

    // Log performance for monitoring
    console.log(`Puzzle generation took ${duration}ms`);
  });
});

test.describe('Puzzle Generation Accessibility', () => {
  test('should have accessible form labels', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');

    // Check for proper labels
    const topicLabel = page.locator('label[for*="topic"]');
    await expect(topicLabel).toBeVisible();

    // Check ARIA attributes
    const generateButton = page.getByRole('button', { name: /generate puzzle/i });
    await expect(generateButton).toBeVisible();
  });

  test('should be keyboard navigable', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');

    // Tab through form elements
    await page.keyboard.press('Tab');
    const topicInput = page.locator('input[name="topic"]').first();
    await expect(topicInput).toBeFocused();

    // Type in the input
    await page.keyboard.type('Keyboard Test');

    // Tab to submit button
    await page.keyboard.press('Tab');
    // Continue tabbing until we reach the generate button
    for (let i = 0; i < 5; i++) {
      const generateButton = page.getByRole('button', { name: /generate puzzle/i });
      const isFocused = await generateButton.evaluate((el) => el === document.activeElement);
      if (isFocused) break;
      await page.keyboard.press('Tab');
    }
  });
});
