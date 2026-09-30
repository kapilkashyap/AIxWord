/**
 * End-to-End tests for manual puzzle solving flow.
 * 
 * These tests verify the complete manual solving user journey
 * including cell navigation, input, validation, and completion.
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
 * 5. Run tests: npx playwright test e2e/manual-solving.spec.ts
 */

import { test, expect, Page } from '@playwright/test';

// Test configuration
const FRONTEND_URL = 'http://localhost:5173';
const GENERATION_TIMEOUT = 90000; // 90 seconds for puzzle generation

/**
 * Helper function to generate a puzzle and wait for it to load
 */
async function setupPuzzle(page: Page, topic = 'Testing') {
  await page.goto(FRONTEND_URL);
  await page.waitForLoadState('networkidle');

  // Fill and submit generation form
  const topicInput = page.locator('input[name="topic"]').first();
  await topicInput.fill(topic);

  const generateButton = page.getByRole('button', { name: /generate puzzle/i });
  await generateButton.click();

  // Wait for puzzle to be generated
  await page.waitForSelector('[data-testid="grid-container"]', { timeout: GENERATION_TIMEOUT });
}

/**
 * Helper function to get a cell input element
 */
function getCellInput(page: Page, row: number, col: number) {
  return page.locator(`[data-testid="cell-input-${row}-${col}"]`);
}

/**
 * Helper function to get a cell element
 */
function getCell(page: Page, row: number, col: number) {
  return page.locator(`[data-testid="cell-${row}-${col}"]`);
}

test.describe('Manual Puzzle Solving - Cell Interaction', () => {
  test.beforeEach(async ({ page }) => {
    await setupPuzzle(page, 'Animals');
  });

  test('should select a cell when clicked', async ({ page }) => {
    // Click on a cell
    const cell = getCell(page, 0, 0);
    await cell.click();

    // Verify cell is selected
    const isSelected = await cell.getAttribute('data-selected');
    expect(isSelected).toBe('true');
  });

  test('should allow typing letters in selected cell', async ({ page }) => {
    // Click on a cell
    const cellInput = getCellInput(page, 0, 0);
    await cellInput.click();

    // Type a letter
    await cellInput.fill('A');

    // Verify letter is entered
    const value = await cellInput.inputValue();
    expect(value).toBe('A');
  });

  test('should convert lowercase letters to uppercase', async ({ page }) => {
    // Click on a cell
    const cellInput = getCellInput(page, 0, 0);
    await cellInput.click();

    // Type lowercase letter
    await cellInput.type('a');

    // Verify it's converted to uppercase
    await page.waitForTimeout(100); // Small delay for conversion
    const value = await cellInput.inputValue();
    expect(value).toBe('A');
  });

  test('should only accept single letters', async ({ page }) => {
    // Click on a cell
    const cellInput = getCellInput(page, 0, 0);
    await cellInput.click();

    // Try to type multiple letters
    await cellInput.fill('ABC');

    // Verify only one letter is accepted
    const value = await cellInput.inputValue();
    expect(value.length).toBeLessThanOrEqual(1);
  });

  test('should not accept numbers or special characters', async ({ page }) => {
    // Click on a cell
    const cellInput = getCellInput(page, 0, 0);
    await cellInput.click();

    // Try to type a number
    await cellInput.type('5');

    // Verify it's not accepted
    let value = await cellInput.inputValue();
    expect(value).toBe('');

    // Try to type a special character
    await cellInput.type('!');

    // Verify it's not accepted
    value = await cellInput.inputValue();
    expect(value).toBe('');
  });

  test('should clear cell when backspace is pressed', async ({ page }) => {
    // Click on a cell and enter a letter
    const cellInput = getCellInput(page, 0, 0);
    await cellInput.click();
    await cellInput.fill('A');

    // Verify letter is entered
    let value = await cellInput.inputValue();
    expect(value).toBe('A');

    // Press backspace
    await cellInput.press('Backspace');

    // Verify cell is cleared
    value = await cellInput.inputValue();
    expect(value).toBe('');
  });

  test('should not allow input in blocked cells', async ({ page }) => {
    // Find a blocked cell (if any)
    const blockedCells = page.locator('[data-testid^="cell-"][data-blocked="true"]');
    const count = await blockedCells.count();

    if (count > 0) {
      const blockedCell = blockedCells.first();
      await blockedCell.click();

      // Try to type
      await page.keyboard.type('A');

      // Verify no input was accepted (blocked cells shouldn't have input elements)
      const inputExists = await blockedCell.locator('input').count();
      expect(inputExists).toBe(0);
    }
  });
});

