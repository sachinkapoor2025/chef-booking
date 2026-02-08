# Header Component Update Instructions

## Overview

The hamburger menu for mobile view has been successfully implemented and is working on the home page. To make it available on all pages, you need to update the remaining HTML files to use the new header component.

## What Has Been Completed

✅ **Header Component Created**: `website/components/header.html`  
✅ **CSS Styles Added**: Mobile menu styles in `website/css/style.css`  
✅ **JavaScript Functionality**: Toggle functionality in `website/js/global-header.js`  
✅ **Home Page Updated**: `website/index.html` already uses the component  
✅ **About Us Page Updated**: `website/about-us.html` updated  
✅ **Become a Chef Page Updated**: `website/become-a-chef.html` updated  
✅ **Test Page Created**: `website/test-hamburger.html` for testing  

## Pages That Need Updates

The following pages still use the old header structure and need to be updated:

### Key Pages (High Priority)
- `website/book-a-chef.html`
- `website/catering-services.html`
- `website/balanced-diet.html`
- `website/weekly-meals.html`
- `website/faq.html`
- `website/gallery.html`
- `website/blogs.html`

### Chef Profile Pages
- `website/chef-profile-anna.html`
- `website/chef-profile-carlos.html`
- `website/chef-profile-david.html`
- `website/chef-profile-james.html`
- `website/chef-profile-maria.html`
- `website/chef-profile-michael.html`
- `website/chef-profile-rajesh.html`

### Other Pages
- `website/chef-services.html`
- `website/services.html`
- `website/special-events.html`
- `website/user-profile.html`
- `website/login.html`
- `website/payment.html`
- `website/contact-us.html`
- And more...

## How to Update Each Page

### Method 1: Manual Update (Recommended for a few pages)

For each page that needs updating:

1. **Replace the old header** (look for this pattern):
   ```html
   <!-- Mobile Menu Header -->
   <header class="global-header" id="global-header">
       <!-- header content -->
   </header>
   ```

2. **Replace with the component include**:
   ```html
   <!-- Include the header component -->
   <div id="header-container"></div>
   ```

3. **Add the header loading script** before the closing `</body>` tag:
   ```html
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
   </script>
   ```

### Method 2: Using the Python Script

I've created a Python script that can automate this process:

1. **Install Python** if not already installed
2. **Run the script**:
   ```bash
   python update_headers.py
   ```

**Note**: The script requires Python to be available in your system PATH.

### Method 3: Using Command Line Tools

If you have command-line tools like `sed` or `awk` available:

```bash
# Replace old header pattern with component include
sed -i 's|<!-- Mobile Menu Header -->.*</header>|<!-- Include the header component -->\n    <div id="header-container"></div>|' filename.html

# Add the script before </body>
sed -i '/<\/body>/i\
    <script>\
        // Load header component\
        fetch('\''components/header.html'\'')\
            .then(response => response.text())\
            .then(html => {\
                document.getElementById('\''header-container'\'').innerHTML = html;\
            })\
            .catch(error => {\
                console.error('\''Error loading header:'\'', error);\
            });\
    </script>' filename.html
```

## Testing the Updates

After updating any page:

1. **Open the page in a browser**
2. **Resize to mobile width** (≤768px)
3. **Look for the hamburger button** in the top-right corner
4. **Click the hamburger** to open the mobile menu
5. **Test all dropdowns** work within the mobile menu
6. **Test closing** the menu (click outside or close button)

## Troubleshooting

### Hamburger Button Not Visible
- Check that the page width is ≤768px
- Verify the CSS styles are loaded
- Check browser console for JavaScript errors

### Mobile Menu Not Opening
- Ensure the JavaScript file `js/global-header.js` is loaded
- Check that the hamburger button has the correct class `hamburger-menu`
- Verify the mobile menu has the correct ID `mobile-menu`

### Dropdowns Not Working in Mobile Menu
- Check that the dropdown JavaScript is working
- Verify the dropdown toggle buttons have the correct classes
- Ensure the CSS transitions are applied

### Header Not Loading
- Check that `components/header.html` exists and is accessible
- Verify the fetch request is working (check browser console)
- Ensure the page has internet access if loading from external sources

## Files Created/Modified

### New Files
- `website/components/header.html` - Header component
- `website/test-hamburger.html` - Test page
- `update_headers.py` - Update script
- `HEADER_UPDATE_INSTRUCTIONS.md` - This file

### Modified Files
- `website/css/style.css` - Added mobile menu styles
- `website/js/global-header.js` - Added hamburger functionality
- `website/index.html` - Already had component
- `website/about-us.html` - Updated to use component
- `website/become-a-chef.html` - Updated to use component

## Next Steps

1. **Choose your update method** (manual, script, or command line)
2. **Update the remaining pages** using the chosen method
3. **Test each updated page** on mobile devices
4. **Verify all functionality** works as expected
5. **Deploy the changes** to your live site

## Support

If you encounter issues:

1. **Check the browser console** for JavaScript errors
2. **Verify file paths** are correct
3. **Test the header component** by opening `website/components/header.html` directly
4. **Use the test page** at `website/test-hamburger.html` to verify functionality

The hamburger menu implementation is complete and ready for use across all pages once the header updates are applied.