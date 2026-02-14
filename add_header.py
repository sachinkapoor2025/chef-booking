import re

# Read the index.html file
with open('website/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Header HTML with hamburger
header_html = '''<header class="global-header" id="global-header"> 
    <nav class="global-nav">
        <div class="header-left">
            <div class="logo">
                <h1>
                    <a href="index.html">
                        <img src="images/logo.jpg" alt="Maharaja Chef Services Logo" style="height:60px;">
                    </a>
                </h1>
            </div>
        </div>

        <div class="header-center">
            <ul class="nav-menu">
                <li><a href="index.html">Home</a></li>
                <li><a href="catering-services.html">Catering Services</a></li>
                <li><a href="balanced-diet.html">Balanced Diet</a></li>
                <li class="dropdown">
                    <a href="#" class="dropdown-toggle">Services <span class="dropdown-arrow">▼</span></a>
                    <ul class="dropdown-menu">
                        <li><a href="book-a-chef.html">Book a Chef</a></li>
                        <li><a href="weekly-meals.html">Weekly Meal Service</a></li>
                    </ul>
                </li>
                <li class="dropdown">
                    <a href="#" class="dropdown-toggle">For Chefs <span class="dropdown-arrow">▼</span></a>
                    <ul class="dropdown-menu">
                        <li><a href="become-a-chef.html">Become a Chef</a></li>
                        <li><a href="chef-guidelines.html">Chef Guidelines</a></li>
                        <li><a href="chef-faq.html">Chef FAQ</a></li>
                        <li><a href="success-stories.html">Success Stories</a></li>
                    </ul>
                </li>
                <li class="dropdown">
                    <a href="#" class="dropdown-toggle">Explore More <span class="dropdown-arrow">▼</span></a>
                    <ul class="dropdown-menu">
                        <li><a href="explore-chefs.html">Explore Chefs</a></li>
                        <li><a href="menu-services.html">Menu Services</a></li>
                        <li><a href="about-us.html">About Us</a></li>
                        <li><a href="blogs.html">Blogs</a></li>
                        <li><a href="gallery.html">Gallery</a></li>
                        <li><a href="faq.html">FAQ</a></li>
                        <li><a href="contact-us.html">Contact Us</a></li>
                    </ul>
                </li>
                <li><a href="owner.html">Business Owner</a></li>
                <li><a href="login.html">Log In</a></li>
            </ul>
        </div>

        <!-- Mobile Menu Toggle Button -->
        <button class="mobile-menu-toggle" id="mobileMenuToggle" aria-label="Toggle mobile menu">
            <span></span>
            <span></span>
            <span></span>
        </button>
    </nav>
</header>'''

# Replace the header-container div with the actual header
old_pattern = r'<div id="header-container"></div>'
new_content = re.sub(old_pattern, header_html, content)

# Write back
with open('website/index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Header with hamburger added to index.html')