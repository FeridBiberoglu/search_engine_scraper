#!/usr/bin/env node

/**
 * This script updates the API_URL in the api.ts file based on environment variables
 * Run this before build to configure the frontend for different environments
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get the directory name using ES modules approach
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Path to the api.ts file
const apiFilePath = path.join(__dirname, 'src', 'api.ts');

// Read the current content
let content = fs.readFileSync(apiFilePath, 'utf8');

// Get API URL from environment or use default
const apiUrl = process.env.API_URL || 'http://localhost:8000';

// Replace the API_URL constant in the file
content = content.replace(
  /const API_URL = ['"](.+)['"];/,
  `const API_URL = '${apiUrl}';`
);

// Write the updated content back
fs.writeFileSync(apiFilePath, content);

console.log(`API URL updated to: ${apiUrl}`); 