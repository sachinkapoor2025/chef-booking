#!/usr/bin/env python3
"""Add global header with hamburger menu to all pages"""

import os
import re

# Pages to update
PAGES = [
    'website/catering-services.html',
    'website/balanced-diet.html',
    'website/services.html',
    'website/book-a-chef.html',
    'website/weekly-meals.html',
    'website/become-a-chef.html',
    'website/chef-guidelines.html',
    'website/chef-faq.html',
    'website/success-stories.html',
    'website/explore-chefs.html',
    'website/menu-services.html',
    'website/about-us.html',
    'website/blogs.html',
    'website/gallery.html',
    'website/contact-us.html',
    'website/faq.html',
    'website/owner.html',
    'website/login.html'
]

# Styles needed for global header (from index.html)
HEADER_STYLES = '''    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preload" href="css/style.css" as="style">
    <link rel="preload" href="js/script.js" as="script">
    
    <!-- Global Header Styles -->
    <style>
        /* Global Header Styles - Optimized for Fast Loading */
        .global-header {
            background-color: #ffffff;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
            will-change: transform;
        }

        .global-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }

        .global-nav .logo h1 {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 700;
        }

        .global-nav .logo img {
            height: 60px;
            width: auto;
            display: block;
            transition: transform 0.2s ease;
        }

        .global-nav .logo:hover img {
            transform: scale(1.02);
        }

        .nav-menu {
            display: flex;
            list-style: none;
            margin: 0;
            padding: 0;
            gap: 0.5rem;
            align-items: center;
        }

        .nav-menu li {
            position: relative;
        }

        .nav-menu a {
            text-decoration: none;
            color: #333;
            font-weight: 500;
            padding: 0.75rem 1rem;
            border-radius: 6px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .nav-menu a::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1), transparent);
            transition: left 0.5s;
        }

        .nav-menu a:hover {
            background-color: #f8fafc;
            color: #1e3a8a;
            transform: translateY(-1px);
        }

        .nav-menu a:hover::before {
            left: 100%;
        }

        .dropdown {
            position: relative;
        }

        .dropdown-menu {
            position: absolute;
            top: 100%;
            left: 0;
            background-color: white;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            padding: 1rem;
            border-radius: 8px;
            min-width: 220px;
            z-index: 1001;
            opacity: 0;
            visibility: hidden;
            transform: translateY(-10px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid #e5e7eb;
        }

        .dropdown:hover .dropdown-menu,
        .dropdown.active .dropdown-menu {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
        }

        .dropdown-menu a {
            display: block;
            padding: 0.75rem 1rem;
            color: #333;
            border-radius: 6px;
            transition: all 0.3s ease;
            margin-bottom: 0.25rem;
        }

        .dropdown-menu a:hover {
            background-color: #f8fafc;
            color: #1e3a8a;
            padding-left: 1.25rem;
        }

        .dropdown-arrow {
            font-size: 0.8rem;
            margin-left: 0.25rem;
            transition: transform 0.3s ease;
        }

        .dropdown.active .dropdown-arrow {
            transform: rotate(180deg);
        }

        /* Mobile menu toggle */
        .mobile-menu-toggle {
            display: none;
            background: none;
            border: none;
            font-size: 1.5rem;
            color: #333;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 6px;
            transition: all 0.3s ease;
        }

        .mobile-menu-toggle:hover {
            background-color: #f0f0f0;
        }

        .mobile-menu-toggle.active {
            color: #1e3a8a;
            background-color: #e3f2fd;
        }

        /* Mobile responsive styles */
        @media (max-width: 992px) {
            .global-nav {
                padding: 1rem;
            }
            
            .nav-menu {
                position: fixed;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100vh;
                background-color: white;
                flex-direction: column;
                align-items: flex-start;
                padding: 4rem 2rem 2rem;
                gap: 1.5rem;
                box-shadow: 2px 0 20px rgba(0,0,0,0.1);
                transition: left 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                z-index: 1002;
                overflow-y: auto;
                display: none;
            }
            
            .nav-menu.mobile-active {
                left: 0;
                display: flex !important;
            }
            
            .mobile-menu-toggle {
                display: block;
            }
            
            .nav-menu li {
                width: 100%;
            }

            .nav-menu a {
                padding: 1rem;
                border-bottom: 1px solid #eee;
                font-size: 1rem;
                min-height: 48px;
                display: flex;
                align-items: center;
                justify-content: flex-start;
            }
            
            .dropdown-menu a {
                padding: 0.5rem 0;
                margin-bottom: 0.25rem;
                border-radius: 0;
                background: transparent;
            }
            
            .dropdown-menu a:hover {
                padding-left: 0;
                background: transparent;
                color: #1e3a8a;
            }
        }

        /* Sticky CTA Bar for Mobile */
        .sticky-cta-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            padding: 1rem;
            display: none;
            justify-content: space-around;
            align-items: center;
            z-index: 1000;
            box-shadow: 0 -4px 12px rgba(0,0,0,0.15);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .sticky-cta-bar .btn {
            background: white;
            color: #1d4ed8;
            border: 2px solid #1d4ed8;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            font-weight: 700;
            border-radius: 8px;
            text-decoration: none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            min-width: 140px;
            text-align: center;
        }

        .sticky-cta-bar .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(29, 78, 216, 0.3);
        }

        .sticky-cta-bar .btn.secondary {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            border: 2px solid #3b82f6;
        }

        .sticky-cta-bar .btn.secondary:hover {
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }

        @media (max-width: 768px) {
            .sticky-cta-bar {
                display: flex;
            }
        }

        .nav-menu {
            will-change: transform;
        }
    </style>
'''

def add_global_header(filepath):
    """Add global header to a page"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has global-header
        if 'id="header-container"' in content or 'global-header.js' in content:
            print(f"Header already exists in: {filepath}")
            return
        
        # Add styles before </head>
        if '</head>' in content:
            content = content.replace('</head>', HEADER_STYLES + '</head>')
        
        # Add header container and script after <body>
        if '<body>' in content:
            # Find position after <body> tag
            body_match = re.search(r'<body[^>]*>', content)
            if body_match:
                insert_pos = body_match.end()
                header_html = '''\n    <!-- Global Header will be loaded here -->\n    <div id="header-container"></div>\n'''
                content = content[:insert_pos] + header_html + content[insert_pos:]
        
        # Add global-header.js before other scripts or at end of body
        if '<script src="js/global-header.js"></script>' not in content:
            # Add before </body> or after other scripts
            if '</body>' in content:
                content = content.replace('</body>', '    <script src="js/global-header.js"></script>\n</body>')
        
        # Add sticky CTA bar if not present
        if 'sticky-cta-bar' not in content:
            sticky_bar = '''    <!-- Sticky CTA Bar for Mobile -->
    <div class="sticky-cta-bar" id="sticky-cta-bar">
        <a href="explore-chefs.html" class="btn">👨‍🍳 Explore Chefs</a>
        <a href="book-a-chef.html" class="btn secondary">📅 Book Chef</a>
    </div>
'''
            # Insert after header-container
            if 'id="header-container"' in content:
                content = content.replace(
                    '<div id="header-container"></div>',
                    '<div id="header-container"></div>\n\n' + sticky_bar
                )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Added global header to: {filepath}")
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def main():
    for page in PAGES:
        if os.path.exists(page):
            add_global_header(page)
        else:
            print(f"File not found: {page}")

if __name__ == "__main__":
    main()
