#!/usr/bin/env python3
"""
Script to update Facebook links in all HTML files to the correct URL.
"""

import os
import re
from pathlib import Path

def update_facebook_links():
    """Update Facebook links in all HTML files."""
    
    # The correct Facebook link
    correct_facebook_link = "https://www.facebook.com/profile.php?id=61587294953271"
    
    # Patterns to match different variations of Facebook links
    facebook_patterns = [
        r'href="https://facebook\.com"',
        r'href="https://www\.facebook\.com"',
        r'href="https://www\.facebook\.com/"',
        r'href="https://www\.facebook\.com/profile\.php\?id=[0-9]+"',
        r'href="https://m\.facebook\.com"',
        r'href="https://business\.facebook\.com"',
    ]
    
    # Get all HTML files in the website directory
    website_dir = Path("website")
    html_files = []
    
    # Find all .html files recursively
    for file_path in website_dir.rglob("*.html"):
        html_files.append(file_path)
    
    print(f"Found {len(html_files)} HTML files to check...")
    
    updated_files = []
    
    for html_file in html_files:
        try:
            # Read the file content
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if the file contains any Facebook links that need updating
            original_content = content
            updated = False
            
            # Check if the correct link is already present
            if correct_facebook_link in content:
                print(f"✓ {html_file.relative_to(website_dir)} - Already has correct Facebook link")
                continue
            
            # Look for incorrect Facebook links and replace them
            for pattern in facebook_patterns:
                if re.search(pattern, content):
                    # Replace with the correct link
                    content = re.sub(pattern, f'href="{correct_facebook_link}"', content)
                    updated = True
            
            # If we made changes, write the file back
            if updated:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                updated_files.append(html_file)
                print(f"✓ {html_file.relative_to(website_dir)} - Updated Facebook link")
            else:
                print(f"• {html_file.relative_to(website_dir)} - No Facebook link found")
                
        except Exception as e:
            print(f"✗ Error processing {html_file}: {e}")
    
    print(f"\nSummary:")
    print(f"Total files processed: {len(html_files)}")
    print(f"Files updated: {len(updated_files)}")
    
    if updated_files:
        print(f"\nUpdated files:")
        for file_path in updated_files:
            print(f"  - {file_path.relative_to(website_dir)}")
    
    return updated_files

if __name__ == "__main__":
    print("Updating Facebook links in all HTML files...")
    print("=" * 50)
    
    updated_files = update_facebook_links()
    
    if updated_files:
        print(f"\n✅ Successfully updated Facebook links in {len(updated_files)} files!")
    else:
        print("\nℹ️  No files needed updating or no Facebook links found.")