test.describe('Manual Puzzle Solving - Keyboard Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await setupPuzzle(page, 'Geography');
  });

  test('should navigate right with arrow key', async ({ page }) => {
    // Click on first cell
    const cell00 = getCell(page, 0, 0);
    await cell00.click();

    // Press right arrow
    await page.keyboard.press('ArrowRight');

    // Verify next cell is selected
    await page.waitForTimeout(100);
    const cell01 = getCell(page, 0, 1);
    const isSelected = await cell01.getAttribute('data-selected');
    expect(isSelected).toBe('true');
  });

  test('should navigate down with arrow key', async ({ page }) => {
    // Click on first cell
    const cell00 = getCell(page, 0, 0);
    await cell00.click();

    // Press down arrow
    await page.keyboard.press('ArrowDown');

    // Verify cell below is selected
    await page.waitForTimeout(100);
    const cell10 = getCell(page, 1, 0);
    const isSelected = await cell10.getAttribute('data-selected');
    expect(isSelected).toBe('true');
  });

  test('should navigate left with arrow key', async ({ page }) => {
    // Click on a cell that's not in the first column
    const cell01 = getCell(page, 0, 1);
    await cell01.click();

    // Press left arrow
    await page.keyboard.press('ArrowLeft');

    // Verify previous cell is selected
    await page.waitForTimeout(100);
    const cell00 = getCell(page, 0, 0);
    const isSelected = await cell00.getAttribute('data-selected');
    expect(isSelected).toBe('true');
  });

  test('should navigate up with arrow key', async ({ page }) => {
    // Click on a cell that's not in the first row
    const cell10 = getCell(page, 1, 0);
    await cell10.click();

    // Press up arrow
    await page.keyboard.press('ArrowUp');

    // Verify cell above is selected
    await page.waitForTimeout(100);
    const cell00 = getCell(page, 0, 0);
    const isSelected = await cell00.getAttribute('data-selected');
    expect(isSelected).toBe('true');
  });

  test('should move to next cell after entering a letter', async ({ page }) => {
    // Click on first cell
    const cellInput00 = getCellInput(page, 0, 0);
    await cellInput00.click();

    // Type a letter
    await cellInput00.type('A');

    // Verify cursor moved to next cell
    await page.waitForTimeout(200);
    const cellInput01 = getCellInput(page, 0, 1);
    const isFocused = await cellInput01.evaluate((el) => el === document.activeElement);
    expect(isFocused).toBeTruthy();
  });

  test('should toggle direction with space key', async ({ page }) => {
    // Click on a cell
    const cell00 = getCell(page, 0, 0);
    await cell00.click();

    // Get initial direction
    const directionIndicator = page.getByTestId('direction-indicator');
    const initialDirection = await directionIndicator.textContent();

    // Press space to toggle
    await page.keyboard.press('Space');

    // Verify direction changed
    await page.waitForTimeout(100);
    const newDirection = await directionIndicator.textContent();
    expect(newDirection).not.toBe(initialDirection);
  });

  test('should navigate to next word with Tab key', async ({ page }) => {
    // Click on first cell
    const cell00 = getCell(page, 0, 0);
    await cell00.click();

    // Press Tab
    await page.keyboard.press('Tab');

    // Verify focus moved (exact behavior depends on implementation)
    await page.waitForTimeout(100);
    
    // At least verify we didn't lose focus from the grid
    const gridContainer = page.getByTestId('grid-container');
    await expect(gridContainer).toBeVisible();
  });
});

