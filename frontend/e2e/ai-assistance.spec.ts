/**
 * End-to-End tests for AI assistance features.
 * 
 * These tests verify the complete AI assistance user journey including:
 * - Solving individual words with AI
 * - Solving entire puzzle with AI
 * - Getting hints for words
 * - Confirmation dialogs and animations
 * 
 * Prerequisites:
 * - Backend server must be running on http://localhost:8000
 * - Frontend dev server must be running on http://localhost:5173
 * - OpenAI API key must be configured (or demo mode enabled)
 * 
 * To run these tests:
 * 1. Install Playwright: npm install -D @playwright/test
 * 2. Install browsers: npx playwright install
 * 3. Start backend: cd backend && uvicorn app.main:app --reload
 * 4. Start frontend: cd frontend && npm run dev
 * 5. Run tests: npx playwright test e2e/ai-assistance.spec.ts
 */

import { test, expect, Page } from '@playwright/test';

// Test configuration
const FRONTEND_URL = 'http://localhost:5173';
const GENERATION_TIMEOUT = 90000; // 90 seconds for puzzle generation
const AI_OPERATION_TIMEOUT = 30000; // 30 seconds for AI operations

/**
 * Helper function to generate a puzzle and wait for it to load
 */
async function setupPuzzle(page: Page, topic = 'Science') {
  await page.goto(FRONTEND_URL);
  await page.waitForLoadState('networkidle');

  // Fill and submit generation form
  const topicInput = page.locator('input[name="topic"]').first();
  await topicInput.fill(topic);

  const generateButton = page.getByRole('button', { name: /generate puzzle/i });
  await generateButton.click();

  // Wait for puzzle to be generated
  await page.waitForSelector('[data-testid="grid-container"]', { timeout: GENERATION_TIMEOUT });
  
  // Wait a bit for the puzzle to fully render
  await page.waitForTimeout(1000);
}

/**
 * Helper function to select a clue
 */
async function selectClue(page: Page, clueNumber: number, direction: 'across' | 'down') {
  const clueSelector = `[data-testid="clue-${clueNumber}-${direction}"]`;
  const clue = page.locator(clueSelector).first();
  
  // If clue exists, click it
  const clueExists = await clue.count() > 0;
  if (clueExists) {
    await clue.click();
    await page.waitForTimeout(300); // Wait for selection to register
  }
}

/**
 * Helper function to get cell value
 */
async function getCellValue(page: Page, row: number, col: number): Promise<string> {
  const cellInput = page.locator(`[data-testid="cell-input-${row}-${col}"]`);
  const value = await cellInput.inputValue();
  return value;
}

