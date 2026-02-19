# Speed Optimization Script

## Prerequisites

This script requires **Python** to be installed on your computer.

### Install Python (If Not Available)
1. Download Python from: https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Run the script below after installation

## How to Run

### Option 1: Using Python
Open Command Prompt (cmd) and run:
```bash
python batch_optimize_speed.py
```

### Option 2: Using Node.js
If Node.js is installed:
```bash
node batch_optimize_speed.js
```

## What the Script Does

1. **Lazy Loading for Images**: Adds `loading="lazy"` attribute to all images
2. **Deferred Scripts**: Adds `defer` attribute to all JavaScript files

## Already Optimized Files

The homepage (`website/index.html`) has been manually optimized with:
- Hero image: `fetchpriority="high"` and `decoding="async"`
- Gallery images: `loading="lazy"`
- All scripts: `defer` attribute

## Manual Optimization (If Script Fails)

To manually optimize any HTML file, add these attributes:

### For Images:
```html
<!-- Above the fold (hero, featured) -->
<img src="image.jpg" fetchpriority="high" decoding="async">

<!-- Below the fold -->
<img src="image.jpg" loading="lazy">
```

### For Scripts:
```html
<script src="script.js" defer></script>
```

## Additional Recommendations

1. **Compress Images**: Use TinyPNG, ImageOptim, or Squoosh to compress images
2. **Use WebP**: Convert images to WebP format for smaller file sizes
3. **Server Compression**: Enable Gzip or Brotli on your web server
4. **CDN**: Use a CDN like CloudFlare for faster content delivery

## Manual Optimization Steps

Since Python/Node.js may not be available, manually optimize key pages:

### Key Pages to Optimize:
- index.html ✅ Already optimized
- about-us.html
- services.html
- explore-chefs.html
- gallery.html
- chef-profiles/*.html
- blog-*.html

### Quick Fix: Add to All Images
Add `loading="lazy"` to images (except hero image):
```html
<img src="image.jpg" loading="lazy" alt="...">
```

### Quick Fix: Add to All Scripts
Add `defer` to script tags:
```html
<script src="script.js" defer></script>
```

### Quick Fix: Add to Hero/Featured Images
Add `fetchpriority="high" decoding="async"`:
```html
<img src="hero.jpg" fetchpriority="high" decoding="async" alt="...">
```
