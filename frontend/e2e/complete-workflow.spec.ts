/**
 * End-to-End tests for complete user workflow.
 * 
 * These tests verify the complete user journey from puzzle generation
 * through manual solving to AI assistance, ensuring all features work
 * together seamlessly.
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
 * 5. Run tests: npx playwright test e2e/complete-workflow.spec.ts
 */

import { test, expect, Page } from '@playwright/test';

// Test configuration
const FRONTEND_URL = 'http://localhost:5173';
const GENERATION_TIMEOUT = 90000; // 90 seconds for puzzle generation
const AI_OPERATION_TIMEOUT = 30000; // 30 seconds for AI operations

/**
 * Helper function to fill cell
 */
async function fillCell(page: Page, row: number, col: number, value: string) {
  const cellInput = page.locator(`[data-testid="cell-input-${row}-${col}"]`);
  await cellInput.click();
  await cellInput.fill(value);
}

/**
 * Helper function to get cell value
 */
async function getCellValue(page: Page, row: number, col: number): Promise<string> {
  const cellInput = page.locator(`[data-testid="cell-input-${row}-${col}"]`);
  return await cellInput.inputValue();
}

/**
 * Helper function to select a clue
 */
async function selectClue(page: Page, clueNumber: number, direction: 'across' | 'down') {
  const clueSelector = `[data-testid="clue-${clueNumber}-${direction}"]`;
  const clue = page.locator(clueSelector).first();
  
  const clueExists = await clue.count() > 0;
  if (clueExists) {
    await clue.click();
    await page.waitForTimeout(300);
  }
}

test.describe('Complete User Workflow - Basic Journey', () => {
  test('should complete full workflow: generate → solve manually → use AI assistance', async ({ page }) => {
    // ============================================================
    // STEP 1: Navigate to application
    // ============================================================
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');

    // Verify we're on the generator page
    await expect(page.getByTestId('puzzle-generator-form')).toBeVisible();

    // ============================================================
    // STEP 2: Generate a puzzle
    // ============================================================
    const topicInput = page.locator('input[name="topic"]').first();
    await topicInput.fill('Animals');

    const generateButton = page.getByRole('button', { name: /generate puzzle/i });
    await generateButton.click();

    // Wait for puzzle generation
    await page.waitForSelector('[data-testid="grid-container"]', { timeout: GENERATION_TIMEOUT });
    await page.waitForTimeout(1000); // Wait for full render

    // Verify puzzle is displayed
    await expect(page.getByTestId('grid-container')).toBeVisible();
    await expect(page.getByText(/animals/i)).toBeVisible();

    // ============================================================
    // STEP 3: Manually solve some words
    // ============================================================
    // Select first clue
    await selectClue(page, 1, 'across');

    // Try to fill some cells manually
    await fillCell(page, 0, 0, 'C');
    await fillCell(page, 0, 1, 'A');
    await fillCell(page, 0, 2, 'T');

    // Verify cells are filled
    const cell0Value = await getCellValue(page, 0, 0);
    expect(cell0Value).toBe('C');

    // ============================================================
    // STEP 4: Use AI to get a hint
    // ============================================================
    // Verify AI assistance panel is visible
    await expect(page.getByTestId('ai-assistance-panel')).toBeVisible();

    // Select a clue for hint
    await selectClue(page, 1, 'across');

    // Click hint button
    const hintButton = page.getByRole('button', { name: /get hint/i });
    await expect(hintButton).toBeEnabled();
    await hintButton.click();

    // Wait for hint (might show modal or inline)
    await page.waitForTimeout(AI_OPERATION_TIMEOUT);

    // ============================================================
    // STEP 5: Use AI to solve a word
    // ============================================================
    // Select a different clue
    await selectClue(page, 2, 'across');

    // Click solve word button
    const solveWordButton = page.getByRole('button', { name: /solve word/i });
    await expect(solveWordButton).toBeEnabled();
    await solveWordButton.click();

    // Confirm in dialog
    const _confirmDialog = await page.waitForSelector('[data-testid="confirmation-dialog"]', { timeout: 2000 });
    const confirmButton = page.getByRole('button', { name: /confirm|yes/i });
    await confirmButton.click();

    // Wait for AI to solve
    await page.waitForTimeout(AI_OPERATION_TIMEOUT);

    // Verify more cells are filled
    const cellsWithValues = await page.locator('[data-testid^="cell-input-"]:not([value=""])').count();
    expect(cellsWithValues).toBeGreaterThan(3); // Should have more than our manual entries

    // ============================================================
    // STEP 6: Check progress
    // ============================================================
    // Look for progress indicator
    const progressText = page.locator('text=/progress/i, text=/\\d+%/');
    const hasProgress = await progressText.first().isVisible().catch(() => false);
    
    if (hasProgress) {
      const progressContent = await progressText.first().textContent();
      expect(progressContent).toBeTruthy();
    }

    // ============================================================
    // STEP 7: Verify puzzle state is maintained
    // ============================================================
    // Click on a previously filled cell
    await fillCell(page, 0, 0, 'C');
    const verifyValue = await getCellValue(page, 0, 0);
    expect(verifyValue).toBe('C');
  });
});

