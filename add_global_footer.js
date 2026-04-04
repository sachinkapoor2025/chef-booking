#!/usr/bin/env node
/**
 * Script to add global-footer.js script to all HTML pages in the website folder.
 * This ensures consistent footer across all pages.
 */

const fs = require('fs');
const path = require('path');

const WEBSITE_DIR = 'website';

// Script tag to add
const FOOTER_SCRIPT = '<script src="js/global-footer.js" defer></script>';

function addFooterScriptToFile(filepath) {
    try {
        let content = fs.readFileSync(filepath, 'utf8');
        
        // Check if global-footer.js is already included
        if (content.includes('global-footer.js')) {
            console.log(`  [SKIP] ${filepath} - already has global-footer.js`);
            return false;
        }
        
        // Check if the file has a </body> tag
        if (!content.includes('</body>')) {
            console.log(`  [SKIP] ${filepath} - no </body> tag found`);
            return false;
        }
        
        // Add the script before </body>
        const modifiedContent = content.replace('</body>', `    ${FOOTER_SCRIPT}\n</body>`);
        
        fs.writeFileSync(filepath, modifiedContent, 'utf8');
        
        console.log(`  [OK] ${filepath} - added global-footer.js`);
        return true;
    } catch (error) {
        console.log(`  [ERROR] ${filepath} - ${error.message}`);
        return null;
    }
}

function main() {
    console.log('Adding global-footer.js to all HTML files...');
    console.log('-'.repeat(50));
    
    let modifiedCount = 0;
    let skippedCount = 0;
    let errorCount = 0;
    
    // Process all HTML files in the website directory
    const files = fs.readdirSync(WEBSITE_DIR);
    for (const filename of files) {
        if (filename.endsWith('.html')) {
            const filepath = path.join(WEBSITE_DIR, filename);
            const result = addFooterScriptToFile(filepath);
            if (result === true) modifiedCount++;
            else if (result === false) skippedCount++;
            else errorCount++;
        }
    }
    
    // Also process subdirectories
    const subdirs = ['admin', 'chef-profiles', 'components'];
    for (const subdir of subdirs) {
        const subdirPath = path.join(WEBSITE_DIR, subdir);
        if (fs.existsSync(subdirPath)) {
            const subFiles = fs.readdirSync(subdirPath);
            for (const filename of subFiles) {
                if (filename.endsWith('.html')) {
                    const filepath = path.join(subdirPath, filename);
                    const result = addFooterScriptToFile(filepath);
                    if (result === true) modifiedCount++;
                    else if (result === false) skippedCount++;
                    else errorCount++;
                }
            }
        }
    }
    
    console.log('-'.repeat(50));
    console.log('Summary:');
    console.log(`  Modified: ${modifiedCount} files`);
    console.log(`  Skipped: ${skippedCount} files`);
    console.log(`  Errors: ${errorCount} files`);
    console.log('Done!');
}

main();