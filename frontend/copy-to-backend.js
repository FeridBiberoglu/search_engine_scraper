#!/usr/bin/env node

/**
 * This script copies the built Vite frontend files to the backend's static directory
 * Run this after building the frontend to make it available through the FastAPI backend
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

// Get the directory name using ES modules approach
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths
const distDir = path.join(__dirname, 'dist');
const staticDir = path.join(__dirname, '..', 'autoscraper', 'static', 'frontend');
const indexTemplate = path.join(__dirname, '..', 'autoscraper', 'templates', 'frontend.html');

// Check if dist directory exists
if (!fs.existsSync(distDir)) {
  console.error('Error: dist directory does not exist. Run "npm run build" first.');
  process.exit(1);
}

// Create static/frontend directory if it doesn't exist
if (!fs.existsSync(staticDir)) {
  console.log(`Creating directory: ${staticDir}`);
  fs.mkdirSync(staticDir, { recursive: true });
}

// Clean the static directory
console.log('Cleaning static directory...');
try {
  execSync(`rm -rf ${staticDir}/*`);
} catch (error) {
  console.log('No files to clean or error during cleaning (continuing anyway)');
}

// Copy all files from dist to static/frontend
console.log('Copying files to static directory...');
try {
  execSync(`cp -R ${distDir}/* ${staticDir}/`);
  console.log('Files copied successfully!');
} catch (error) {
  console.error('Error copying files:', error.message);
  process.exit(1);
}

// Create the templates directory if it doesn't exist
const templatesDir = path.join(__dirname, '..', 'autoscraper', 'templates');
if (!fs.existsSync(templatesDir)) {
  console.log(`Creating directory: ${templatesDir}`);
  fs.mkdirSync(templatesDir, { recursive: true });
}

// Check if we need to create a template file to serve the frontend
if (!fs.existsSync(indexTemplate)) {
  console.log('Creating frontend template file...');
  
  // Read the index.html from dist
  const indexHtml = fs.readFileSync(path.join(distDir, 'index.html'), 'utf8');
  
  // Modify paths to point to the static directory
  const modifiedHtml = indexHtml
    .replace(/(src|href)="\//g, '$1="/static/frontend/')
    .replace('<title>Vite + React + TS</title>', '<title>AutoScraper</title>');
  
  // Write the modified HTML to the templates directory
  fs.writeFileSync(indexTemplate, modifiedHtml);
  console.log('Frontend template created!');
}

console.log('Frontend integration complete!'); 