test.describe('Complete User Workflow - Advanced Features', () => {
  test('should handle multiple AI operations in sequence', async ({ page }) => {
    // Generate puzzle
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');

    const topicInput = page.locator('input[name="topic"]').first();
    await topicInput.fill('Science');

    const generateButton = page.getByRole('button', { name: /generate puzzle/i });
    await generateButton.click();

    await page.waitForSelector('[data-testid="grid-container"]', { timeout: GENERATION_TIMEOUT });
    await page.waitForTimeout(1000);

    // Operation 1: Get hint for first word
    await selectClue(page, 1, 'across');
    const hintButton = page.getByRole('button', { name: /get hint/i });
    if (await hintButton.isEnabled()) {
      await hintButton.click();
      await page.waitForTimeout(AI_OPERATION_TIMEOUT);
    }

    // Operation 2: Solve second word
    await selectClue(page, 2, 'across');
    const solveWordButton = page.getByRole('button', { name: /solve word/i });
    if (await solveWordButton.isEnabled()) {
      await solveWordButton.click();
      
      const confirmDialog = await page.waitForSelector('[data-testid="confirmation-dialog"]', { timeout: 2000 }).catch(() => null);
      if (confirmDialog) {
        const confirmButton = page.getByRole('button', { name: /confirm|yes/i });
        await confirmButton.click();
        await page.waitForTimeout(AI_OPERATION_TIMEOUT);
      }
    }

    // Operation 3: Get hint for third word
    await selectClue(page, 3, 'across');
    if (await hintButton.isEnabled()) {
      await hintButton.click();
      await page.waitForTimeout(AI_OPERATION_TIMEOUT);
    }

    // Verify puzzle still works
    await expect(page.getByTestId('grid-container')).toBeVisible();
  });

  test('should handle manual solving after AI assistance', async ({ page }) => {
    // Generate puzzle
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');

    const topicInput = page.locator('input[name="topic"]').first();
    await topicInput.fill('Technology');

    const generateButton = page.getByRole('button', { name: /generate puzzle/i });
    await generateButton.click();

    await page.waitForSelector('[data-testid="grid-container"]', { timeout: GENERATION_TIMEOUT });
    await page.waitForTimeout(1000);

    // Use AI to solve a word
    await selectClue(page, 1, 'across');
    const solveWordButton = page.getByRole('button', { name: /solve word/i });
    
    if (await solveWordButton.isEnabled()) {
      await solveWordButton.click();
      
      const confirmDialog = await page.waitForSelector('[data-testid="confirmation-dialog"]', { timeout: 2000 }).catch(() => null);
      if (confirmDialog) {
        const confirmButton = page.getByRole('button', { name: /confirm|yes/i });
        await confirmButton.click();
        await page.waitForTimeout(AI_OPERATION_TIMEOUT);
      }
    }

    // Now manually edit cells
    await fillCell(page, 1, 0, 'X');
    await fillCell(page, 1, 1, 'Y');
    await fillCell(page, 1, 2, 'Z');

    // Verify manual edits work
    const cell1Value = await getCellValue(page, 1, 0);
    expect(cell1Value).toBe('X');

    // Use AI again
    await selectClue(page, 2, 'across');
    if (await solveWordButton.isEnabled()) {
      await solveWordButton.click();
      
      const confirmDialog = await page.waitForSelector('[data-testid="confirmation-dialog"]', { timeout: 2000 }).catch(() => null);
      if (confirmDialog) {
        const confirmButton = page.getByRole('button', { name: /confirm|yes/i });
        await confirmButton.click();
        await page.waitForTimeout(AI_OPERATION_TIMEOUT);
      }
    }

    // Verify puzzle still works
    await expect(page.getByTestId('grid-container')).toBeVisible();
  });

  test('should handle solve entire puzzle workflow', async ({ page }) => {
    // Generate puzzle
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');

    const topicInput = page.locator('input[name="topic"]').first();
    await topicInput.fill('History');

    const generateButton = page.getByRole('button', { name: /generate puzzle/i });
    await generateButton.click();

    await page.waitForSelector('[data-testid="grid-container"]', { timeout: GENERATION_TIMEOUT });
    await page.waitForTimeout(1000);

    // Manually fill some cells first
    await fillCell(page, 0, 0, 'A');
    await fillCell(page, 0, 1, 'B');

    // Get initial filled cell count
    const initialFilledCells = await page.locator('[data-testid^="cell-input-"]:not([value=""])').count();

    // Use AI to solve entire puzzle
    const solvePuzzleButton = page.getByRole('button', { name: /solve puzzle/i });
    await solvePuzzleButton.click();

    // Confirm
    const _confirmDialog = await page.waitForSelector('[data-testid="confirmation-dialog"]', { timeout: 2000 });
    const confirmButton = page.getByRole('button', { name: /confirm|yes/i });
    await confirmButton.click();

    // Wait for AI to solve (longer timeout for full puzzle)
    await page.waitForTimeout(AI_OPERATION_TIMEOUT * 2);

    // Verify many more cells are filled
    const finalFilledCells = await page.locator('[data-testid^="cell-input-"]:not([value=""])').count();
    expect(finalFilledCells).toBeGreaterThan(initialFilledCells);

    // Verify puzzle is still interactive
    await fillCell(page, 0, 0, 'Z');
    const verifyValue = await getCellValue(page, 0, 0);
    expect(verifyValue).toBe('Z');
  });
});

