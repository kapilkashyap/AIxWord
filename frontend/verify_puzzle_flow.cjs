#!/usr/bin/env node

/**
 * Verification script for Puzzle Generation UI Flow
 * 
 * This script verifies that all components for the puzzle generation
 * and solving flow are properly created and integrated.
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Verifying Puzzle Generation UI Flow...\n');

let allChecksPass = true;

// Check 1: Component files exist
console.log('📁 Checking component files...');
const componentFiles = [
  'src/components/PuzzleGeneratorForm.tsx',
  'src/components/PuzzleGeneratorForm.module.css',
  'src/components/PuzzleGeneratorForm.module.css.d.ts',
  'src/components/GenerationProgress.tsx',
  'src/components/GenerationProgress.module.css',
  'src/components/GenerationProgress.module.css.d.ts',
  'src/components/PuzzleActions.tsx',
  'src/components/PuzzleActions.module.css',
  'src/components/PuzzleActions.module.css.d.ts',
  'src/components/PuzzleContainer.tsx',
  'src/components/PuzzleContainer.module.css',
  'src/components/PuzzleContainer.module.css.d.ts',
];

componentFiles.forEach(file => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    console.log(`  ✓ ${file}`);
  } else {
    console.log(`  ✗ ${file} - NOT FOUND`);
    allChecksPass = false;
  }
});

// Check 2: Exports in index.ts
console.log('\n📦 Checking component exports...');
const indexPath = path.join(__dirname, 'src/components/index.ts');
const indexContent = fs.readFileSync(indexPath, 'utf8');

const expectedExports = [
  'PuzzleGeneratorForm',
  'PuzzleGeneratorFormProps',
  'GenerationProgress',
  'GenerationProgressProps',
  'PuzzleActions',
  'PuzzleActionsProps',
  'PuzzleContainer',
  'PuzzleContainerProps',
];

expectedExports.forEach(exp => {
  if (indexContent.includes(exp)) {
    console.log(`  ✓ ${exp}`);
  } else {
    console.log(`  ✗ ${exp} - NOT EXPORTED`);
    allChecksPass = false;
  }
});

// Check 3: App.tsx integration
console.log('\n🔗 Checking App.tsx integration...');
const appPath = path.join(__dirname, 'src/App.tsx');
const appContent = fs.readFileSync(appPath, 'utf8');

if (appContent.includes('PuzzleContainer')) {
  console.log('  ✓ PuzzleContainer is used in App.tsx');
} else {
  console.log('  ✗ PuzzleContainer is NOT used in App.tsx');
  allChecksPass = false;
}

if (appContent.includes("import { PuzzleContainer } from './components'")) {
  console.log('  ✓ Import statement is correct');
} else {
  console.log('  ✗ Import statement is incorrect');
  allChecksPass = false;
}

// Check 4: TypeScript compilation
console.log('\n🔧 Checking TypeScript compilation...');
const { execSync } = require('child_process');

try {
  execSync('npx tsc --noEmit', { cwd: __dirname, stdio: 'pipe' });
  console.log('  ✓ TypeScript compilation successful');
} catch (error) {
  console.log('  ✗ TypeScript compilation failed');
  console.log('  Error:', error.stdout?.toString() || error.message);
  allChecksPass = false;
}

// Check 5: Component structure
console.log('\n🏗️  Checking component structure...');

const checkComponentStructure = (componentName, filePath) => {
  const content = fs.readFileSync(filePath, 'utf8');
  
  const checks = [
    { name: 'Has interface/type definition', test: content.includes(`${componentName}Props`) },
    { name: 'Has React.FC declaration', test: content.includes(`React.FC<${componentName}Props>`) },
    { name: 'Has export', test: content.includes(`export const ${componentName}`) || content.includes(`export default ${componentName}`) },
    { name: 'Has data-testid', test: content.includes('data-testid') },
  ];
  
  console.log(`  ${componentName}:`);
  checks.forEach(check => {
    if (check.test) {
      console.log(`    ✓ ${check.name}`);
    } else {
      console.log(`    ✗ ${check.name}`);
      allChecksPass = false;
    }
  });
};

checkComponentStructure('PuzzleGeneratorForm', path.join(__dirname, 'src/components/PuzzleGeneratorForm.tsx'));
checkComponentStructure('GenerationProgress', path.join(__dirname, 'src/components/GenerationProgress.tsx'));
checkComponentStructure('PuzzleActions', path.join(__dirname, 'src/components/PuzzleActions.tsx'));
checkComponentStructure('PuzzleContainer', path.join(__dirname, 'src/components/PuzzleContainer.tsx'));

// Check 6: API integration
console.log('\n🌐 Checking API integration...');
const containerPath = path.join(__dirname, 'src/components/PuzzleContainer.tsx');
const containerContent = fs.readFileSync(containerPath, 'utf8');

const apiCalls = [
  'apiClient.generatePuzzle',
  'apiClient.solvePuzzle',
  'apiClient.solveWord',
  'apiClient.getHint',
  'apiClient.validateSolution',
];

apiCalls.forEach(call => {
  if (containerContent.includes(call)) {
    console.log(`  ✓ ${call}`);
  } else {
    console.log(`  ✗ ${call} - NOT FOUND`);
    allChecksPass = false;
  }
});

// Check 7: Hook usage
console.log('\n🪝 Checking hook usage...');
const hooks = [
  'usePuzzle',
  'useAPI',
  'useMultiAPI',
];

hooks.forEach(hook => {
  if (containerContent.includes(hook)) {
    console.log(`  ✓ ${hook}`);
  } else {
    console.log(`  ✗ ${hook} - NOT USED`);
    allChecksPass = false;
  }
});

// Final result
console.log('\n' + '='.repeat(50));
if (allChecksPass) {
  console.log('✅ All checks passed! Puzzle Generation UI Flow is ready.');
  console.log('\nYou can now:');
  console.log('  1. Run: npm run dev');
  console.log('  2. Open: http://localhost:5173');
  console.log('  3. Generate a puzzle and test the flow');
  process.exit(0);
} else {
  console.log('❌ Some checks failed. Please review the errors above.');
  process.exit(1);
}