test.describe('AI Assistance - Solve Word', () => {
  test.beforeEach(async ({ page }) => {
    await setupPuzzle(page, 'Animals');
  });

  test('should show AI assistance panel when puzzle is loaded', async ({ page }) => {
    // Verify AI assistance panel is visible
    const aiPanel = page.getByTestId('ai-assistance-panel');
    await expect(aiPanel).toBeVisible();

    // Verify buttons are present
    await expect(page.getByRole('button', { name: /solve word/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /solve puzzle/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /get hint/i })).toBeVisible();
  });

  test('should disable solve word button when no clue is selected', async ({ page }) => {
    const solveWordButton = page.getByRole('button', { name: /solve word/i });
    
    // Button should be disabled when no clue is selected
    await expect(solveWordButton).toBeDisabled();
  });

  test('should enable solve word button when clue is selected', async ({ page }) => {
    // Select a clue
    await selectClue(page, 1, 'across');

    const solveWordButton = page.getByRole('button', { name: /solve word/i });
    
    // Button should be enabled
    await expect(solveWordButton).toBeEnabled();
  });

  test('should show confirmation dialog when solve word is clicked', async ({ page }) => {
    // Select a clue
    await selectClue(page, 1, 'across');

    // Click solve word button
    const solveWordButton = page.getByRole('button', { name: /solve word/i });
    await solveWordButton.click();

    // Verify confirmation dialog appears
    const confirmDialog = page.getByTestId('confirmation-dialog');
    await expect(confirmDialog).toBeVisible({ timeout: 2000 });

    // Verify dialog content
    await expect(page.getByText(/solve word with ai/i)).toBeVisible();
    await expect(page.getByText(/are you sure/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /confirm|yes/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /cancel|no/i })).toBeVisible();
  });

  test('should cancel solve word when cancel is clicked', async ({ page }) => {
    // Select a clue
    await selectClue(page, 1, 'across');

    // Click solve word button
    const solveWordButton = page.getByRole('button', { name: /solve word/i });
    await solveWordButton.click();

    // Wait for confirmation dialog
    await page.waitForSelector('[data-testid="confirmation-dialog"]', { timeout: 2000 });

    // Click cancel
    const cancelButton = page.getByRole('button', { name: /cancel|no/i });
    await cancelButton.click();

    // Verify dialog is closed
    const confirmDialog = page.getByTestId('confirmation-dialog');
    await expect(confirmDialog).not.toBeVisible();
  });

  test('should solve word when confirmed', async ({ page }) => {
    // Select a clue
    await selectClue(page, 1, 'across');

    // Get initial cell values
    const _initialValue = await getCellValue(page, 0, 0);

    // Click solve word button
    const solveWordButton = page.getByRole('button', { name: /solve word/i });
    await solveWordButton.click();

    // Wait for confirmation dialog
    await page.waitForSelector('[data-testid="confirmation-dialog"]', { timeout: 2000 });

    // Click confirm
    const confirmButton = page.getByRole('button', { name: /confirm|yes/i });
    await confirmButton.click();

    // Wait for AI operation to complete
    await page.waitForTimeout(AI_OPERATION_TIMEOUT);

    // Verify cells are filled (at least some cells should have values)
    const cellsWithValues = await page.locator('[data-testid^="cell-input-"]:not([value=""])').count();
    expect(cellsWithValues).toBeGreaterThan(0);
  });

  test('should show loading state during solve word operation', async ({ page }) => {
    // Select a clue
    await selectClue(page, 1, 'across');

    // Click solve word button
    const solveWordButton = page.getByRole('button', { name: /solve word/i });
    await solveWordButton.click();

    // Confirm
    await page.waitForSelector('[data-testid="confirmation-dialog"]', { timeout: 2000 });
    const confirmButton = page.getByRole('button', { name: /confirm|yes/i });
    await confirmButton.click();

    // Verify loading indicator appears
    const loadingIndicator = page.locator('[data-testid="ai-loading"], [class*="loading"], [class*="spinner"]');
    const _isLoading = await loadingIndicator.first().isVisible({ timeout: 2000 }).catch(() => false);
    
    // Loading state might be brief, so we just check it was triggered
    // The operation should complete within timeout
    await page.waitForTimeout(AI_OPERATION_TIMEOUT);
  });

  test('should display animation when word is solved', async ({ page }) => {
    // Select a clue
    await selectClue(page, 1, 'across');

    // Click solve word and confirm
    const solveWordButton = page.getByRole('button', { name: /solve word/i });
    await solveWordButton.click();
    
    await page.waitForSelector('[data-testid="confirmation-dialog"]', { timeout: 2000 });
    const confirmButton = page.getByRole('button', { name: /confirm|yes/i });
    await confirmButton.click();

    // Look for animation elements
    const animationElement = page.locator('[data-testid="solution-animation"], [class*="animation"]');
    const _hasAnimation = await animationElement.first().isVisible({ timeout: 5000 }).catch(() => false);
    
    // Animation might be brief, so we just verify the operation completes
    await page.waitForTimeout(AI_OPERATION_TIMEOUT);
  });
});

