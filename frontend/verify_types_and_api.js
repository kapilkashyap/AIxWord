#!/usr/bin/env node

/**
 * Verification script for TypeScript types and API client.
 * 
 * This script verifies that:
 * 1. All TypeScript files compile without errors
 * 2. Type definitions are complete and consistent
 * 3. API client is properly configured
 * 4. Utility functions are properly exported
 * 5. Custom hooks are properly structured
 */

import { execSync } from 'child_process';
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const REQUIRED_FILES = [
  'src/types/puzzle.ts',
  'src/types/api.ts',
  'src/services/api.ts',
  'src/hooks/usePuzzle.ts',
  'src/hooks/useAPI.ts',
  'src/utils/grid.ts',
  'src/utils/validation.ts',
  'src/utils/keyboard.ts',
];

const REQUIRED_EXPORTS = {
  'src/types/puzzle.ts': [
    'Direction',
    'Difficulty',
    'HintType',
    'Cell',
    'Clue',
    'Puzzle',
    'WordPlacement',
    'CellState',
    'GridState',
    'ValidationError',
  ],
  'src/types/api.ts': [
    'PuzzleGenerateRequest',
    'SolvePuzzleRequest',
    'SolveWordRequest',
    'HintRequest',
    'ValidateRequest',
    'PuzzleGenerateResponse',
    'SolveResponse',
    'HintResponse',
    'ValidateResponse',
    'ErrorResponse',
    'ApiState',
    'ApiConfig',
  ],
  'src/services/api.ts': [
    'apiClient',
    'ApiClient',
  ],
  'src/hooks/usePuzzle.ts': [
    'usePuzzle',
  ],
  'src/hooks/useAPI.ts': [
    'useAPI',
    'useMultiAPI',
  ],
  'src/utils/grid.ts': [
    'coordsToIndex',
    'indexToCoords',
    'isValidCoord',
    'getCellAt',
    'getWordCells',
    'getWordText',
    'isWordComplete',
    'getNextCell',
    'getPreviousCell',
    'findClueForCell',
    'getIntersectingClues',
    'createEmptyGrid',
    'cloneCells',
    'updateCell',
  ],
  'src/utils/validation.ts': [
    'isValidLetter',
    'sanitizeLetter',
    'validateTopic',
    'validateGridSize',
    'validateWordCount',
    'isLetterKey',
    'isNavigationKey',
    'isDeletionKey',
    'validatePuzzleRequest',
  ],
  'src/utils/keyboard.ts': [
    'getNextCellFromArrow',
    'getNextCellInWord',
    'getPreviousCellInWord',
    'toggleDirection',
    'getWordStartCell',
    'getWordEndCell',
    'isCellInWord',
    'getWordCellPositions',
    'findNextEmptyCell',
  ],
};

let errors = 0;
let warnings = 0;

function log(message, type = 'info') {
  const prefix = {
    info: '  ',
    success: '✓ ',
    error: '✗ ',
    warning: '⚠ ',
  }[type];
  console.log(`${prefix}${message}`);
}

function checkFileExists(file) {
  const fullPath = join(__dirname, file);
  if (!existsSync(fullPath)) {
    log(`Missing file: ${file}`, 'error');
    errors++;
    return false;
  }
  return true;
}

function checkExports(file, expectedExports) {
  const fullPath = join(__dirname, file);
  const content = readFileSync(fullPath, 'utf-8');
  
  const missingExports = [];
  for (const exportName of expectedExports) {
    // Check for various export patterns
    const patterns = [
      new RegExp(`export\\s+(interface|type|class|function|const)\\s+${exportName}\\b`),
      new RegExp(`export\\s+\\{[^}]*\\b${exportName}\\b[^}]*\\}`),
      new RegExp(`export\\s+default\\s+${exportName}\\b`),
    ];
    
    const found = patterns.some(pattern => pattern.test(content));
    if (!found) {
      missingExports.push(exportName);
    }
  }
  
  if (missingExports.length > 0) {
    log(`Missing exports in ${file}: ${missingExports.join(', ')}`, 'warning');
    warnings++;
  }
}

function runTypeScriptCheck() {
  try {
    log('Running TypeScript compilation check...', 'info');
    execSync('npx tsc --noEmit', { 
      cwd: __dirname,
      stdio: 'pipe',
      encoding: 'utf-8'
    });
    log('TypeScript compilation successful', 'success');
    return true;
  } catch (error) {
    log('TypeScript compilation failed:', 'error');
    console.log(error.stdout);
    errors++;
    return false;
  }
}

