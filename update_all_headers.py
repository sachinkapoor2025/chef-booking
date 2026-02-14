#!/usr/bin/env python3
"""
Script to update all HTML pages with the global header structure.
Adds:
1. <div id="header-container"></div> after <body> tag
2. Scripts js/global-header.js and js/header.js before closing </body>
3. Removes old hardcoded <header> elements
"""

import os
import re
from pathlib import Path

def update_html_file(filepath):
    """Update a single HTML file with global header structure."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        changes = []
        
        # Skip if already has header-container (assume it's already updated)
        if 'id="header-container"' in content:
            print(f"  ⏭️  Skipping {filepath.name} - already has header-container")
            return False
        
        # 1. Add header-container div after <body> tag if not present
        if 'id="header-container"' not in content:
            # Find <body> tag (handle attributes)
            body_pattern = r'(<body[^>]*>)'
            body_match = re.search(body_pattern, content, re.IGNORECASE)
            
            if body_match:
                body_tag = body_match.group(1)
                # Check if there's already a header comment or similar
                header_container_html = '\n    <!-- Global Header will be loaded here -->\n    <div id="header-container"></div>\n'
                
                # Insert after body tag
                content = re.sub(body_pattern, body_tag + header_container_html, content, count=1, flags=re.IGNORECASE)
                changes.append("Added header-container div")
        
        # 2. Remove old hardcoded <header> elements (but be careful not to remove <header> inside articles/sections)
        # Look for header that contains navigation or logo
        header_pattern = r'<header[^>]*>[\s\S]*?</header>'
        headers_found = re.findall(header_pattern, content, re.IGNORECASE)
        
        for header in headers_found:
            # Only remove if it contains nav-related content
            if any(keyword in header.lower() for keyword in ['nav', 'menu', 'logo', 'hamburger', 'navigation', 'home', 'services', 'about']):
                content = content.replace(header, '')
                changes.append("Removed old hardcoded header")
                break  # Remove only the main header
        
        # 3. Add required scripts before closing </body> if not present
        scripts_to_add = [
            '<script src="js/global-header.js"></script>',
            '<script src="js/header.js"></script>'
        ]
        
        # Check if scripts are already present
        if 'js/global-header.js' not in content:
            # Find the closing body tag and insert scripts before it
            # Look for existing script tags before </body>
            script_section = '\n    ' + '\n    '.join(scripts_to_add) + '\n'
            
            # Try to find </body> tag
            body_end_pattern = r'(</body>)'
            if re.search(body_end_pattern, content, re.IGNORECASE):
                content = re.sub(body_end_pattern, script_section + r'\1', content, count=1, flags=re.IGNORECASE)
                changes.append("Added global-header scripts")
        
        # 4. Also check if there's a </body> with scripts already and we need to add before those
        # Find the last </script> before </body> and add after it
        if 'js/global-header.js' not in content:
            # Try finding position before </body>
            body_end_pos = content.lower().find('</body>')
            if body_end_pos != -1:
                script_section = '\n    ' + '\n    '.join(scripts_to_add) + '\n'
                content = content[:body_end_pos] + script_section + content[body_end_pos:]
                changes.append("Added global-header scripts")
        
        # Write changes if any were made
        if changes and content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Updated {filepath.name}: {', '.join(changes)}")
            return True
        else:
            print(f"  ⏭️  No changes needed for {filepath.name}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error updating {filepath}: {e}")
        return False

def main():
    website_dir = Path('website')
    
    # Get all HTML files recursively
    html_files = list(website_dir.rglob('*.html'))
    
    print(f"Found {len(html_files)} HTML files to process\n")
    
    updated_count = 0
    skipped_count = 0
    
    for html_file in sorted(html_files):
        # Skip test files if needed
        if 'test-' in html_file.name.lower():
            print(f"⏭️  Skipping test file: {html_file.name}")
            skipped_count += 1
            continue
            
        print(f"Processing: {html_file.relative_to(website_dir)}")
        if update_html_file(html_file):
            updated_count += 1
        print()
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total files: {len(html_files)}")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped (test files): {skipped_count}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
