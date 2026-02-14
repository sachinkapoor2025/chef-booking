import re
import os

os.chdir('c:/Users/dell/OneDrive/Desktop/maharajachef-git/chef-booking/website')

files_to_update = [
    'become-a-chef.html',
    'balanced-diet.html', 
    'explore-chefs.html',
    'login.html',
    'owner.html',
    'book-a-chef.html',
    'about-us.html'
]

for filename in files_to_update:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove header-right div with mobile-menu-toggle
        content = re.sub(r'<div class="header-right">\s*<button class="mobile-menu-toggle"[^>]*>.*?</button>\s*</div>', '', content, flags=re.DOTALL)
        
        # Remove mobile-menu-toggle button that might be elsewhere
        content = re.sub(r'<button class="mobile-menu-toggle"[^>]*>.*?</button>', '', content, flags=re.DOTALL)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated: {filename}')
    except Exception as e:
        print(f'Error with {filename}: {e}')

print("Done!")
