#!/usr/bin/env python3
"""
Comprehensive script to update all HTML pages with the new header component.
This script ensures consistent mobile navigation across the entire website.
"""

import os
import re
import glob
from pathlib import Path

def update_html_file(file_path):
    """Update a single HTML file with the header component."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip files that already have the header component
        if 'components/header.html' in content and 'global-header.js' in content:
            print(f"✓ {file_path} - Already updated")
            return True
        
        # Skip files that have the old header structure
        if '<header class="global-header">' in content:
            print(f"✓ {file_path} - Already has header structure")
            return True
        
        # Skip files that are not HTML pages (like templates or components)
        if 'components/' in file_path or 'admin/' in file_path:
            print(f"⚠ {file_path} - Skipping component/admin file")
            return True
        
        # Skip the header component file itself
        if file_path.endswith('components/header.html'):
            print(f"⚠ {file_path} - Skipping header component file")
            return True
        
        # Add header component include at the beginning of body
        header_include = '''    <!-- Header Component -->
    <div id="header-container"></div>
    
    <!-- Load Header Script -->
    <script src="js/global-header.js"></script>
    
    <!-- Main Content -->
    <main>'''
        
        # Add closing main tag at the end
        closing_main = '''    </main>
    
    <!-- Footer -->
    <footer>
        <div class="footer-content">
            <div class="footer-column">
                <h3>About Maharaja Chef Services</h3>
                <p>Providing premium chef services for your home and events. We connect you with skilled chefs who bring restaurant-quality dining to your doorstep.</p>
                <div class="social-media">
                    <a href="#"><i class="fab fa-facebook-f"></i></a>
                    <a href="#"><i class="fab fa-twitter"></i></a>
                    <a href="#"><i class="fab fa-instagram"></i></a>
                    <a href="#"><i class="fab fa-linkedin-in"></i></a>
                </div>
            </div>
            <div class="footer-column">
                <h3>Quick Links</h3>
                <ul>
                    <li><a href="index.html">Home</a></li>
                    <li><a href="catering-services.html">Catering Services</a></li>
                    <li><a href="balanced-diet.html">Balanced Diet</a></li>
                    <li><a href="book-a-chef.html">Book a Chef</a></li>
                    <li><a href="become-a-chef.html">Become a Chef</a></li>
                </ul>
            </div>
            <div class="footer-column">
                <h3>Services</h3>
                <ul>
                    <li><a href="weekly-meals.html">Weekly Meal Plans</a></li>
                    <li><a href="special-events.html">Special Events</a></li>
                    <li><a href="explore-chefs.html">Explore Chefs</a></li>
                    <li><a href="contact-us.html">Contact Us</a></li>
                </ul>
            </div>
            <div class="footer-column">
                <h3>Contact Us</h3>
                <div class="contact-info">
                    <div class="contact-item">
                        <div class="contact-icon">
                            <i class="fas fa-map-marker-alt"></i>
                        </div>
                        <div class="contact-details">
                            <h3>Address</h3>
                            <p>123 Chef Street, Culinary District, Food City</p>
                        </div>
                    </div>
                    <div class="contact-item">
                        <div class="contact-icon">
                            <i class="fas fa-phone-alt"></i>
                        </div>
                        <div class="contact-details">
                            <h3>Phone</h3>
                            <p>+1 (555) 123-4567</p>
                        </div>
                    </div>
                    <div class="contact-item">
                        <div class="contact-icon">
                            <i class="fas fa-envelope"></i>
                        </div>
                        <div class="contact-details">
                            <h3>Email</h3>
                            <p>info@maharajachef.com</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <hr>
        <div class="footer-bottom">
            <p>&copy; 2025 Maharaja Chef Services. All rights reserved.</p>
        </div>
    </footer>'''
        
        # Find the body tag and add header after it
        body_pattern = r'(<body[^>]*>)'
        body_match = re.search(body_pattern, content, re.IGNORECASE)
        
        if body_match:
            # Insert header after body tag
            body_end = body_match.end()
            content = content[:body_end] + '\n\n' + header_include + '\n\n' + content[body_end:]
            
            # Find the end of the file and add footer before it
            # Look for common closing patterns
            end_patterns = [
                r'(</body>\s*</html>)',
                r'(</html>)',
                r'(\s*$)'  # End of file
            ]
            
            end_found = False
            for pattern in end_patterns:
                end_match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if end_match:
                    end_pos = end_match.start()
                    content = content[:end_pos] + closing_main + '\n\n' + content[end_pos:]
                    end_found = True
                    break
            
            if not end_found:
                # If no pattern found, just append at the end
                content += '\n\n' + closing_main
        
        # Write the updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ {file_path} - Updated successfully")
        return True
        
    except Exception as e:
        print(f"✗ {file_path} - Error: {str(e)}")
        return False

def find_html_files(directory):
    """Find all HTML files in the directory."""
    html_files = []
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__']]
        
        for file in files:
            if file.endswith('.html') and not file.startswith('.'):
                html_files.append(os.path.join(root, file))
    
    return html_files

def main():
    """Main function to update all HTML files."""
    print("🔧 Updating all HTML pages with header component...")
    print("=" * 60)
    
    # Find all HTML files
    html_files = find_html_files('.')
    
    if not html_files:
        print("No HTML files found!")
        return
    
    print(f"Found {len(html_files)} HTML files to process:")
    for file in html_files:
        print(f"  - {file}")
    
    print("\n" + "=" * 60)
    print("Updating files...")
    
    success_count = 0
    total_count = len(html_files)
    
    for file_path in html_files:
        if update_html_file(file_path):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"Update complete! {success_count}/{total_count} files processed successfully.")
    
    if success_count == total_count:
        print("🎉 All files updated successfully!")
        print("\nNext steps:")
        print("1. Test the updated pages in your browser")
        print("2. Verify the mobile hamburger menu works on all pages")
        print("3. Check that the header appears consistently across all pages")
    else:
        print("⚠️  Some files may need manual attention.")

if __name__ == "__main__":
    main()