#!/usr/bin/env node

/**
 * Verification script for Grid UI Components
 * 
 * This script verifies that:
 * 1. All component files exist
 * 2. TypeScript compilation succeeds
 * 3. Component exports are correct
 * 4. CSS files are present
 * 5. No syntax errors
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔍 Verifying Grid UI Components...\n');

let hasErrors = false;

// Check if files exist
const requiredFiles = [
  'src/components/CrosswordGrid.tsx',
  'src/components/GridCell.tsx',
  'src/components/CrosswordGrid.css',
  'src/components/index.ts',
  'src/components/CrosswordGrid.example.tsx',
];

console.log('📁 Checking required files...');
requiredFiles.forEach(file => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    console.log(`  ✓ ${file}`);
  } else {
    console.log(`  ✗ ${file} - MISSING`);
    hasErrors = true;
  }
});

// Check TypeScript compilation
console.log('\n🔨 Checking TypeScript compilation...');
try {
  execSync('npx tsc --noEmit', { stdio: 'pipe', cwd: __dirname });
  console.log('  ✓ TypeScript compilation successful');
} catch (error) {
  console.log('  ✗ TypeScript compilation failed');
  console.log(error.stdout?.toString() || error.message);
  hasErrors = true;
}

// Check component exports
console.log('\n📦 Checking component exports...');
try {
  const indexContent = fs.readFileSync(
    path.join(__dirname, 'src/components/index.ts'),
    'utf8'
  );
  
  const expectedExports = [
    'CrosswordGrid',
    'CrosswordGridProps',
    'GridCell',
    'GridCellProps',
  ];
  
  expectedExports.forEach(exportName => {
    if (indexContent.includes(exportName)) {
      console.log(`  ✓ ${exportName} exported`);
    } else {
      console.log(`  ✗ ${exportName} - NOT EXPORTED`);
      hasErrors = true;
    }
  });
} catch (error) {
  console.log('  ✗ Failed to read index.ts');
  hasErrors = true;
}

// Check CSS file content
console.log('\n🎨 Checking CSS file...');
try {
  const cssContent = fs.readFileSync(
    path.join(__dirname, 'src/components/CrosswordGrid.css'),
    'utf8'
  );
  
  const requiredClasses = [
    '.crossword-grid-container',
    '.crossword-grid',
    '.grid-cell',
    '.grid-cell--selected',
    '.grid-cell--active-word',
    '.grid-cell--blocked',
    '.grid-cell__number',
    '.grid-cell__input',
    '.direction-indicator',
  ];
  
  requiredClasses.forEach(className => {
    if (cssContent.includes(className)) {
      console.log(`  ✓ ${className} defined`);
    } else {
      console.log(`  ✗ ${className} - NOT DEFINED`);
      hasErrors = true;
    }
  });
} catch (error) {
  console.log('  ✗ Failed to read CSS file');
  hasErrors = true;
}

// Check component structure
console.log('\n🏗️  Checking component structure...');
try {
  const gridContent = fs.readFileSync(
    path.join(__dirname, 'src/components/CrosswordGrid.tsx'),
    'utf8'
  );
  
  const requiredFeatures = [
    { name: 'CrosswordGridProps interface', pattern: /export interface CrosswordGridProps/ },
    { name: 'CrosswordGrid component', pattern: /export const CrosswordGrid.*React\.FC/ },
    { name: 'Cell selection handling', pattern: /handleCellClick/ },
    { name: 'Cell input handling', pattern: /handleCellInput/ },
    { name: 'Keyboard navigation', pattern: /handleKeyDown/ },
    { name: 'Direction toggle', pattern: /toggleDirection/ },
    { name: 'Active word highlighting', pattern: /is_active_word/ },
  ];
  
  requiredFeatures.forEach(({ name, pattern }) => {
    if (pattern.test(gridContent)) {
      console.log(`  ✓ ${name}`);
    } else {
      console.log(`  ✗ ${name} - NOT FOUND`);
      hasErrors = true;
    }
  });
} catch (error) {
  console.log('  ✗ Failed to read CrosswordGrid.tsx');
  hasErrors = true;
}

// Check GridCell component
console.log('\n🔲 Checking GridCell component...');
try {
  const cellContent = fs.readFileSync(
    path.join(__dirname, 'src/components/GridCell.tsx'),
    'utf8'
  );
  
  const requiredFeatures = [
    { name: 'GridCellProps interface', pattern: /export interface GridCellProps/ },
    { name: 'GridCell component', pattern: /export const GridCell.*React\.FC/ },
    { name: 'Click handling', pattern: /handleClick/ },
    { name: 'Input handling', pattern: /handleChange/ },
    { name: 'Focus management', pattern: /useRef.*HTMLInputElement/ },
    { name: 'Cell number display', pattern: /cell\.number/ },
    { name: 'Blocked cell rendering', pattern: /is_blocked/ },
  ];
  
  requiredFeatures.forEach(({ name, pattern }) => {
    if (pattern.test(cellContent)) {
      console.log(`  ✓ ${name}`);
    } else {
      console.log(`  ✗ ${name} - NOT FOUND`);
      hasErrors = true;
    }
  });
} catch (error) {
  console.log('  ✗ Failed to read GridCell.tsx');
  hasErrors = true;
}

// Check integration with utilities
console.log('\n🔧 Checking utility integration...');
try {
  const gridContent = fs.readFileSync(
    path.join(__dirname, 'src/components/CrosswordGrid.tsx'),
    'utf8'
  );
  
  const requiredImports = [
    { name: 'Grid utilities', pattern: /from '\.\.\/utils\/grid'/ },
    { name: 'Keyboard utilities', pattern: /from '\.\.\/utils\/keyboard'/ },
    { name: 'Type imports', pattern: /from '\.\.\/types\/puzzle'/ },
    { name: 'GridCell import', pattern: /from '\.\/GridCell'/ },
  ];
  
  requiredImports.forEach(({ name, pattern }) => {
    if (pattern.test(gridContent)) {
      console.log(`  ✓ ${name}`);
    } else {
      console.log(`  ✗ ${name} - NOT IMPORTED`);
      hasErrors = true;
    }
  });
} catch (error) {
  console.log('  ✗ Failed to check imports');
  hasErrors = true;
}

// Final summary
console.log('\n' + '='.repeat(50));
if (hasErrors) {
  console.log('❌ Verification FAILED - Please fix the errors above');
  process.exit(1);
} else {
  console.log('✅ All verifications PASSED!');
  console.log('\n📋 Summary:');
  console.log('  • All required files present');
  console.log('  • TypeScript compilation successful');
  console.log('  • Component exports correct');
  console.log('  • CSS classes defined');
  console.log('  • Component structure valid');
  console.log('  • Utility integration correct');
  console.log('\n🎉 Grid UI Components are ready to use!');
  process.exit(0);
}
