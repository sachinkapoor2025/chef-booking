#!/usr/bin/env python3
"""
Script to add mobile menu overlay with logo to all HTML pages that have inline headers.
This ensures consistent hamburger menu behavior across all pages.
"""

import os
import re

# Mobile menu overlay HTML to add after </header> tag
MOBILE_MENU_OVERLAY = '''
    <!-- Mobile Menu Overlay with Logo -->
    <div class="mobile-menu-overlay" id="mobile-menu-overlay">
        <div class="mobile-menu-content">
            <div class="mobile-menu-header" style="display: flex; justify-content: space-between; align-items: center; padding: 1.5rem; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white;">
                <div class="logo">
                    <a href="index.html" style="text-decoration: none; color: inherit;">
                        <img src="images/logo.jpg" alt="Maharaja Chef Services Logo" style="height: 50px; width: auto;">
                    </a>
                </div>
                <button class="mobile-menu-close" id="mobile-menu-close" aria-label="Close mobile menu" style="background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3); color: white; font-size: 2rem; cursor: pointer; padding: 0.5rem 0.75rem; border-radius: 8px;">
                    <span>&times;</span>
                </button>
            </div>
            
            <ul class="mobile-nav-menu">
                <li><a href="index.html">Home</a></li>
                <li><a href="catering-services.html">Catering Services</a></li>
                <li><a href="balanced-diet.html">Balanced Diet</a></li>

                <li class="mobile-dropdown">
                    <button class="mobile-dropdown-toggle" aria-expanded="false">
                        Services <span class="mobile-dropdown-arrow">▼</span>
                    </button>
                    <ul class="mobile-dropdown-menu">
                        <li><a href="book-a-chef.html">Book a Chef</a></li>
                        <li><a href="catering-services.html">Catering Services</a></li>
                        <li><a href="balanced-diet.html">Balanced Diet</a></li>
                        <li><a href="weekly-meals.html">Weekly Meal Service</a></li>
                    </ul>
                </li>

                <li class="mobile-dropdown">
                    <button class="mobile-dropdown-toggle" aria-expanded="false">
                        For Chefs <span class="mobile-dropdown-arrow">▼</span>
                    </button>
                    <ul class="mobile-dropdown-menu">
                        <li><a href="become-a-chef.html">Become a Chef</a></li>
                        <li><a href="chef-guidelines.html">Chef Guidelines</a></li>
                        <li><a href="chef-faq.html">Chef FAQ</a></li>
                        <li><a href="success-stories.html">Success Stories</a></li>
                    </ul>
                </li>

                <li class="mobile-dropdown">
                    <button class="mobile-dropdown-toggle" aria-expanded="false">
                        Explore More <span class="mobile-dropdown-arrow">▼</span>
                    </button>
                    <ul class="mobile-dropdown-menu">
                        <li><a href="explore-chefs.html">Explore Chefs</a></li>
                        <li><a href="menu-services.html">Menu Services</a></li>
                        <li><a href="about-us.html">About Us</a></li>
                        <li><a href="blogs.html">Blogs</a></li>
                        <li><a href="gallery.html">Gallery</a></li>
                        <li><a href="faq.html">FAQ</a></li>
                        <li><a href="contact-us.html">Contact Us</a></li>
                    </ul>
                </li>

                <li><a href="owner.html">Business Owner</a></li>
                <li><a href="login.html">Log In</a></li>
            </ul>
        </div>
    </div>

'''

