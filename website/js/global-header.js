(function () {
    'use strict';

    function initHeader() {
        const hamburger = document.querySelector('.mobile-menu-toggle');
        const navMenu = document.querySelector('.nav-menu');
        const body = document.body;

        if (!hamburger || !navMenu) {
            console.warn("Hamburger or nav menu not found");
            return;
        }

        console.log("Hamburger initialized");

        // Remove old listener safety (prevents duplicates)
        hamburger.onclick = null;

        hamburger.addEventListener('click', function (e) {
            e.preventDefault();
            console.log("Hamburger clicked");

            // Toggle menu state
            const isMenuOpen = navMenu.classList.contains('mobile-active');
            console.log("Menu is currently open:", isMenuOpen);
            console.log("Nav menu element:", navMenu);
            console.log("Nav menu computed style:", window.getComputedStyle(navMenu));
            console.log("Nav menu left position:", window.getComputedStyle(navMenu).left);
            console.log("Nav menu display property:", window.getComputedStyle(navMenu).display);
            console.log("Nav menu position property:", window.getComputedStyle(navMenu).position);
            console.log("Nav menu width:", window.getComputedStyle(navMenu).width);
            console.log("Nav menu height:", window.getComputedStyle(navMenu).height);
            
            if (isMenuOpen) {
                // Close menu
                console.log("Closing menu");
                navMenu.classList.remove('mobile-active');
                hamburger.classList.remove('active');
                body.style.overflow = '';
                console.log("After closing - left position:", window.getComputedStyle(navMenu).left);
            } else {
                // Open menu
                console.log("Opening menu");
                navMenu.classList.add('mobile-active');
                hamburger.classList.add('active');
                body.style.overflow = 'hidden';
                console.log("After opening - left position:", window.getComputedStyle(navMenu).left);
                console.log("After opening - display property:", window.getComputedStyle(navMenu).display);
            }
        });

        // Close on ESC
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                console.log("ESC key pressed, closing menu");
                navMenu.classList.remove('mobile-active');
                hamburger.classList.remove('active');
                body.style.overflow = '';
            }
        });
    }

    function loadHeader() {
        console.log("Loading header...");

        const existingHeader = document.querySelector('.global-header');

        // Only skip loading if header already contains nav menu
        if (existingHeader && existingHeader.querySelector('.nav-menu')) {
            console.log("Header already exists, initializing...");
            initHeader();
            return;
        }

        fetch('components/header.html')
            .then(response => {
                if (!response.ok) throw new Error("Header fetch failed: " + response.status);
                return response.text();
            })
            .then(html => {
                console.log("Header HTML loaded successfully");
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const headerElement = doc.querySelector('.global-header');

                if (!headerElement) {
                    console.error("Header not found inside header.html");
                    return;
                }

                console.log("Inserting header into DOM");
                document.body.insertBefore(headerElement, document.body.firstChild);

                // Wait for DOM paint
                requestAnimationFrame(() => {
                    console.log("DOM painted, initializing header...");
                    initHeader();
                });
            })
            .catch(error => {
                console.error("Header load failed:", error);
            });
    }

    if (document.readyState === 'loading') {
        console.log("Document is loading, waiting for DOMContentLoaded");
        document.addEventListener('DOMContentLoaded', loadHeader);
    } else {
        console.log("Document already loaded, loading header now");
        loadHeader();
    }

})();