function checkImportPaths() {
  log('Checking import paths...', 'info');
  
  const filesToCheck = [
    'src/services/api.ts',
    'src/hooks/useAPI.ts',
    'src/hooks/usePuzzle.ts',
    'src/utils/grid.ts',
    'src/utils/keyboard.ts',
  ];
  
  for (const file of filesToCheck) {
    const fullPath = join(__dirname, file);
    if (!existsSync(fullPath)) continue;
    
    const content = readFileSync(fullPath, 'utf-8');
    
    // Check for problematic @types/ imports
    if (content.includes("from '@types/")) {
      log(`File ${file} uses problematic @types/ import path`, 'error');
      errors++;
    }
    
    // Check for relative imports
    const relativeImports = content.match(/from ['"]\.\.?\//g);
    if (relativeImports) {
      log(`File ${file} uses relative imports (${relativeImports.length} found)`, 'success');
    }
  }
}

function checkAPIConfiguration() {
  log('Checking API configuration...', 'info');
  
  const apiFile = join(__dirname, 'src/services/api.ts');
  const content = readFileSync(apiFile, 'utf-8');
  
  // Check for environment variable usage
  if (content.includes('import.meta.env.VITE_API_BASE_URL')) {
    log('API client uses environment variables', 'success');
  } else {
    log('API client does not use environment variables', 'warning');
    warnings++;
  }
  
  // Check for error handling
  if (content.includes('handleError')) {
    log('API client has error handling', 'success');
  } else {
    log('API client missing error handling', 'error');
    errors++;
  }
  
  // Check for all required API methods
  const requiredMethods = [
    'generatePuzzle',
    'getPuzzle',
    'listPuzzles',
    'solvePuzzle',
    'solveWord',
    'getHint',
    'validateSolution',
    'deletePuzzle',
  ];
  
  for (const method of requiredMethods) {
    if (content.includes(`async ${method}(`)) {
      log(`API method ${method} implemented`, 'success');
    } else {
      log(`API method ${method} missing`, 'error');
      errors++;
    }
  }
}

function checkHooks() {
  log('Checking custom hooks...', 'info');
  
  // Check useAPI hook
  const useAPIFile = join(__dirname, 'src/hooks/useAPI.ts');
  const useAPIContent = readFileSync(useAPIFile, 'utf-8');
  
  if (useAPIContent.includes('useState') && useAPIContent.includes('useCallback')) {
    log('useAPI hook uses React hooks correctly', 'success');
  } else {
    log('useAPI hook missing React hooks', 'error');
    errors++;
  }
  
  // Check usePuzzle hook
  const usePuzzleFile = join(__dirname, 'src/hooks/usePuzzle.ts');
  const usePuzzleContent = readFileSync(usePuzzleFile, 'utf-8');
  
  const requiredPuzzleMethods = [
    'loadPuzzle',
    'clearPuzzle',
    'setCellValue',
    'clearCell',
    'resetGrid',
    'selectCell',
    'toggleDirection',
    'selectClue',
  ];
  
  for (const method of requiredPuzzleMethods) {
    if (usePuzzleContent.includes(method)) {
      log(`usePuzzle method ${method} implemented`, 'success');
    } else {
      log(`usePuzzle method ${method} missing`, 'error');
      errors++;
    }
  }
}

function checkUtilities() {
  log('Checking utility functions...', 'info');
  
  // Check grid utilities
  const gridFile = join(__dirname, 'src/utils/grid.ts');
  const gridContent = readFileSync(gridFile, 'utf-8');
  
  if (gridContent.includes('coordsToIndex') && gridContent.includes('indexToCoords')) {
    log('Grid coordinate conversion utilities present', 'success');
  }
  
  // Check validation utilities
  const validationFile = join(__dirname, 'src/utils/validation.ts');
  const validationContent = readFileSync(validationFile, 'utf-8');
  
  if (validationContent.includes('validateTopic') && validationContent.includes('validateGridSize')) {
    log('Validation utilities present', 'success');
  }
  
  // Check keyboard utilities
  const keyboardFile = join(__dirname, 'src/utils/keyboard.ts');
  const keyboardContent = readFileSync(keyboardFile, 'utf-8');
  
  if (keyboardContent.includes('getNextCellFromArrow') && keyboardContent.includes('toggleDirection')) {
    log('Keyboard navigation utilities present', 'success');
  }
}

// Main verification
console.log('\n=== TypeScript Types and API Client Verification ===\n');

console.log('1. Checking required files...');
for (const file of REQUIRED_FILES) {
  if (checkFileExists(file)) {
    log(`Found: ${file}`, 'success');
  }
}

console.log('\n2. Checking exports...');
for (const [file, exports] of Object.entries(REQUIRED_EXPORTS)) {
  if (existsSync(join(__dirname, file))) {
    checkExports(file, exports);
  }
}

console.log('\n3. TypeScript compilation...');
runTypeScriptCheck();

console.log('\n4. Import paths...');
checkImportPaths();

console.log('\n5. API configuration...');
checkAPIConfiguration();

console.log('\n6. Custom hooks...');
checkHooks();

console.log('\n7. Utility functions...');
checkUtilities();

// Summary
console.log('\n=== Verification Summary ===\n');
if (errors === 0 && warnings === 0) {
  log('All checks passed! ✨', 'success');
  process.exit(0);
} else {
  if (errors > 0) {
    log(`Found ${errors} error(s)`, 'error');
  }
  if (warnings > 0) {
    log(`Found ${warnings} warning(s)`, 'warning');
  }
  process.exit(errors > 0 ? 1 : 0);
}
