#!/usr/bin/env python3

import os
import re

def add_chatbot_to_page(file_path):
    """Add chatbot script to an HTML file if not already present"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Check if chatbot script is already present
        if 'chatbot.html' in content:
            print(f"Chatbot already present in {file_path}")
            return False

        # Create chatbot script
        chatbot_script = '''    <!-- Chatbot Integration -->
    <script>
        // Load chatbot
        fetch('chatbot.html')
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const chatbotContainer = doc.querySelector('.chatbot-container');
                const styleTags = doc.querySelectorAll('style');

                // Add styles
                styleTags.forEach(style => {
                    document.head.appendChild(style.cloneNode(true));
                });

                // Add chatbot container
                document.body.appendChild(chatbotContainer.cloneNode(true));

                // Initialize chatbot script
                const scriptTags = doc.querySelectorAll('script');
                scriptTags.forEach(script => {
                    const newScript = document.createElement('script');
                    newScript.textContent = script.textContent;
                    document.body.appendChild(newScript);
                });
            })
            .catch(error => {
                console.error('Error loading chatbot:', error);
            });
    </script>
</body>'''

        # Find the closing body tag and insert before it
        if '</body>' in content:
            # Replace </body> with our script + </body>
            new_content = content.replace('</body>', chatbot_script)

            # Write the modified content back to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)

            print(f"Added chatbot to {file_path}")
            return True
        else:
            print(f"No closing body tag found in {file_path}")
            return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    # Get all HTML files in the website directory
    website_dir = 'website'
    html_files = []

    for root, dirs, files in os.walk(website_dir):
        # Skip admin directory
        if 'admin' in root:
            continue

        for file in files:
            if file.endswith('.html') and file != 'chatbot.html':
                html_files.append(os.path.join(root, file))

    print(f"Found {len(html_files)} HTML files to process")

    # Process each HTML file
    modified_count = 0
    for html_file in html_files:
        if add_chatbot_to_page(html_file):
            modified_count += 1

    print(f"\nProcessed {len(html_files)} files, modified {modified_count} files")

if __name__ == "__main__":
    main()