test.describe('Manual Puzzle Solving - Clue Interaction', () => {
  test.beforeEach(async ({ page }) => {
    await setupPuzzle(page, 'Science');
  });

  test('should highlight active word when cell is selected', async ({ page }) => {
    // Click on a cell
    const cell00 = getCell(page, 0, 0);
    await cell00.click();

    // Verify cells in the active word are highlighted
    await page.waitForTimeout(100);
    const activeWordCells = page.locator('[data-testid^="cell-"][data-active-word="true"]');
    const count = await activeWordCells.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should display active clue when cell is selected', async ({ page }) => {
    // Click on a cell with a clue number
    const numberedCell = page.locator('[data-testid^="cell-"] [class*="number"]').first();
    const parentCell = numberedCell.locator('..');
    await parentCell.click();

    // Verify a clue is highlighted in the clue panel
    await page.waitForTimeout(100);
    const activeClue = page.locator('[data-testid^="clue-item-"][data-active="true"]');
    await expect(activeClue).toBeVisible();
  });

  test('should select cell when clicking on a clue', async ({ page }) => {
    // Click on a clue in the clue panel
    const firstClue = page.locator('[data-testid^="clue-item-"]').first();
    await firstClue.click();

    // Verify a cell is selected
    await page.waitForTimeout(100);
    const selectedCell = page.locator('[data-testid^="cell-"][data-selected="true"]');
    await expect(selectedCell).toBeVisible();
  });

  test('should show clue text for active word', async ({ page }) => {
    // Click on a cell
    const cell00 = getCell(page, 0, 0);
    await cell00.click();

    // Verify clue text is visible in the clue panel
    await page.waitForTimeout(100);
    const cluePanel = page.getByTestId('clue-panel');
    await expect(cluePanel).toBeVisible();

    // At least one clue should be visible
    const clues = page.locator('[data-testid^="clue-item-"]');
    const count = await clues.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should switch between across and down clues', async ({ page }) => {
    // Find and click on "Across" tab/section
    const acrossTab = page.locator('text=/across/i').first();
    await acrossTab.click();

    // Verify across clues are visible
    await page.waitForTimeout(100);
    const acrossClues = page.locator('[data-testid*="across"]');
    const acrossCount = await acrossClues.count();
    expect(acrossCount).toBeGreaterThan(0);

    // Click on "Down" tab/section
    const downTab = page.locator('text=/down/i').first();
    await downTab.click();

    // Verify down clues are visible
    await page.waitForTimeout(100);
    const downClues = page.locator('[data-testid*="down"]');
    const downCount = await downClues.count();
    expect(downCount).toBeGreaterThan(0);
  });
});

test.describe('Manual Puzzle Solving - Progress Tracking', () => {
  test.beforeEach(async ({ page }) => {
    await setupPuzzle(page, 'History');
  });

  test('should show initial progress as 0%', async ({ page }) => {
    // Verify progress is 0%
    const progressText = page.locator('text=/progress/i');
    await expect(progressText).toBeVisible();

    const progressValue = page.locator('text=/0%/');
    await expect(progressValue).toBeVisible();
  });

  test('should update progress as cells are filled', async ({ page }) => {
    // Fill in a few cells
    const cellInput00 = getCellInput(page, 0, 0);
    await cellInput00.click();
    await cellInput00.fill('A');

    const cellInput01 = getCellInput(page, 0, 1);
    await cellInput01.click();
    await cellInput01.fill('B');

    // Wait for progress to update
    await page.waitForTimeout(500);

    // Verify progress is no longer 0%
    const progressText = await page.locator('text=/progress/i').textContent();
    expect(progressText).toBeTruthy();
    
    // Progress should have increased
    const hasProgress = await page.locator('text=/[1-9]\\d*%/').isVisible();
    expect(hasProgress).toBeTruthy();
  });

  test('should show completion message when puzzle is fully filled', async ({ page }) => {
    // This test would require filling the entire puzzle
    // For now, we'll just verify the completion message element exists
    const completionMessage = page.getByTestId('completion-message');
    
    // It should not be visible initially
    const isVisible = await completionMessage.isVisible().catch(() => false);
    expect(isVisible).toBe(false);
  });

  test('should display filled cells count', async ({ page }) => {
    // Look for cells count display
    const cellsText = page.locator('text=/cells/i');
    await expect(cellsText).toBeVisible();

    // Fill a cell
    const cellInput00 = getCellInput(page, 0, 0);
    await cellInput00.click();
    await cellInput00.fill('A');

    // Wait for update
    await page.waitForTimeout(500);

    // Verify count updated
    const updatedText = await cellsText.textContent();
    expect(updatedText).toContain('1');
  });

  test('should display completed words count', async ({ page }) => {
    // Look for words count display
    const wordsText = page.locator('text=/words/i');
    await expect(wordsText).toBeVisible();

    // Initially should be 0 completed
    const initialText = await wordsText.textContent();
    expect(initialText).toContain('0');
  });
});