# JavaScript to add before </body>
MOBILE_MENU_SCRIPT = '''
    <!-- Mobile Menu Script -->
    <script>
        (function() {
            const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
            const mobileMenuOverlay = document.getElementById('mobile-menu-overlay');
            const mobileMenuClose = document.getElementById('mobile-menu-close');
            const mobileDropdownToggles = document.querySelectorAll('.mobile-dropdown-toggle');

            if (mobileMenuToggle && mobileMenuOverlay) {
                mobileMenuToggle.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    mobileMenuOverlay.classList.add('active');
                    document.body.style.overflow = 'hidden';
                });
            }

            if (mobileMenuClose && mobileMenuOverlay) {
                mobileMenuClose.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    mobileMenuOverlay.classList.remove('active');
                    document.body.style.overflow = '';
                });
            }

            if (mobileMenuOverlay) {
                mobileMenuOverlay.addEventListener('click', function(e) {
                    if (e.target === mobileMenuOverlay) {
                        mobileMenuOverlay.classList.remove('active');
                        document.body.style.overflow = '';
                    }
                });
            }

            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && mobileMenuOverlay && mobileMenuOverlay.classList.contains('active')) {
                    mobileMenuOverlay.classList.remove('active');
                    document.body.style.overflow = '';
                }
            });

            if (mobileDropdownToggles.length > 0) {
                mobileDropdownToggles.forEach(toggle => {
                    toggle.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        const dropdown = this.closest('.mobile-dropdown');
                        const isActive = dropdown.classList.contains('active');
                        
                        mobileDropdownToggles.forEach(otherToggle => {
                            if (otherToggle !== toggle) {
                                const otherDropdown = otherToggle.closest('.mobile-dropdown');
                                otherDropdown.classList.remove('active');
                                otherToggle.setAttribute('aria-expanded', 'false');
                            }
                        });
                        
                        dropdown.classList.toggle('active');
                        this.setAttribute('aria-expanded', !isActive);
                    });
                });
            }
        })();
    </script>
'''

def update_html_file(filepath):
    """Update an HTML file with mobile menu overlay and script."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file already has mobile menu overlay
        if 'mobile-menu-overlay' in content:
            print(f"  Skipping {filepath} - already has mobile menu overlay")
            return False
        
        # Check if file loads header from component (no inline header)
        if 'components/header.html' in content:
            print(f"  Skipping {filepath} - loads header from component")
            return False
        
        # Check if file has inline header (has mobile-menu-toggle or global-header)
        if 'mobile-menu-toggle' not in content and 'global-header' not in content:
            print(f"  Skipping {filepath} - no inline header found")
            return False
        
        # Fix mobile-menu-toggle ID if it uses different format
        content = content.replace('id="mobileMenuToggle"', 'id="mobile-menu-toggle"')
        
        # Add mobile menu overlay after </header> tag (but before <main>)
        header_pattern = r'(</header>\s*)(<main>)'
        if re.search(header_pattern, content):
            content = re.sub(header_pattern, r'\1\n' + MOBILE_MENU_OVERLAY.strip() + r'\n\2', content)
            print(f"  Added mobile menu overlay to {filepath}")
        else:
            # Try to find any </header> tag
            if '</header>' in content:
                content = content.replace('</header>', '</header>\n' + MOBILE_MENU_OVERLAY.strip())
                print(f"  Added mobile menu overlay to {filepath}")
        
        # Add mobile menu script before </body>
        if '</body>' in content:
            content = content.replace('</body>', MOBILE_MENU_SCRIPT.strip() + '\n</body>')
            print(f"  Added mobile menu script to {filepath}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"  Error processing {filepath}: {e}")
        return False

def main():
    """Main function to update all HTML files in the website directory."""
    website_dir = 'website'
    html_files = []
    
    # Collect all HTML files
    for root, dirs, files in os.walk(website_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                html_files.append(filepath)
    
    print(f"Found {len(html_files)} HTML files")
    
    # Files that are already known to work correctly (load from component)
    skip_files = [
        'components/header.html'  # The source component - already has proper mobile menu
    ]
    
    updated_count = 0
    skipped_count = 0
    
    for filepath in html_files:
        rel_path = os.path.relpath(filepath)
        
        # Skip files that load header from component
        if any(skip in filepath for skip in skip_files):
            skipped_count += 1
            continue
        
        # Check if file has inline header that needs updating
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip files that load from component
            if 'components/header.html' in content:
                print(f"Skipping {rel_path} - loads from component")
                skipped_count += 1
                continue
            
            # Check if file already has mobile menu overlay
            if 'mobile-menu-overlay' in content:
                print(f"Skipping {rel_path} - already has mobile menu")
                skipped_count += 1
                continue
            
            # This file needs updating
            print(f"Updating {rel_path}...")
            if update_html_file(filepath):
                updated_count += 1
            else:
                skipped_count += 1
                
        except Exception as e:
            print(f"Error reading {rel_path}: {e}")
            skipped_count += 1
    
    print(f"\nDone! Updated: {updated_count}, Skipped: {skipped_count}")

if __name__ == '__main__':
    main()
