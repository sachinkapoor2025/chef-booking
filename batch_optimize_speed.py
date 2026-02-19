"""
Batch Speed Optimization Script
Adds lazy-loading to images and defer to scripts across all HTML files
"""
import os
import re

def optimize_html_file(filepath):
    """Optimize a single HTML file for speed"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # 1. Add loading="lazy" to images that don't have it
        # Pattern to find <img tags without loading attribute
        img_pattern = r'<img([^>]*)(?<!loading=")(?<!loading=)(?:\s|>)'
        
        def add_lazy_loading(match):
            img_tag = match.group(0)
            # Check if already has loading attribute
            if 'loading=' in img_tag:
                return img_tag
            # Add loading="lazy" before the closing >
            if img_tag.endswith('/>'):
                return img_tag[:-2] + ' loading="lazy"/>'
            elif img_tag.endswith('>'):
                return img_tag[:-1] + ' loading="lazy">'
            return img_tag
        
        content = re.sub(img_pattern, add_lazy_loading, content)
        
        # 2. Add defer to script tags that don't have defer or async
        script_pattern = r'<script([^>]*)(?<!defer)(?<!async)(?:\s|>)'
        
        def add_defer(match):
            script_tag = match.group(0)
            # Check if already has defer or async
            if 'defer=' in script_tag or 'async=' in script_tag:
                return script_tag
            # Add defer before the closing >
            if script_tag.endswith('/>'):
                return script_tag[:-2] + ' defer/>'
            elif script_tag.endswith('>'):
                return script_tag[:-1] + ' defer>'
            return script_tag
        
        content = re.sub(script_pattern, add_defer, content)
        
        # Only write if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Optimized: {filepath}")
            return True
        return False
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Process all HTML files in the website directory"""
    website_dir = "website"
    html_files = []
    
    # Find all HTML files
    for root, dirs, files in os.walk(website_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print(f"Found {len(html_files)} HTML files")
    
    optimized_count = 0
    for filepath in html_files:
        if optimize_html_file(filepath):
            optimized_count += 1
    
    print(f"\nOptimization complete! Optimized {optimized_count} out of {len(html_files)} files.")

if __name__ == "__main__":
    main()
