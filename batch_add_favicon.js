const fs = require('fs');
const path = require('path');

function addFaviconToHtml(filePath) {
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Check if favicon already exists
    if (content.includes('rel="icon"')) {
        console.log('  - Favicon already exists, skipping...');
        return false;
    }
    
    // Favicon HTML to add
    const faviconHtml = `
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="images/logo.jpg">
    <link rel="icon" type="image/png" sizes="32x32" href="images/logo.jpg">
    <link rel="icon" type="image/png" sizes="16x16" href="images/logo.jpg">
    <link rel="apple-touch-icon" sizes="180x180" href="images/logo.jpg">
    <link rel="apple-touch-icon" href="images/logo.jpg">
    <meta name="msapplication-TileImage" content="images/logo.jpg">
`;
    
    // Find the last stylesheet link before </head>
    const stylesheetRegex = /<link rel="stylesheet"[^>]*>/g;
    let matches;
    let lastMatch = null;
    let lastMatchEnd = 0;
    
    while ((matches = stylesheetRegex.exec(content)) !== null) {
        const beforeHead = content.indexOf('</head>', matches.index + matches[0].length);
        if (beforeHead !== -1) {
            lastMatch = matches[0];
            lastMatchEnd = matches.index + matches[0].length;
        }
    }
    
    if (lastMatch) {
        content = content.slice(0, lastMatchEnd) + faviconHtml + content.slice(lastMatchEnd);
        fs.writeFileSync(filePath, content, 'utf8');
        return true;
    }
    
    return false;
}

function walkDir(dir, callback) {
    fs.readdirSync(dir).forEach(f => {
        const filePath = path.join(dir, f);
        if (fs.statSync(filePath).isDirectory()) {
            walkDir(filePath, callback);
        } else if (f.endsWith('.html')) {
            callback(filePath);
        }
    });
}

console.log('Adding favicon to all HTML files...\n');

let updatedCount = 0;
let skippedCount = 0;

walkDir('website', (filePath) => {
    const relPath = path.relative('.', filePath);
    console.log(`Processing: ${relPath}`);
    
    try {
        if (addFaviconToHtml(filePath)) {
            console.log('  - ✓ Favicon added successfully!');
            updatedCount++;
        } else {
            console.log('  - Skipped (already has favicon)');
            skippedCount++;
        }
    } catch (e) {
        console.log(`  - ✗ Error: ${e.message}`);
    }
});

console.log(`\n${'='.repeat(50)}`);
console.log('Summary:');
console.log(`  - Files updated: ${updatedCount}`);
console.log(`  - Files skipped: ${skippedCount}`);
