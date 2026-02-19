import os

website_dir = 'website'
old_facebook = 'https://facebook.com'
new_facebook = 'https://www.facebook.com/profile.php?id=61587294953271'

# List of files to update based on search results
files_to_update = [
    'privacy-policy.html', 'sev-puri.html', 'success-stories.html', 'user-login.html',
    'user-profile.html', 'weekly-meals.html', 'user-signup.html', 'terms-conditions.html',
    'submit-blog.html', 'special-events.html', 'signup.html', 'refund-policy.html',
    'pani-puri.html', 'payment.html', 'owner.html', 'menu-services.html', 'login.html',
    'gallery.html', 'diet-plan.html', 'enquiry-form.html', 'diet-plan-view.html',
    'create-balanced-diet.html', 'chef-services.html', 'chef-profile-template.html',
    'chef-profile-rajesh.html', 'chef-profile-michael.html', 'chef-profile-maria.html',
    'chef-profiles/anna-smith.html', 'chef-profile-james.html', 'chef-profiles/carlos-mendez.html',
    'chef-profiles/david-kim.html', 'chef-profile-david.html', 'chef-profiles/emily-chen.html',
    'chef-profiles/michael-brown.html', 'chef-profile-carlos.html', 'chef-profiles/sarah-johnson.html',
    'chef-profile-anna.html', 'chef-guidelines.html', 'chef-faq.html', 'chef-application.html',
    'catering-services.html', 'catering-form.html', 'catering-enquiry.html', 'book-weekly-service.html',
    'blogs.html', 'blog-meal-prep.html', 'blog-healthy-eating.html', 'blog-food-trends.html',
    'blog-chef-tips.html', 'blog-event-menu.html', 'become-a-chef.html'
]

count = 0
for file_path in files_to_update:
    full_path = os.path.join(website_dir, file_path)
    if os.path.exists(full_path):
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if old_facebook in content:
                new_content = content.replace(old_facebook, new_facebook)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                count += 1
                print(f'Updated: {file_path}')
        except Exception as e:
            print(f'Error updating {file_path}: {e}')

print(f'\nTotal files updated: {count}')
