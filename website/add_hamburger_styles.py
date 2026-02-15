#!/usr/bin/env python3
"""Add hamburger menu CSS styles to all pages"""

import os

# CSS styles needed for the global header and hamburger menu
HAMBURGER_STYLES = '''
    <!-- Global Header Styles -->
    <style>
        /* Global Header Styles */
        .global-header {
            background-color: #ffffff;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
        }

        .global-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }

        .global-nav .logo img {
            height: 60px;
            width: auto;
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
            transition: all 0.3s ease;
        }

        .nav-menu a:hover {
            background-color: #f8fafc;
            color: #1e3a8a;
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
            transition: all 0.3s ease;
            border: 1px solid #e5e7eb;
        }

        .dropdown:hover .dropdown-menu {
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
                transition: left 0.4s ease;
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
            text-align: center;
        }

        @media (max-width: 768px) {
            .sticky-cta-bar {
                display: flex;
            }
        }
    </style>
'''

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

def add_styles(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has styles
        if 'mobile-menu-toggle' in content:
            print(f"Styles already exist in: {filepath}")
            return
        
        # Add styles before </head>
        if '</head>' in content:
            content = content.replace('</head>', HAMBURGER_STYLES + '</head>')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Added styles to: {filepath}")
        else:
            print(f"No </head> tag found in: {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def main():
    for page in PAGES:
        if os.path.exists(page):
            add_styles(page)
        else:
            print(f"File not found: {page}")

if __name__ == "__main__":
    main()