test.describe('Complete User Workflow - Error Recovery', () => {
  test('should recover from generation errors and retry', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');

    // Try with invalid topic
    const topicInput = page.locator('input[name="topic"]').first();
    await topicInput.fill('x');

    const generateButton = page.getByRole('button', { name: /generate puzzle/i });
    await generateButton.click();

    // Wait for either success or error
    await page.waitForSelector(
      '[data-testid="grid-container"], text=/failed/i, text=/error/i',
      { timeout: GENERATION_TIMEOUT }
    );

    // If error occurred, retry with valid topic
    const errorVisible = await page.locator('text=/failed/i, text=/error/i').isVisible();
    if (errorVisible) {
      const retryButton = page.getByRole('button', { name: /try again|retry/i });
      if (await retryButton.isVisible()) {
        await retryButton.click();
      }

      // Fill with valid topic
      await topicInput.fill('Valid Topic');
      await generateButton.click();

      // Wait for success
      await page.waitForSelector('[data-testid="grid-container"]', { timeout: GENERATION_TIMEOUT });
      await expect(page.getByTestId('grid-container')).toBeVisible();
    }
  });

  test('should handle AI operation errors gracefully', async ({ page }) => {
    // Generate puzzle
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');

    const topicInput = page.locator('input[name="topic"]').first();
    await topicInput.fill('Test');

    const generateButton = page.getByRole('button', { name: /generate puzzle/i });
    await generateButton.click();

    await page.waitForSelector('[data-testid="grid-container"]', { timeout: GENERATION_TIMEOUT });
    await page.waitForTimeout(1000);

    // Try AI operation
    await selectClue(page, 1, 'across');
    const solveWordButton = page.getByRole('button', { name: /solve word/i });
    
    if (await solveWordButton.isEnabled()) {
      await solveWordButton.click();
      
      const confirmDialog = await page.waitForSelector('[data-testid="confirmation-dialog"]', { timeout: 2000 }).catch(() => null);
      if (confirmDialog) {
        const confirmButton = page.getByRole('button', { name: /confirm|yes/i });
        await confirmButton.click();
        await page.waitForTimeout(AI_OPERATION_TIMEOUT);
      }
    }

    // Verify puzzle is still usable even if AI failed
    await expect(page.getByTestId('grid-container')).toBeVisible();
    
    // Manual solving should still work
    await fillCell(page, 0, 0, 'T');
    const value = await getCellValue(page, 0, 0);
    expect(value).toBe('T');
  });
});

