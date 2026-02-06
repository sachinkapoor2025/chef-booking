// Optimized Global Header Loading Script
(function() {
    'use strict';

    // Fast header loading with caching
    function loadHeader() {
        // Check if header already exists (for pages that include it directly)
        const existingHeader = document.querySelector('.global-header');
        if (existingHeader) {
            // Initialize functionality for existing header
            initHeaderFunctionality();
            return;
        }

        // Try to load header from cache first
        const cachedHeader = sessionStorage.getItem('global-header');
        if (cachedHeader) {
            insertHeader(cachedHeader);
            return;
        }

        // Load header via fetch with caching
        fetch('components/header.html', {
            cache: 'force-cache',
            headers: {
                'Cache-Control': 'max-age=3600' // Cache for 1 hour
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load header');
            }
            return response.text();
        })
        .then(html => {
            // Cache the header for faster subsequent loads
            try {
                sessionStorage.setItem('global-header', html);
            } catch (e) {
                // Ignore cache errors
            }
            
            insertHeader(html);
        })
        .catch(error => {
            console.warn('Header loading failed, using fallback:', error);
            createMinimalHeader();
        });
    }

    function insertHeader(html) {
        // Parse the HTML to extract just the header content
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const headerElement = doc.querySelector('.global-header');
        
        if (headerElement) {
            // Insert the header at the beginning of the body
            document.body.insertBefore(headerElement, document.body.firstChild);
            
            // Initialize functionality
            initHeaderFunctionality();
        }
    }

    function createMinimalHeader() {
        // Create a minimal header as fallback
        const header = document.createElement('header');
        header.className = 'global-header';
        header.innerHTML = `
            <nav class="global-nav">
                <div class="header-left">
                    <div class="logo">
                        <h1><a href="index.html" style="text-decoration: none; color: inherit;"><img src="images/logo.jpg" alt="Maharaja Chef Services Logo" style="height: 90px; width: auto;"></a></h1>
                    </div>
                </div>
                <div class="header-center">
                    <ul class="nav-menu">
                        <li><a href="index.html">Home</a></li>
                        <li><a href="catering-services.html">Catering Services</a></li>
                        <li><a href="balanced-diet.html">Balanced Diet</a></li>
                        <li><a href="book-a-chef.html">Book a Chef</a></li>
                        <li><a href="become-a-chef.html">Become a Chef</a></li>
                        <li><a href="explore-chefs.html">Explore Chefs</a></li>
                        <li><a href="contact-us.html">Contact Us</a></li>
                    </ul>
                </div>
            </nav>
        `;
        
        document.body.insertBefore(header, document.body.firstChild);
        initHeaderFunctionality();
    }

    function initHeaderFunctionality() {
        // Mobile menu toggle
        function initMobileMenu() {
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navMenu = document.querySelector('.nav-menu');

    if (mobileMenuToggle && navMenu) {
        mobileMenuToggle.addEventListener('click', function(e) {
            e.preventDefault();

            if (window.innerWidth <= 768) {
                navMenu.classList.toggle('active');
                mobileMenuToggle.classList.toggle('active');
            }
        });
    }
}

        // Dropdown functionality
        function initDropdowns() {
            const dropdowns = document.querySelectorAll('.dropdown');
            
            dropdowns.forEach(dropdown => {
                const trigger = dropdown.querySelector('a');
                const menu = dropdown.querySelector('.dropdown-menu');
                
                if (trigger && menu) {
                    trigger.addEventListener('click', function(e) {
                        e.preventDefault();
                        
                        // Toggle dropdown visibility
                        dropdown.classList.toggle('active');
                        
                        // Close other dropdowns
                        dropdowns.forEach(otherDropdown => {
                            if (otherDropdown !== dropdown) {
                                otherDropdown.classList.remove('active');
                            }
                        });
                    });
                    
                    // Close dropdown when clicking outside
                    document.addEventListener('click', function(e) {
                        if (!dropdown.contains(e.target)) {
                            dropdown.classList.remove('active');
                        }
                    });
                }
            });
        }

        // Mobile detection and CTA bar
        function initMobileCTA() {
            const stickyBar = document.getElementById('sticky-cta-bar');
            if (stickyBar) {
                // Show CTA bar on mobile devices
                if (window.innerWidth <= 768) {
                    stickyBar.style.display = 'flex';
                }
                
                // Handle resize events
                window.addEventListener('resize', function() {
                    if (window.innerWidth <= 768) {
                        stickyBar.style.display = 'flex';
                    } else {
                        stickyBar.style.display = 'none';
                    }
                });
            }
        }

        // Initialize all functionality
        initMobileMenu();
        initDropdowns();
        initMobileCTA();
    }

    // Load header immediately if DOM is already loaded, otherwise wait for DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadHeader);
    } else {
        loadHeader();
    }

    // Preload header for faster navigation (optional performance enhancement)
    if ('requestIdleCallback' in window) {
        requestIdleCallback(() => {
            fetch('components/header.html', { cache: 'force-cache' })
                .then(() => {})
                .catch(() => {});
        });
    }
})();
        function initMobileMenu() {
            const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
              const navMenu = document.querySelector('.nav-menu');

    if (mobileMenuToggle && navMenu) {
        mobileMenuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            navMenu.classList.toggle('active');
            mobileMenuToggle.classList.toggle('active');
        });
    }
}
