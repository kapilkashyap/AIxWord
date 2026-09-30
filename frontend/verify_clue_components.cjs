/**
 * Verification script for Clue Display components.
 * 
 * This script verifies that:
 * 1. All component files exist
 * 2. All CSS module files exist
 * 3. TypeScript declaration files exist
 * 4. Components are properly exported
 * 5. No TypeScript errors in component files
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔍 Verifying Clue Display Components...\n');

// Check if files exist
console.log('📁 Checking file existence...');
const files = [
  'src/components/ClueItem.tsx',
  'src/components/ClueItem.module.css',
  'src/components/ClueItem.module.css.d.ts',
  'src/components/ClueList.tsx',
  'src/components/ClueList.module.css',
  'src/components/ClueList.module.css.d.ts',
  'src/components/ClueList.example.tsx',
  'src/components/index.ts'
];

let allFilesExist = true;
files.forEach(file => {
  const exists = fs.existsSync(file);
  console.log(`  ${exists ? '✓' : '✗'} ${file}`);
  if (!exists) allFilesExist = false;
});

if (!allFilesExist) {
  console.error('\n❌ Some files are missing!');
  process.exit(1);
}

console.log('\n✓ All files exist!\n');

// Check exports
console.log('📦 Checking exports...');
const indexContent = fs.readFileSync('src/components/index.ts', 'utf8');
const expectedExports = [
  'ClueList',
  'ClueListProps',
  'ClueItem',
  'ClueItemProps'
];

let allExportsFound = true;
expectedExports.forEach(exp => {
  const found = indexContent.includes(exp);
  console.log(`  ${found ? '✓' : '✗'} ${exp}`);
  if (!found) allExportsFound = false;
});

if (!allExportsFound) {
  console.error('\n❌ Some exports are missing!');
  process.exit(1);
}

console.log('\n✓ All exports found!\n');

// Check TypeScript compilation
console.log('🔧 Checking TypeScript compilation...');
try {
  execSync('npx tsc --noEmit', { stdio: 'pipe' });
  console.log('  ✓ No TypeScript errors\n');
} catch (error) {
  console.error('  ✗ TypeScript errors found:');
  console.error(error.stdout.toString());
  process.exit(1);
}

// Check linting
console.log('🧹 Checking ESLint...');
try {
  execSync('npm run lint', { stdio: 'pipe' });
  console.log('  ✓ No linting errors\n');
} catch (error) {
  console.error('  ✗ Linting errors found:');
  console.error(error.stdout.toString());
  process.exit(1);
}

// Verify component structure
console.log('🏗️  Verifying component structure...');

// Check ClueItem.tsx
const clueItemContent = fs.readFileSync('src/components/ClueItem.tsx', 'utf8');
const clueItemChecks = [
  { name: 'ClueItemProps interface', pattern: /export interface ClueItemProps/ },
  { name: 'ClueItem component', pattern: /export const ClueItem: React\.FC<ClueItemProps>/ },
  { name: 'CSS module import', pattern: /import styles from '\.\/ClueItem\.module\.css'/ },
  { name: 'Clue type import', pattern: /import type \{.*Clue.*\} from '\.\.\/types\/puzzle'/ },
];

let clueItemValid = true;
clueItemChecks.forEach(check => {
  const found = check.pattern.test(clueItemContent);
  console.log(`  ${found ? '✓' : '✗'} ClueItem: ${check.name}`);
  if (!found) clueItemValid = false;
});

// Check ClueList.tsx
const clueListContent = fs.readFileSync('src/components/ClueList.tsx', 'utf8');
const clueListChecks = [
  { name: 'ClueListProps interface', pattern: /export interface ClueListProps/ },
  { name: 'ClueList component', pattern: /export const ClueList: React\.FC<ClueListProps>/ },
  { name: 'CSS module import', pattern: /import styles from '\.\/ClueList\.module\.css'/ },
  { name: 'ClueItem import', pattern: /import \{ ClueItem \} from '\.\/ClueItem'/ },
  { name: 'Type imports', pattern: /import type \{.*Clue.*Cell.*Direction.*\} from '\.\.\/types\/puzzle'/ },
];

let clueListValid = true;
clueListChecks.forEach(check => {
  const found = check.pattern.test(clueListContent);
  console.log(`  ${found ? '✓' : '✗'} ClueList: ${check.name}`);
  if (!found) clueListValid = false;
});

if (!clueItemValid || !clueListValid) {
  console.error('\n❌ Component structure validation failed!');
  process.exit(1);
}

console.log('\n✓ Component structure validated!\n');

// Summary
console.log('═══════════════════════════════════════════════════════');
console.log('✅ All verifications passed!');
console.log('═══════════════════════════════════════════════════════');
console.log('\nClue Display Components are ready to use:');
console.log('  • ClueItem: Individual clue display component');
console.log('  • ClueList: Container for all clues with tabs/split layout');
console.log('\nExample usage:');
console.log('  import { ClueList, ClueItem } from "./components";');
console.log('\nSee ClueList.example.tsx for a complete integration example.');
console.log('');