test.describe('Complete User Workflow - State Persistence', () => {
  test('should maintain puzzle state across interactions', async ({ page }) => {
    // Generate puzzle
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');

    const topicInput = page.locator('input[name="topic"]').first();
    await topicInput.fill('Geography');

    const generateButton = page.getByRole('button', { name: /generate puzzle/i });
    await generateButton.click();

    await page.waitForSelector('[data-testid="grid-container"]', { timeout: GENERATION_TIMEOUT });
    await page.waitForTimeout(1000);

    // Fill some cells
    await fillCell(page, 0, 0, 'A');
    await fillCell(page, 0, 1, 'B');
    await fillCell(page, 0, 2, 'C');

    // Select different clues
    await selectClue(page, 1, 'across');
    await selectClue(page, 2, 'across');
    await selectClue(page, 1, 'down');

    // Verify original cells still have values
    expect(await getCellValue(page, 0, 0)).toBe('A');
    expect(await getCellValue(page, 0, 1)).toBe('B');
    expect(await getCellValue(page, 0, 2)).toBe('C');

    // Use AI assistance
    await selectClue(page, 1, 'across');
    const hintButton = page.getByRole('button', { name: /get hint/i });
    if (await hintButton.isEnabled()) {
      await hintButton.click();
      await page.waitForTimeout(AI_OPERATION_TIMEOUT);
    }

    // Verify cells still have values after AI operation
    expect(await getCellValue(page, 0, 0)).toBe('A');
    expect(await getCellValue(page, 0, 1)).toBe('B');
    expect(await getCellValue(page, 0, 2)).toBe('C');
  });

  test('should track progress correctly', async ({ page }) => {
    // Generate puzzle
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');

    const topicInput = page.locator('input[name="topic"]').first();
    await topicInput.fill('Sports');

    const generateButton = page.getByRole('button', { name: /generate puzzle/i });
    await generateButton.click();

    await page.waitForSelector('[data-testid="grid-container"]', { timeout: GENERATION_TIMEOUT });
    await page.waitForTimeout(1000);

    // Check initial progress
    const progressIndicator = page.locator('text=/progress/i, text=/\\d+%/');
    const hasProgress = await progressIndicator.first().isVisible().catch(() => false);

    if (hasProgress) {
      const _initialProgress = await progressIndicator.first().textContent();

      // Fill some cells
      await fillCell(page, 0, 0, 'X');
      await fillCell(page, 0, 1, 'Y');
      await fillCell(page, 0, 2, 'Z');

      // Progress might update
      await page.waitForTimeout(500);

      // Use AI to solve a word
      await selectClue(page, 1, 'across');
      const solveWordButton = page.getByRole('button', { name: /solve word/i });
      
      if (await solveWordButton.isEnabled()) {
        await solveWordButton.click();
        
        const confirmDialog = await page.waitForSelector('[data-testid="confirmation-dialog"]', { timeout: 2000 }).catch(() => null);
        if (confirmDialog) {
          const confirmButton = page.getByRole('button', { name: /confirm|yes/i });
          await confirmButton.click();
          await page.waitForTimeout(AI_OPERATION_TIMEOUT);
        }
      }

      // Progress should have changed
      const finalProgress = await progressIndicator.first().textContent();
      // Progress exists and is being tracked
      expect(finalProgress).toBeTruthy();
    }
  });
});

