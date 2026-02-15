#!/usr/bin/env python3
"""
Script to update all HTML files to use the new header component
"""

import os
import re

# List of files to update (excluding index.html which already has the component)
files_to_update = [
    'website/about-us.html',
    'website/become-a-chef.html',
    'website/blog-chef-tips.html',
    'website/blog-event-menu.html',
    'website/blog-food-trends.html',
    'website/blog-healthy-eating.html',
    'website/blog-meal-prep.html',
    'website/blogs.html',
    'website/book-a-chef.html',
    'website/book-weekly-service.html',
    'website/booking-widget.html',
    'website/balanced-diet.html',
    'website/catering-enquiry.html',
    'website/catering-form.html',
    'website/catering-services.html',
    'website/chef-application.html',
    'website/chef-faq.html',
    'website/chef-guidelines.html',
    'website/chef-profile-anna.html',
    'website/chef-profile-carlos.html',
    'website/chef-profile-david.html',
    'website/chef-profile-james.html',
    'website/chef-profile-maria.html',
    'website/chef-profile-michael.html',
    'website/chef-profile-rajesh.html',
    'website/chef-profile-template.html',
    'website/chef-services.html',
    'website/contact-us.html',
    'website/create-balanced-diet.html',
    'website/diet-plan.html',
    'website/diet-plan-view.html',
    'website/explore-chefs.html',
    'website/faq.html',
    'website/gallery.html',
    'website/login.html',
    'website/menu-services.html',
    'website/owner.html',
    'website/payment.html',
    'website/refund-policy.html',
    'website/services.html',
    'website/signup.html',
    'website/special-events.html',
    'website/success-stories.html',
    'website/terms-conditions.html',
    'website/user-login.html',
    'website/user-profile.html',
    'website/user-signup.html',
    'website/weekly-meals.html',
    'website/submit-blog.html'
]

def update_file(file_path):
    """Update a single HTML file to use the header component"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match the old header structure
        old_header_pattern = r'<!-- Mobile Menu Header -->\s*<header class="global-header" id="global-header">.*?</header>'
        
        # Check if the file already uses the header component
        if 'id="header-container"' in content:
            print(f"✓ {file_path} already uses header component")
            return True
        
        # Check if the file has the old header structure
        if re.search(old_header_pattern, content, re.DOTALL):
            # Replace old header with component include
            new_content = re.sub(
                old_header_pattern,
                '<!-- Include the header component -->\n    <div id="header-container"></div>',
                content,
                flags=re.DOTALL
            )
            
            # Add the header loading script before the closing body tag
            script_to_add = '''
    <script>
        // Load header component
        fetch('components/header.html')
            .then(response => response.text())
            .then(html => {
                document.getElementById('header-container').innerHTML = html;
            })
            .catch(error => {
                console.error('Error loading header:', error);
            });
    </script>'''
            
            # Insert script before closing body tag
            new_content = new_content.replace('</body>', script_to_add + '\n</body>')
            
            # Write the updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✓ Updated {file_path}")
            return True
        else:
            print(f"⚠ {file_path} doesn't have recognizable header structure")
            return False
            
    except Exception as e:
        print(f"✗ Error updating {file_path}: {e}")
        return False

def main():
    """Main function to update all files"""
    print("Updating HTML files to use header component...")
    print("=" * 50)
    
    success_count = 0
    total_count = len(files_to_update)
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            if update_file(file_path):
                success_count += 1
        else:
            print(f"✗ File not found: {file_path}")
    
    print("=" * 50)
    print(f"Updated {success_count}/{total_count} files successfully")
    
    if success_count == total_count:
        print("🎉 All files updated successfully!")
    else:
        print("⚠ Some files may need manual attention")

if __name__ == "__main__":
    main()