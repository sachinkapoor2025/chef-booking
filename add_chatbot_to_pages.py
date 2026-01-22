#!/usr/bin/env python3
"""
Script to add chatbot to all website HTML pages
"""

import os
import re
from bs4 import BeautifulSoup

def add_chatbot_to_page(file_path):
    """Add chatbot include to an HTML file"""
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Check if chatbot is already added
        if soup.find('div', {'class': 'chatbot-container'}):
            print(f"✅ Chatbot already exists in {file_path}")
            return False

        # Add chatbot include before closing body tag
        body_tag = soup.find('body')
        if body_tag:
            # Create chatbot include
            chatbot_include = soup.new_tag('div')
            chatbot_include['class'] = 'chatbot-container'
            chatbot_include.string = '<!-- Chatbot will be loaded here -->'

            # Add script to load chatbot
            script_tag = soup.new_tag('script')
            script_tag.string = '''
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
            '''

            # Insert before closing body tag
            if body_tag.find('script'):
                # Insert before last script
                last_script = body_tag.find_all('script')[-1]
                last_script.insert_after(chatbot_include)
                last_script.insert_after(script_tag)
            else:
                body_tag.append(chatbot_include)
                body_tag.append(script_tag)

            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))

            print(f"✅ Added chatbot to {file_path}")
            return True

        return False

    except Exception as e:
        print(f"❌ Error processing {file_path}: {str(e)}")
        return False

def main():
    """Main function to add chatbot to all HTML files"""
    print("🚀 Starting chatbot integration...")

    # Get all HTML files in website directory
    website_dir = 'website'
    html_files = []

    for root, dirs, files in os.walk(website_dir):
        # Skip admin directory
        if 'admin' in root:
            continue

        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))

    print(f"📁 Found {len(html_files)} HTML files")

    # Add chatbot to each file
    modified_count = 0
    for file_path in html_files:
        if add_chatbot_to_page(file_path):
            modified_count += 1

    print(f"🎉 Completed! Modified {modified_count} files")
    print("💡 Chatbot has been added to all website pages")

if __name__ == "__main__":
    main()