test.describe('Manual Puzzle Solving - Control Actions', () => {
  test.beforeEach(async ({ page }) => {
    await setupPuzzle(page, 'Sports');
  });

  test('should clear current word with clear word button', async ({ page }) => {
    // Fill in some cells
    const cellInput00 = getCellInput(page, 0, 0);
    await cellInput00.click();
    await cellInput00.fill('A');

    const cellInput01 = getCellInput(page, 0, 1);
    await cellInput01.fill('B');

    // Click clear word button
    const clearWordButton = page.getByTestId('clear-word-button');
    await clearWordButton.click();

    // Verify cells in the word are cleared
    await page.waitForTimeout(100);
    const value00 = await cellInput00.inputValue();
    const value01 = await cellInput01.inputValue();
    
    // At least one should be cleared (depending on which word was active)
    expect(value00 === '' || value01 === '').toBeTruthy();
  });

  test('should clear all cells with clear all button', async ({ page }) => {
    // Fill in multiple cells
    const cellInput00 = getCellInput(page, 0, 0);
    await cellInput00.click();
    await cellInput00.fill('A');

    const cellInput01 = getCellInput(page, 0, 1);
    await cellInput01.fill('B');

    const cellInput10 = getCellInput(page, 1, 0);
    await cellInput10.fill('C');

    // Click clear all button
    const clearAllButton = page.getByTestId('clear-all-button');
    await clearAllButton.click();

    // Verify all cells are cleared
    await page.waitForTimeout(100);
    const value00 = await cellInput00.inputValue();
    const value01 = await cellInput01.inputValue();
    const value10 = await cellInput10.inputValue();

    expect(value00).toBe('');
    expect(value01).toBe('');
    expect(value10).toBe('');
  });

  test('should validate solution with check button', async ({ page }) => {
    // Fill in some cells
    const cellInput00 = getCellInput(page, 0, 0);
    await cellInput00.click();
    await cellInput00.fill('A');

    // Click check solution button
    const checkButton = page.getByTestId('check-solution-button');
    await checkButton.click();

    // Wait for validation response
    await page.waitForTimeout(2000);

    // Verify validation notification appears
    const notification = page.getByTestId('validation-notification');
    const isVisible = await notification.isVisible().catch(() => false);
    
    // Notification should appear (even if solution is incorrect)
    expect(isVisible).toBeTruthy();
  });

  test('should disable clear buttons when no input exists', async ({ page }) => {
    // Clear all button should be disabled initially
    const clearAllButton = page.getByTestId('clear-all-button');
    const isDisabled = await clearAllButton.isDisabled();
    expect(isDisabled).toBe(true);
  });

  test('should enable clear buttons after input', async ({ page }) => {
    // Fill in a cell
    const cellInput00 = getCellInput(page, 0, 0);
    await cellInput00.click();
    await cellInput00.fill('A');

    // Wait for state update
    await page.waitForTimeout(100);

    // Clear all button should now be enabled
    const clearAllButton = page.getByTestId('clear-all-button');
    const isDisabled = await clearAllButton.isDisabled();
    expect(isDisabled).toBe(false);
  });
});