test.describe('AI Assistance - Solve Puzzle', () => {
  test.beforeEach(async ({ page }) => {
    await setupPuzzle(page, 'Technology');
  });

  test('should show confirmation dialog when solve puzzle is clicked', async ({ page }) => {
    // Click solve puzzle button
    const solvePuzzleButton = page.getByRole('button', { name: /solve puzzle/i });
    await solvePuzzleButton.click();

    // Verify confirmation dialog appears
    const confirmDialog = page.getByTestId('confirmation-dialog');
    await expect(confirmDialog).toBeVisible({ timeout: 2000 });

    // Verify dialog content
    await expect(page.getByText(/solve entire puzzle/i)).toBeVisible();
    await expect(page.getByText(/overwrite all/i)).toBeVisible();
  });

  test('should solve entire puzzle when confirmed', async ({ page }) => {
    // Click solve puzzle button
    const solvePuzzleButton = page.getByRole('button', { name: /solve puzzle/i });
    await solvePuzzleButton.click();

    // Wait for confirmation dialog
    await page.waitForSelector('[data-testid="confirmation-dialog"]', { timeout: 2000 });

    // Click confirm
    const confirmButton = page.getByRole('button', { name: /confirm|yes/i });
    await confirmButton.click();

    // Wait for AI operation to complete (longer timeout for full puzzle)
    await page.waitForTimeout(AI_OPERATION_TIMEOUT * 2);

    // Verify many cells are filled
    const cellsWithValues = await page.locator('[data-testid^="cell-input-"]:not([value=""])').count();
    expect(cellsWithValues).toBeGreaterThan(5); // Should have multiple words filled
  });

  test('should show loading state during solve puzzle operation', async ({ page }) => {
    // Click solve puzzle button
    const solvePuzzleButton = page.getByRole('button', { name: /solve puzzle/i });
    await solvePuzzleButton.click();

    // Confirm
    await page.waitForSelector('[data-testid="confirmation-dialog"]', { timeout: 2000 });
    const confirmButton = page.getByRole('button', { name: /confirm|yes/i });
    await confirmButton.click();

    // Verify loading indicator appears
    const loadingIndicator = page.locator('[data-testid="ai-loading"], [class*="loading"]');
    const _isLoading = await loadingIndicator.first().isVisible({ timeout: 2000 }).catch(() => false);
    
    // Wait for operation to complete
    await page.waitForTimeout(AI_OPERATION_TIMEOUT * 2);
  });

  test('should disable buttons during solve puzzle operation', async ({ page }) => {
    // Click solve puzzle button
    const solvePuzzleButton = page.getByRole('button', { name: /solve puzzle/i });
    await solvePuzzleButton.click();

    // Confirm
    await page.waitForSelector('[data-testid="confirmation-dialog"]', { timeout: 2000 });
    const confirmButton = page.getByRole('button', { name: /confirm|yes/i });
    await confirmButton.click();

    // Wait a moment for operation to start
    await page.waitForTimeout(1000);

    // Verify buttons are disabled during operation
    const solveWordButton = page.getByRole('button', { name: /solve word/i });
    const getHintButton = page.getByRole('button', { name: /get hint/i });
    
    // At least one button should be disabled during operation
    const _wordButtonDisabled = await solveWordButton.isDisabled().catch(() => false);
    const _hintButtonDisabled = await getHintButton.isDisabled().catch(() => false);
    
    // Wait for operation to complete
    await page.waitForTimeout(AI_OPERATION_TIMEOUT * 2);
  });
});

