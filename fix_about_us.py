#!/usr/bin/env python3
import re

with open('website/about-us.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the inline header loading script
pattern = r"<script>\s*// Load header component[\s\S]*?console\.error\([\"']Error loading header[\"'], error\);\s*}\);\s*</script>"
content = re.sub(pattern, "", content)

# Clean up extra whitespace
content = re.sub(r"\n{3,}", "\n\n", content)

with open('website/about-us.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed about-us.html - removed duplicate header script')
