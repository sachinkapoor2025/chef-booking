#!/usr/bin/env python3
"""Add chatbot to remaining pages that don't have it"""

import os

CHATBOT_SCRIPT = '''
    <!-- Chatbot Integration -->
    <script>
        fetch('chatbot.html')
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const styleTags = doc.querySelectorAll('style');
                styleTags.forEach(style => {
                    document.head.appendChild(style.cloneNode(true));
                });
                const chatbotContainer = doc.querySelector('.chatbot-container');
                document.body.appendChild(chatbotContainer.cloneNode(true));
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
</body>
</html>'''

def add_chatbot_to_file(filepath):
    """Add chatbot script to an HTML file if not already present"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if chatbot already exists
        if 'chatbot.html' in content:
            print(f"Chatbot already exists in: {filepath}")
            return
        
        # Replace closing body tag with chatbot script
        if '</body>' in content:
            new_content = content.replace('</body>\n</html>', CHATBOT_SCRIPT)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Added chatbot to: {filepath}")
        else:
            print(f"No closing body tag found in: {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def main():
    pages = [
        'website/about-us.html',
        'website/blogs.html',
        'website/gallery.html',
        'website/faq.html',
        'website/contact-us.html'
    ]
    
    for page in pages:
        if os.path.exists(page):
            add_chatbot_to_file(page)
        else:
            print(f"File not found: {page}")

if __name__ == "__main__":
    main()
