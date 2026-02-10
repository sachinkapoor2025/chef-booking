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

            navMenu.classList.toggle('mobile-active');
            hamburger.classList.toggle('active');

            // Lock scroll when menu open
            if (navMenu.classList.contains('mobile-active')) {
                body.style.overflow = 'hidden';
            } else {
                body.style.overflow = '';
            }
        });

        // Close on ESC
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                navMenu.classList.remove('mobile-active');
                hamburger.classList.remove('active');
                body.style.overflow = '';
            }
        });
    }

    function loadHeader() {

        const existingHeader = document.querySelector('.global-header');

        // Only skip loading if header already contains nav menu
        if (existingHeader && existingHeader.querySelector('.nav-menu')) {
            initHeader();
            return;
        }

        fetch('components/header.html')
            .then(response => {
                if (!response.ok) throw new Error("Header fetch failed");
                return response.text();
            })
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const headerElement = doc.querySelector('.global-header');

                if (!headerElement) {
                    console.error("Header not found inside header.html");
                    return;
                }

                document.body.insertBefore(headerElement, document.body.firstChild);

                // Wait for DOM paint
                requestAnimationFrame(initHeader);
            })
            .catch(error => {
                console.error("Header load failed:", error);
            });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadHeader);
    } else {
        loadHeader();
    }

})();