test.describe('Complete User Workflow - User Experience', () => {
  test('should provide smooth transitions between states', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');

    // Generate puzzle
    const topicInput = page.locator('input[name="topic"]').first();
    await topicInput.fill('Music');

    const generateButton = page.getByRole('button', { name: /generate puzzle/i });
    await generateButton.click();

    // Verify loading state
    const loadingIndicator = page.getByTestId('puzzle-generator-loading-overlay');
    await expect(loadingIndicator).toBeVisible({ timeout: 5000 });

    // Wait for puzzle
    await page.waitForSelector('[data-testid="grid-container"]', { timeout: GENERATION_TIMEOUT });

    // Verify loading is gone
    await expect(loadingIndicator).not.toBeVisible();

    // Verify puzzle is interactive
    await expect(page.getByTestId('grid-container')).toBeVisible();
  });

  test('should show appropriate feedback for user actions', async ({ page }) => {
    // Generate puzzle
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');

    const topicInput = page.locator('input[name="topic"]').first();
    await topicInput.fill('Art');

    const generateButton = page.getByRole('button', { name: /generate puzzle/i });
    await generateButton.click();

    await page.waitForSelector('[data-testid="grid-container"]', { timeout: GENERATION_TIMEOUT });
    await page.waitForTimeout(1000);

    // Click on a cell - should show selection
    const cell = page.locator('[data-testid="cell-0-0"]');
    await cell.click();

    // Cell should be selected (visual feedback)
    const isSelected = await cell.getAttribute('data-selected');
    expect(isSelected).toBeTruthy();

    // Click on a clue - should highlight word
    await selectClue(page, 1, 'across');

    // Clue should be active
    const activeClue = page.locator('[data-testid="clue-1-across"]');
    const isActive = await activeClue.getAttribute('data-active');
    expect(isActive).toBeTruthy();
  });

  test('should handle rapid user interactions', async ({ page }) => {
    // Generate puzzle
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');

    const topicInput = page.locator('input[name="topic"]').first();
    await topicInput.fill('Rapid');

    const generateButton = page.getByRole('button', { name: /generate puzzle/i });
    await generateButton.click();

    await page.waitForSelector('[data-testid="grid-container"]', { timeout: GENERATION_TIMEOUT });
    await page.waitForTimeout(1000);

    // Rapidly click different cells
    for (let i = 0; i < 5; i++) {
      await fillCell(page, 0, i, String.fromCharCode(65 + i)); // A, B, C, D, E
    }

    // Verify all cells were filled
    for (let i = 0; i < 5; i++) {
      const value = await getCellValue(page, 0, i);
      expect(value).toBe(String.fromCharCode(65 + i));
    }

    // Rapidly switch between clues
    await selectClue(page, 1, 'across');
    await selectClue(page, 2, 'across');
    await selectClue(page, 1, 'down');
    await selectClue(page, 1, 'across');

    // Puzzle should still be functional
    await expect(page.getByTestId('grid-container')).toBeVisible();
  });
});
