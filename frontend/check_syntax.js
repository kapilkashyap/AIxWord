/**
 * Simple syntax checker for TypeScript/JavaScript files.
 * Checks for basic syntax errors without full compilation.
 */

import { readFileSync, readdirSync, statSync } from 'fs';
import { join, extname } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const EXTENSIONS = ['.ts', '.tsx', '.js', '.jsx'];

function getAllFiles(dir, fileList = []) {
  const files = readdirSync(dir);
  
  for (const file of files) {
    const filePath = join(dir, file);
    const stat = statSync(filePath);
    
    if (stat.isDirectory()) {
      if (!file.startsWith('.') && file !== 'node_modules' && file !== 'dist') {
        getAllFiles(filePath, fileList);
      }
    } else {
      if (EXTENSIONS.includes(extname(file))) {
        fileList.push(filePath);
      }
    }
  }
  
  return fileList;
}

function checkSyntax(filePath) {
  try {
    const content = readFileSync(filePath, 'utf-8');
    
    // Basic syntax checks
    const checks = [
      {
        name: 'Balanced braces',
        test: () => {
          const open = (content.match(/{/g) || []).length;
          const close = (content.match(/}/g) || []).length;
          return open === close;
        }
      },
      {
        name: 'Balanced parentheses',
        test: () => {
          const open = (content.match(/\(/g) || []).length;
          const close = (content.match(/\)/g) || []).length;
          return open === close;
        }
      },
      {
        name: 'Balanced brackets',
        test: () => {
          const open = (content.match(/\[/g) || []).length;
          const close = (content.match(/]/g) || []).length;
          return open === close;
        }
      },
      {
        name: 'No trailing commas in imports',
        test: () => {
          return !content.match(/import\s+{[^}]*,\s*}\s+from/);
        }
      }
    ];
    
    const errors = [];
    for (const check of checks) {
      if (!check.test()) {
        errors.push(check.name);
      }
    }
    
    return { valid: errors.length === 0, errors };
  } catch (error) {
    return { valid: false, errors: [error.message] };
  }
}

console.log('🔍 Checking TypeScript/JavaScript syntax...\n');

const srcDir = join(__dirname, 'src');
const files = getAllFiles(srcDir);

let totalFiles = 0;
let validFiles = 0;
let invalidFiles = 0;

for (const file of files) {
  totalFiles++;
  const relativePath = file.replace(__dirname + '/', '');
  const result = checkSyntax(file);
  
  if (result.valid) {
    validFiles++;
    console.log(`✅ ${relativePath}`);
  } else {
    invalidFiles++;
    console.log(`❌ ${relativePath}`);
    for (const error of result.errors) {
      console.log(`   - ${error}`);
    }
  }
}

console.log('\n' + '='.repeat(50));
console.log(`Total files: ${totalFiles}`);
console.log(`Valid: ${validFiles}`);
console.log(`Invalid: ${invalidFiles}`);

if (invalidFiles === 0) {
  console.log('\n✅ All files passed basic syntax checks!');
  console.log('\nNote: This is a basic check. Run "npm install" and "npx tsc --noEmit"');
  console.log('for full TypeScript type checking.');
} else {
  console.log('\n❌ Some files have syntax issues. Please review above.');
  process.exit(1);
}
