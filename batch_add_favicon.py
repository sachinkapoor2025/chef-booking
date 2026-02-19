import os
import re

def add_favicon_to_html(file_path):
    """Add favicon links to an HTML file if not already present."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if favicon already exists
    if 'rel="icon"' in content:
        print(f"  - Favicon already exists, skipping...")
        return False
    
    # Favicon HTML to add
    favicon_html = '''
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="images/logo.jpg">
    <link rel="icon" type="image/png" sizes="32x32" href="images/logo.jpg">
    <link rel="icon" type="image/png" sizes="16x16" href="images/logo.jpg">
    <link rel="apple-touch-icon" sizes="180x180" href="images/logo.jpg">
    <link rel="apple-touch-icon" href="images/logo.jpg">
    <meta name="msapplication-TileImage" content="images/logo.jpg">
'''
    
    # Find the position after the last stylesheet link
    # Look for </style> or <link rel="stylesheet" that comes before </head>
    stylesheet_pattern = r'(<link rel="stylesheet"[^>]*>)'
    matches = list(re.finditer(stylesheet_pattern, content))
    
    if matches:
        # Find the last stylesheet link before </head>
        last_match = None
        for match in matches:
            # Check if this match is before </head>
            before_head = content.find('</head>', match.end())
            if before_head != -1:
                last_match = match
        
        if last_match:
            insert_pos = last_match.end()
            content = content[:insert_pos] + favicon_html + content[insert_pos:]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
    
    return False

def main():
    website_dir = 'website'
    html_files = []
    
    # Walk through all directories
    for root, dirs, files in os.walk(website_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print(f"Found {len(html_files)} HTML files\n")
    
    updated_count = 0
    skipped_count = 0
    
    for file_path in html_files:
        rel_path = os.path.relpath(file_path, '.')
        print(f"Processing: {rel_path}")
        
        try:
            if add_favicon_to_html(file_path):
                print(f"  - ✓ Favicon added successfully!")
                updated_count += 1
            else:
                print(f"  - Skipped (already has favicon)")
                skipped_count += 1
        except Exception as e:
            print(f"  - ✗ Error: {str(e)}")
    
    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  - Files updated: {updated_count}")
    print(f"  - Files skipped (already had favicon): {skipped_count}")
    print(f"  - Total files processed: {len(html_files)}")

if __name__ == "__main__":
    main()