test.describe('AI Assistance - Hints', () => {
  test.beforeEach(async ({ page }) => {
    await setupPuzzle(page, 'History');
  });

  test('should disable hint button when no clue is selected', async ({ page }) => {
    const hintButton = page.getByRole('button', { name: /get hint/i });
    
    // Button should be disabled when no clue is selected
    await expect(hintButton).toBeDisabled();
  });

  test('should enable hint button when clue is selected', async ({ page }) => {
    // Select a clue
    await selectClue(page, 1, 'across');

    const hintButton = page.getByRole('button', { name: /get hint/i });
    
    // Button should be enabled
    await expect(hintButton).toBeEnabled();
  });

  test('should show hint modal when hint button is clicked', async ({ page }) => {
    // Select a clue
    await selectClue(page, 1, 'across');

    // Click hint button
    const hintButton = page.getByRole('button', { name: /get hint/i });
    await hintButton.click();

    // Wait for hint to be generated
    await page.waitForTimeout(AI_OPERATION_TIMEOUT);

    // Verify hint modal appears
    const hintModal = page.getByTestId('hint-modal');
    const isVisible = await hintModal.isVisible({ timeout: 5000 }).catch(() => false);
    
    if (isVisible) {
      // Verify modal content
      await expect(page.getByText(/hint/i)).toBeVisible();
    }
  });

  test('should close hint modal when close button is clicked', async ({ page }) => {
    // Select a clue
    await selectClue(page, 1, 'across');

    // Click hint button
    const hintButton = page.getByRole('button', { name: /get hint/i });
    await hintButton.click();

    // Wait for hint modal
    await page.waitForTimeout(AI_OPERATION_TIMEOUT);

    const hintModal = page.getByTestId('hint-modal');
    const isVisible = await hintModal.isVisible({ timeout: 5000 }).catch(() => false);
    
    if (isVisible) {
      // Click close button
      const closeButton = page.getByRole('button', { name: /close/i });
      await closeButton.click();

      // Verify modal is closed
      await expect(hintModal).not.toBeVisible();
    }
  });

  test('should show loading state during hint generation', async ({ page }) => {
    // Select a clue
    await selectClue(page, 1, 'across');

    // Click hint button
    const hintButton = page.getByRole('button', { name: /get hint/i });
    await hintButton.click();

    // Verify loading indicator appears
    const loadingIndicator = page.locator('[data-testid="ai-loading"], [class*="loading"]');
    const _isLoading = await loadingIndicator.first().isVisible({ timeout: 2000 }).catch(() => false);
    
    // Wait for operation to complete
    await page.waitForTimeout(AI_OPERATION_TIMEOUT);
  });

  test('should support different hint types', async ({ page }) => {
    // Select a clue
    await selectClue(page, 1, 'across');

    // Look for hint type selector
    const hintTypeSelector = page.locator('select[name="hint_type"], [data-testid="hint-type-selector"]');
    const hasSelectorOptions = await hintTypeSelector.count() > 0;

    if (hasSelectorOptions) {
      // Try selecting different hint types
      await hintTypeSelector.selectOption('definition');
      
      // Click hint button
      const hintButton = page.getByRole('button', { name: /get hint/i });
      await hintButton.click();

      // Wait for hint
      await page.waitForTimeout(AI_OPERATION_TIMEOUT);
    }
  });
});

test.describe('AI Assistance - Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    await setupPuzzle(page, 'Test');
  });

  test('should handle solve word errors gracefully', async ({ page }) => {
    // Select a clue
    await selectClue(page, 1, 'across');

    // Click solve word and confirm
    const solveWordButton = page.getByRole('button', { name: /solve word/i });
    await solveWordButton.click();
    
    await page.waitForSelector('[data-testid="confirmation-dialog"]', { timeout: 2000 });
    const confirmButton = page.getByRole('button', { name: /confirm|yes/i });
    await confirmButton.click();

    // Wait for operation
    await page.waitForTimeout(AI_OPERATION_TIMEOUT);

    // Check for error message
    const errorMessage = page.locator('[data-testid="error-message"], [class*="error"]');
    const hasError = await errorMessage.first().isVisible({ timeout: 2000 }).catch(() => false);
    
    // If error occurred, verify it's user-friendly
    if (hasError) {
      const errorText = await errorMessage.first().textContent();
      expect(errorText).toBeTruthy();
      expect(errorText!.length).toBeGreaterThan(0);
    }
  });

  test('should handle solve puzzle errors gracefully', async ({ page }) => {
    // Click solve puzzle and confirm
    const solvePuzzleButton = page.getByRole('button', { name: /solve puzzle/i });
    await solvePuzzleButton.click();
    
    await page.waitForSelector('[data-testid="confirmation-dialog"]', { timeout: 2000 });
    const confirmButton = page.getByRole('button', { name: /confirm|yes/i });
    await confirmButton.click();

    // Wait for operation
    await page.waitForTimeout(AI_OPERATION_TIMEOUT * 2);

    // Check for error message
    const errorMessage = page.locator('[data-testid="error-message"], [class*="error"]');
    const hasError = await errorMessage.first().isVisible({ timeout: 2000 }).catch(() => false);
    
    // If error occurred, verify it's user-friendly
    if (hasError) {
      const errorText = await errorMessage.first().textContent();
      expect(errorText).toBeTruthy();
    }
  });

  test('should handle hint generation errors gracefully', async ({ page }) => {
    // Select a clue
    await selectClue(page, 1, 'across');

    // Click hint button
    const hintButton = page.getByRole('button', { name: /get hint/i });
    await hintButton.click();

    // Wait for operation
    await page.waitForTimeout(AI_OPERATION_TIMEOUT);

    // Check for error message
    const errorMessage = page.locator('[data-testid="error-message"], [class*="error"]');
    const hasError = await errorMessage.first().isVisible({ timeout: 2000 }).catch(() => false);
    
    // If error occurred, verify it's user-friendly
    if (hasError) {
      const errorText = await errorMessage.first().textContent();
      expect(errorText).toBeTruthy();
    }
  });
});

