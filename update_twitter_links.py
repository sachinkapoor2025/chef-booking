#!/usr/bin/env python
"""
Script to update Twitter links in all HTML files to https://x.com/maharajachef
"""

import os
import re
from pathlib import Path

def update_twitter_links():
    """Update Twitter links in all HTML files"""
    
    # Find all HTML files in the website directory
    website_dir = Path("website")
    html_files = list(website_dir.rglob("*.html"))
    
    print(f"Found {len(html_files)} HTML files")
    
    updated_count = 0
    
    for html_file in html_files:
        try:
            # Read the file content
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if the file contains the old Twitter link pattern
            old_pattern = r'href="https://twitter\.com"[^>]*aria-label="Twitter"'
            new_pattern = 'href="https://x.com/maharajachef" target="_blank" aria-label="Twitter"'
            
            if re.search(old_pattern, content):
                # Replace the old Twitter link with the new one
                updated_content = re.sub(old_pattern, new_pattern, content)
                
                # Write the updated content back to the file
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print(f"Updated: {html_file}")
                updated_count += 1
            else:
                print(f"No Twitter link found in: {html_file}")
                
        except Exception as e:
            print(f"Error processing {html_file}: {e}")
    
    print(f"\nTotal files updated: {updated_count}")

if __name__ == "__main__":
    update_twitter_links()
