#!/usr/bin/env python3
"""
Script to add global-footer.js script to all HTML pages in the website folder.
This ensures consistent footer across all pages.
"""

import os
import re

WEBSITE_DIR = 'website'

# Script tag to add
FOOTER_SCRIPT = '<script src="js/global-footer.js" defer></script>'

def add_footer_script_to_file(filepath):
    """Add global-footer.js script to an HTML file if not already present."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if global-footer.js is already included
        if 'global-footer.js' in content:
            print(f"  [SKIP] {filepath} - already has global-footer.js")
            return False
        
        # Check if the file has a </body> tag
        if '</body>' not in content:
            print(f"  [SKIP] {filepath} - no </body> tag found")
            return False
        
        # Add the script before </body>
        # Find the position of </body> and insert before it
        modified_content = content.replace('</body>', f'    {FOOTER_SCRIPT}\n</body>')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print(f"  [OK] {filepath} - added global-footer.js")
        return True
    
    except Exception as e:
        print(f"  [ERROR] {filepath} - {str(e)}")
        return False

def main():
    """Main function to process all HTML files."""
    print("Adding global-footer.js to all HTML files...")
    print("-" * 50)
    
    modified_count = 0
    skipped_count = 0
    error_count = 0
    
    # Process all HTML files in the website directory
    for filename in os.listdir(WEBSITE_DIR):
        if filename.endswith('.html'):
            filepath = os.path.join(WEBSITE_DIR, filename)
            result = add_footer_script_to_file(filepath)
            if result:
                modified_count += 1
            elif result is False:
                skipped_count += 1
            else:
                error_count += 1
    
    # Also process subdirectories
    for subdir in ['admin', 'chef-profiles', 'components']:
        subdir_path = os.path.join(WEBSITE_DIR, subdir)
        if os.path.exists(subdir_path):
            for filename in os.listdir(subdir_path):
                if filename.endswith('.html'):
                    filepath = os.path.join(subdir_path, filename)
                    result = add_footer_script_to_file(filepath)
                    if result:
                        modified_count += 1
                    elif result is False:
                        skipped_count += 1
                    else:
                        error_count += 1
    
    print("-" * 50)
    print(f"Summary:")
    print(f"  Modified: {modified_count} files")
    print(f"  Skipped: {skipped_count} files")
    print(f"  Errors: {error_count} files")
    print("Done!")

if __name__ == '__main__':
    main()