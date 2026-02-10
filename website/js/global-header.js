// Optimized Global Header Loading Script
(function () {
    'use strict';

    // Fast header loading with caching
    function loadHeader() {
        // Check if header already exists (for pages that include it directly)
        const existingHeader = document.querySelector('.global-header');
        if (existingHeader) {
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

            // Also insert sticky CTA bar if present
            const stickyBar = doc.querySelector('#sticky-cta-bar');
            if (stickyBar) {
                document.body.appendChild(stickyBar);
            }

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
                        <h1>
                            <a href="index.html" style="text-decoration: none; color: inherit;">
                                <img src="images/logo.jpg" alt="Maharaja Chef Services Logo" style="height: 90px; width: auto;">
                            </a>
                        </h1>
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

        // Hamburger Menu Functionality
        function initHamburgerMenu() {
            const hamburger = document.querySelector('.mobile-menu-toggle');
            const navMenu = document.querySelector('.nav-menu');   // ← MOVE HERE
            const mobileOverlay = document.querySelector('.mobile-menu-overlay');
            const mobileContent = document.querySelector('.mobile-menu-content');
            const closeBtn = document.querySelector('.mobile-menu-close');
            const body = document.body;

            if (!hamburger || !navMenu) {
                console.warn('Hamburger or navMenu not found');
                return;
            }


            hamburger.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();

                navMenu.classList.add('mobile-active');   // THIS shows the menu
                body.style.overflow = 'hidden';
                hamburger.classList.add('active');
            });


            // Close menu - overlay click
// Close menu - overlay click
            if (mobileOverlay) {
                mobileOverlay.addEventListener('click', function (e) {
                    if (e.target === mobileOverlay) {
                        closeMenu();
                    }
                });
            }

            // Close menu - close button
            if (closeBtn) {
                closeBtn.addEventListener('click', closeMenu);
            }


            // Close menu - escape key
            document.addEventListener('keydown', function (e) {
                if (e.key === 'Escape' && navMenu.classList.contains('mobile-active')) {
                    closeMenu();
                }

            });

            // Close menu function
            function closeMenu() {
                navMenu.classList.remove('mobile-active');
                body.style.overflow = ''; // Restore scrolling
                hamburger.classList.remove('active');
                
                // Close any open dropdowns
                const dropdowns = document.querySelectorAll('.mobile-dropdown.active');
                dropdowns.forEach(dropdown => dropdown.classList.remove('active'));
            }

            // Mobile dropdown functionality
            const mobileDropdowns = document.querySelectorAll('.mobile-dropdown');
            mobileDropdowns.forEach(dropdown => {
                const toggle = dropdown.querySelector('.mobile-dropdown-toggle');
                const menu = dropdown.querySelector('.mobile-dropdown-menu');

                if (toggle && menu) {
                    toggle.addEventListener('click', function (e) {
                        e.preventDefault();
                        e.stopPropagation();

                        // Toggle dropdown
                        dropdown.classList.toggle('active');
                        
                        // Update aria-expanded
                        const isExpanded = dropdown.classList.contains('active');
                        toggle.setAttribute('aria-expanded', isExpanded);
                        
                        // Rotate arrow
                        const arrow = toggle.querySelector('.mobile-dropdown-arrow');
                        if (arrow) {
                            arrow.style.transform = isExpanded ? 'rotate(180deg)' : 'rotate(0deg)';
                        }
                    });
                }
            });
        }

        // Desktop dropdown functionality
        function initDropdowns() {
            const dropdowns = document.querySelectorAll('.dropdown');

            if (dropdowns.length === 0) return; // No dropdowns found

            dropdowns.forEach(dropdown => {
                const trigger = dropdown.querySelector('.dropdown-toggle');
                const menu = dropdown.querySelector('.dropdown-menu');

                if (trigger && menu) {
                    trigger.addEventListener('click', function (e) {
                        e.preventDefault();
                        e.stopPropagation();

                        // Toggle dropdown on click (both mobile and desktop)
                        dropdown.classList.toggle('active');

                        // Close other dropdowns
                        dropdowns.forEach(otherDropdown => {
                            if (otherDropdown !== dropdown) {
                                otherDropdown.classList.remove('active');
                            }
                        });
                    });

                    // Close dropdown when clicking outside
                    document.addEventListener('click', function (e) {
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
                if (window.innerWidth <= 768) {
                    stickyBar.style.display = 'flex';
                } else {
                    stickyBar.style.display = 'none';
                }

                window.addEventListener('resize', function () {
                    if (window.innerWidth <= 768) {
                        stickyBar.style.display = 'flex';
                    } else {
                        stickyBar.style.display = 'none';
                    }
                });
            }
        }

        // Initialize all functionality
        initHamburgerMenu();
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
                .then(() => { })
                .catch(() => { });
        });
    }

})();