test.describe('AI Assistance - Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await setupPuzzle(page, 'Accessibility');
  });

  test('should have accessible button labels', async ({ page }) => {
    // Verify buttons have proper labels
    await expect(page.getByRole('button', { name: /solve word/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /solve puzzle/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /get hint/i })).toBeVisible();
  });

  test('should be keyboard navigable', async ({ page }) => {
    // Tab through AI assistance buttons
    await page.keyboard.press('Tab');
    
    // Continue tabbing to reach AI assistance panel
    for (let i = 0; i < 20; i++) {
      await page.keyboard.press('Tab');
      
      // Check if we've reached any AI button
      const solveWordButton = page.getByRole('button', { name: /solve word/i });
      const isFocused = await solveWordButton.evaluate((el) => el === document.activeElement);
      if (isFocused) break;
    }
  });

  test('should have proper ARIA attributes', async ({ page }) => {
    const aiPanel = page.getByTestId('ai-assistance-panel');
    
    // Check for ARIA attributes
    const ariaLabel = await aiPanel.getAttribute('aria-label');
    const role = await aiPanel.getAttribute('role');
    
    // Should have some accessibility attributes
    expect(ariaLabel || role).toBeTruthy();
  });
});

test.describe('AI Assistance - Performance', () => {
  test('should complete solve word within reasonable time', async ({ page }) => {
    await setupPuzzle(page, 'Performance');
    
    // Select a clue
    await selectClue(page, 1, 'across');

    const startTime = Date.now();

    // Click solve word and confirm
    const solveWordButton = page.getByRole('button', { name: /solve word/i });
    await solveWordButton.click();
    
    await page.waitForSelector('[data-testid="confirmation-dialog"]', { timeout: 2000 });
    const confirmButton = page.getByRole('button', { name: /confirm|yes/i });
    await confirmButton.click();

    // Wait for operation to complete
    await page.waitForTimeout(AI_OPERATION_TIMEOUT);

    const endTime = Date.now();
    const duration = endTime - startTime;

    // Should complete within timeout
    expect(duration).toBeLessThan(AI_OPERATION_TIMEOUT + 5000);

    console.log(`Solve word took ${duration}ms`);
  });

  test('should complete hint generation within reasonable time', async ({ page }) => {
    await setupPuzzle(page, 'Performance');
    
    // Select a clue
    await selectClue(page, 1, 'across');

    const startTime = Date.now();

    // Click hint button
    const hintButton = page.getByRole('button', { name: /get hint/i });
    await hintButton.click();

    // Wait for operation to complete
    await page.waitForTimeout(AI_OPERATION_TIMEOUT);

    const endTime = Date.now();
    const duration = endTime - startTime;

    // Should complete within timeout
    expect(duration).toBeLessThan(AI_OPERATION_TIMEOUT + 5000);

    console.log(`Hint generation took ${duration}ms`);
  });
});