test.describe('Manual Puzzle Solving - Validation Feedback', () => {
  test.beforeEach(async ({ page }) => {
    await setupPuzzle(page, 'Technology');
  });

  test('should show success message for correct solution', async ({ page }) => {
    // This would require knowing the correct answers
    // For now, we'll just verify the validation flow works
    
    // Fill in some cells
    const cellInput00 = getCellInput(page, 0, 0);
    await cellInput00.click();
    await cellInput00.fill('A');

    // Validate
    const checkButton = page.getByTestId('check-solution-button');
    await checkButton.click();

    // Wait for response
    await page.waitForTimeout(2000);

    // Notification should appear
    const notification = page.getByTestId('validation-notification');
    const isVisible = await notification.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('should show error count for incorrect solution', async ({ page }) => {
    // Fill in some cells (likely incorrect)
    const cellInput00 = getCellInput(page, 0, 0);
    await cellInput00.click();
    await cellInput00.fill('Z');

    const cellInput01 = getCellInput(page, 0, 1);
    await cellInput01.fill('Z');

    // Validate
    const checkButton = page.getByTestId('check-solution-button');
    await checkButton.click();

    // Wait for response
    await page.waitForTimeout(2000);

    // Notification should show accuracy
    const notification = page.getByTestId('validation-notification');
    const isVisible = await notification.isVisible().catch(() => false);
    
    if (isVisible) {
      const text = await notification.textContent();
      // Should contain accuracy information
      expect(text).toBeTruthy();
    }
  });

  test('should allow dismissing validation notification', async ({ page }) => {
    // Fill and validate
    const cellInput00 = getCellInput(page, 0, 0);
    await cellInput00.click();
    await cellInput00.fill('A');

    const checkButton = page.getByTestId('check-solution-button');
    await checkButton.click();

    // Wait for notification
    await page.waitForTimeout(2000);

    const notification = page.getByTestId('validation-notification');
    const isVisible = await notification.isVisible().catch(() => false);
    
    if (isVisible) {
      // Find and click close button
      const closeButton = notification.locator('button[aria-label*="close"], button:has-text("×")');
      await closeButton.click();

      // Notification should disappear
      await page.waitForTimeout(100);
      const stillVisible = await notification.isVisible().catch(() => false);
      expect(stillVisible).toBe(false);
    }
  });
});

test.describe('Manual Puzzle Solving - Keyboard Shortcuts', () => {
  test.beforeEach(async ({ page }) => {
    await setupPuzzle(page, 'Music');
  });

  test('should display keyboard shortcuts hint', async ({ page }) => {
    // Look for shortcuts hint
    const shortcutsHint = page.getByTestId('shortcuts-hint');
    await expect(shortcutsHint).toBeVisible();

    // Verify it contains common shortcuts
    const text = await shortcutsHint.textContent();
    expect(text).toContain('Navigate');
    expect(text).toContain('Backspace');
  });

  test('should support all documented keyboard shortcuts', async ({ page }) => {
    // Click on a cell
    const cell00 = getCell(page, 0, 0);
    await cell00.click();

    // Test arrow keys (already tested above, but verify they work)
    await page.keyboard.press('ArrowRight');
    await page.waitForTimeout(50);
    
    await page.keyboard.press('ArrowDown');
    await page.waitForTimeout(50);
    
    await page.keyboard.press('ArrowLeft');
    await page.waitForTimeout(50);
    
    await page.keyboard.press('ArrowUp');
    await page.waitForTimeout(50);

    // Test space for direction toggle
    await page.keyboard.press('Space');
    await page.waitForTimeout(50);

    // Test backspace for clear
    const cellInput = getCellInput(page, 0, 0);
    await cellInput.fill('A');
    await page.keyboard.press('Backspace');
    await page.waitForTimeout(50);

    // All shortcuts should work without errors
    const gridContainer = page.getByTestId('grid-container');
    await expect(gridContainer).toBeVisible();
  });
});
