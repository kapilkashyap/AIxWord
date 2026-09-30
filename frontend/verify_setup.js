/**
 * Verification script to check frontend setup.
 * Run with: node verify_setup.js
 */

import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const REQUIRED_FILES = [
  'package.json',
  'vite.config.ts',
  'tsconfig.json',
  'tsconfig.node.json',
  'index.html',
  'tailwind.config.js',
  'postcss.config.js',
  'vitest.config.ts',
  '.eslintrc.cjs',
  '.env.example',
  '.gitignore',
  'src/main.tsx',
  'src/App.tsx',
  'src/App.css',
  'src/index.css',
  'src/vite-env.d.ts',
  'src/types/puzzle.ts',
  'src/types/api.ts',
  'src/services/api.ts',
  'src/hooks/useAPI.ts',
  'src/hooks/usePuzzle.ts',
  'src/utils/grid.ts',
  'src/utils/validation.ts',
  'src/utils/keyboard.ts',
  'src/test/setup.ts',
  'public/vite.svg',
];

console.log('🔍 Verifying Frontend Setup...\n');

let allPassed = true;

// Check required files
console.log('📁 Checking required files...');
for (const file of REQUIRED_FILES) {
  const filePath = join(__dirname, file);
  const exists = existsSync(filePath);
  const status = exists ? '✅' : '❌';
  console.log(`  ${status} ${file}`);
  if (!exists) allPassed = false;
}

// Check package.json structure
console.log('\n📦 Checking package.json...');
try {
  const packageJson = JSON.parse(readFileSync(join(__dirname, 'package.json'), 'utf-8'));
  
  const requiredScripts = ['dev', 'build', 'preview', 'lint', 'test'];
  for (const script of requiredScripts) {
    const exists = script in packageJson.scripts;
    const status = exists ? '✅' : '❌';
    console.log(`  ${status} Script: ${script}`);
    if (!exists) allPassed = false;
  }
  
  const requiredDeps = ['react', 'react-dom', 'axios'];
  for (const dep of requiredDeps) {
    const exists = dep in packageJson.dependencies;
    const status = exists ? '✅' : '❌';
    console.log(`  ${status} Dependency: ${dep}`);
    if (!exists) allPassed = false;
  }
  
  const requiredDevDeps = ['typescript', 'vite', '@vitejs/plugin-react', 'tailwindcss', 'vitest'];
  for (const dep of requiredDevDeps) {
    const exists = dep in packageJson.devDependencies;
    const status = exists ? '✅' : '❌';
    console.log(`  ${status} Dev Dependency: ${dep}`);
    if (!exists) allPassed = false;
  }
} catch (error) {
  console.log('  ❌ Failed to parse package.json');
  allPassed = false;
}

// Check TypeScript configuration
console.log('\n⚙️  Checking TypeScript configuration...');
try {
  const tsconfigContent = readFileSync(join(__dirname, 'tsconfig.json'), 'utf-8');
  // Remove comments for JSON parsing
  const cleanedContent = tsconfigContent.replace(/\/\*[\s\S]*?\*\/|\/\/.*/g, '');
  const tsconfig = JSON.parse(cleanedContent);
  
  const checks = [
    { name: 'Strict mode enabled', value: tsconfig.compilerOptions?.strict === true },
    { name: 'JSX set to react-jsx', value: tsconfig.compilerOptions?.jsx === 'react-jsx' },
    { name: 'Path aliases configured', value: !!tsconfig.compilerOptions?.paths },
  ];
  
  for (const check of checks) {
    const status = check.value ? '✅' : '❌';
    console.log(`  ${status} ${check.name}`);
    if (!check.value) allPassed = false;
  }
} catch (error) {
  console.log(`  ❌ Failed to parse tsconfig.json: ${error.message}`);
  allPassed = false;
}

// Check Vite configuration
console.log('\n⚡ Checking Vite configuration...');
try {
  const viteConfig = readFileSync(join(__dirname, 'vite.config.ts'), 'utf-8');
  
  const checks = [
    { name: 'React plugin configured', value: viteConfig.includes('@vitejs/plugin-react') },
    { name: 'Path aliases configured', value: viteConfig.includes('alias') },
    { name: 'Proxy configured', value: viteConfig.includes('proxy') },
  ];
  
  for (const check of checks) {
    const status = check.value ? '✅' : '❌';
    console.log(`  ${status} ${check.name}`);
    if (!check.value) allPassed = false;
  }
} catch (error) {
  console.log('  ❌ Failed to read vite.config.ts');
  allPassed = false;
}

// Check Tailwind configuration
console.log('\n🎨 Checking Tailwind configuration...');
try {
  const tailwindConfig = readFileSync(join(__dirname, 'tailwind.config.js'), 'utf-8');
  
  const checks = [
    { name: 'Content paths configured', value: tailwindConfig.includes('content') },
    { name: 'Custom colors defined', value: tailwindConfig.includes('cell-') },
  ];
  
  for (const check of checks) {
    const status = check.value ? '✅' : '❌';
    console.log(`  ${status} ${check.name}`);
    if (!check.value) allPassed = false;
  }
} catch (error) {
  console.log('  ❌ Failed to read tailwind.config.js');
  allPassed = false;
}

// Summary
console.log('\n' + '='.repeat(50));
if (allPassed) {
  console.log('✅ All checks passed! Frontend setup is complete.');
  console.log('\nNext steps:');
  console.log('  1. Run: npm install');
  console.log('  2. Run: npm run dev');
  console.log('  3. Open: http://localhost:5173');
} else {
  console.log('❌ Some checks failed. Please review the output above.');
  process.exit(1);
}
