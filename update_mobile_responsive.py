#!/usr/bin/env python3
"""
Script to add mobile responsive CSS to all HTML files
"""

import os
import re

# List of HTML files to update
html_files = [
    'index.html',
    'about-us.html',
    'services.html',
    'chef-services.html',
    'special-events.html',
    'weekly-meals.html',
    'catering-services.html',
    'become-a-chef.html',
    'chef-guidelines.html',
    'chef-faq.html',
    'explore-chefs.html',
    'book-a-chef.html',
    'book-weekly-service.html',
    'catering-enquiry.html',
    'catering-form.html',
    'enquiry-form.html',
    'gallery.html',
    'blogs.html',
    'blog-chef-tips.html',
    'blog-healthy-eating.html',
    'blog-meal-prep.html',
    'blog-event-menu.html',
    'blog-food-trends.html',
    'submit-blog.html',
    'faq.html',
    'contact-us.html',
    'success-stories.html',
    'owner.html',
    'login.html',
    'signup.html',
    'user-login.html',
    'user-signup.html',
    'user-profile.html',
    'chef-application.html',
    'chef-profile-template.html',
    'chef-profile-anna.html',
    'chef-profile-carlos.html',
    'chef-profile-david.html',
    'chef-profile-maria.html',
    'chef-profile-michael.html',
    'chef-profile-rajesh.html',
    'chef-profile-james.html',
    'chef-profiles/michael-brown.html',
    'chef-profiles/anna-smith.html',
    'chef-profiles/david-kim.html',
    'chef-profiles/sarah-johnson.html',
    'chef-profiles/carlos-mendez.html',
    'chef-profiles/emily-chen.html',
    'menu-services.html',
    'balanced-diet.html',
    'create-balanced-diet.html',
    'diet-plan.html',
    'diet-plan-view.html',
    'payment.html',
    'privacy-policy.html',
    'refund-policy.html',
    'terms-conditions.html',
    'admin/chef.html',
    'admin/meet.html',
    'test-hamburger.html',
    'test-mobile-menu.html',
    'test-chatbot.html',
    'test-dropdown.html',
    'test-user-profile-api.html',
    'test-diet-plan-form.html',
    'test-async-diet-plan.html',
    'test-beautify-functionality.html',
    'test-chef-integration.html',
    'test_diet_plan_button.html'
]

def update_html_file(filepath):
    """Update a single HTML file to include mobile responsive CSS"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if mobile-responsive.css is already included
        if 'mobile-responsive.css' in content:
            print(f"✓ {filepath} already has mobile-responsive.css")
            return True
        
        # Find the line with the main CSS link
        css_pattern = r'(<link rel="stylesheet" href="[^"]*css/style\.css"[^>]*>)'
        match = re.search(css_pattern, content)
        
        if match:
            # Insert mobile responsive CSS after the main CSS
            new_link = '<link rel="stylesheet" href="mobile-responsive.css">'
            updated_content = content.replace(match.group(1), match.group(1) + '\n    ' + new_link)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✓ Updated {filepath}")
            return True
        else:
            print(f"✗ Could not find CSS link in {filepath}")
            return False
            
    except Exception as e:
        print(f"✗ Error updating {filepath}: {e}")
        return False

def main():
    """Main function to update all HTML files"""
    print("Updating HTML files with mobile responsive CSS...")
    
    updated_count = 0
    total_count = len(html_files)
    
    for filename in html_files:
        filepath = f'website/{filename}'
        if os.path.exists(filepath):
            if update_html_file(filepath):
                updated_count += 1
        else:
            print(f"✗ File not found: {filepath}")
    
    print(f"\nSummary: {updated_count}/{total_count} files updated successfully")

if __name__ == '__main__':
    main()