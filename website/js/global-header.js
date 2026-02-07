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
        // Add CSS styles for mobile menu and dropdowns
        const style = document.createElement('style');
        style.textContent = `
            /* Mobile Menu Styles */
            .mobile-menu-toggle {
                display: none;
                background: none;
                border: none;
                color: #1e3a8a;
                font-size: 1.5rem;
                cursor: pointer;
                padding: 0.5rem;
                border-radius: 4px;
                transition: all 0.3s ease;
            }

            .mobile-menu-toggle:hover {
                background: rgba(30, 58, 138, 0.1);
            }

            .mobile-menu-toggle.active {
                background: #3b82f6;
                color: white;
            }

            .nav-menu {
                display: flex;
                gap: 1rem;
                align-items: center;
                transition: all 0.3s ease;
            }

            .nav-menu.active {
                display: flex;
                flex-direction: column;
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                padding: 1rem;
                z-index: 1000;
            }

            .nav-menu.active li {
                margin-bottom: 0.5rem;
            }

            .nav-menu.active li a {
                display: block;
                padding: 0.75rem;
                border-radius: 6px;
                color: #1e3a8a;
                text-decoration: none;
                transition: all 0.3s ease;
            }

            .nav-menu.active li a:hover {
                background: #f3f4f6;
                color: #3b82f6;
            }

            /* Mobile responsive styles */
            @media (max-width: 768px) {
                .mobile-menu-toggle {
                    display: block;
                }

                .header-center {
                    position: relative;
                }

                .nav-menu {
                    display: none;
                }

                .nav-menu.active {
                    display: flex;
                }

                .dropdown .dropdown-menu {
                    position: static;
                    box-shadow: none;
                    background: transparent;
                    border: none;
                    padding: 0;
                    display: block;
                    opacity: 1;
                    visibility: visible;
                    transform: none;
                }

                .dropdown .dropdown-menu li {
                    margin-left: 1rem;
                }

                .dropdown .dropdown-menu li a {
                    color: #64748b;
                    padding: 0.5rem 0.75rem;
                }

                .dropdown .dropdown-menu li a:hover {
                    color: #3b82f6;
                    background: transparent;
                }
            }
        `;
        document.head.appendChild(style);

        // Mobile menu toggle
        function initMobileMenu() {
            const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
            const navMenu = document.querySelector('.nav-menu');

            if (mobileMenuToggle && navMenu) {
                mobileMenuToggle.addEventListener('click', function (e) {
                    e.preventDefault();
                    e.stopPropagation();

                    navMenu.classList.toggle('active');
                    mobileMenuToggle.classList.toggle('active');
                });

                // Close menu when clicking outside
                document.addEventListener('click', function (e) {
                    if (!document.querySelector('.global-nav').contains(e.target)) {
                        navMenu.classList.remove('active');
                        mobileMenuToggle.classList.remove('active');
                    }
                });
            }
        }

        // Dropdown functionality
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
                .then(() => { })
                .catch(() => { });
        });
    }

})();
