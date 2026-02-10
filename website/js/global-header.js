(function () {
    'use strict';

    function initHeader() {

        const hamburger = document.querySelector('.mobile-menu-toggle');
        const navMenu = document.querySelector('.nav-menu');
        const body = document.body;

        if (!hamburger || !navMenu) {
            console.warn("Header elements not found after load");
            return;
        }

        console.log("Header initialized successfully");

        // Toggle hamburger menu
        hamburger.addEventListener('click', function (e) {
            e.preventDefault();

            navMenu.classList.toggle('mobile-active');
            hamburger.classList.toggle('active');

            if (navMenu.classList.contains('mobile-active')) {
                body.style.overflow = 'hidden';
            } else {
                body.style.overflow = '';
            }
        });

        // Close menu on Escape
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                navMenu.classList.remove('mobile-active');
                hamburger.classList.remove('active');
                body.style.overflow = '';
            }
        });

        // Dropdown toggle
        const dropdownToggles = document.querySelectorAll('.dropdown-toggle');

        dropdownToggles.forEach(toggle => {
            toggle.addEventListener('click', function (e) {
                e.preventDefault();
                const parent = this.closest('.dropdown');
                parent.classList.toggle('active');
            });
        });
    }

    function loadHeader() {
        fetch('components/header.html')
            .then(response => {
                console.log("HEADER RESPONSE:", response);
                return response.text();
            })
            .then(html => {

                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const headerElement = doc.querySelector('.global-header');

                console.log("HEADER ELEMENT FOUND:", headerElement);

                if (!headerElement) {
                    console.error("Header not found inside header.html");
                    return;
                }

                document.body.insertBefore(headerElement, document.body.firstChild);

                // IMPORTANT: initialize AFTER inserting header
                initHeader();
            })
            .catch(error => {
                console.error("HEADER LOAD FAILED:", error);
            });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadHeader);
    } else {
        loadHeader();
    }

})();
