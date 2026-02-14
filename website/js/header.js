(function () {
    'use strict';

    function initHeader() {
        const hamburger = document.querySelector('.mobile-menu-toggle');
        const navMenu = document.querySelector('.nav-menu');
        const body = document.body;

        if (!hamburger || !navMenu) return;

        hamburger.onclick = null;

        hamburger.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const isMenuOpen = navMenu.classList.contains('active');

            if (isMenuOpen) {
                navMenu.classList.remove('active');
                hamburger.classList.remove('active');
                body.style.overflow = '';
            } else {
                navMenu.classList.add('active');
                hamburger.classList.add('active');
                body.style.overflow = 'hidden';
            }
        });

        // Close menu when clicking on a link
        const navLinks = navMenu.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                hamburger.classList.remove('active');
                body.style.overflow = '';
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!navMenu.contains(e.target) && !hamburger.contains(e.target)) {
                navMenu.classList.remove('active');
                hamburger.classList.remove('active');
                body.style.overflow = '';
            }
        });
    }

    // Wait until header is inserted
    const observer = new MutationObserver(() => {
        if (document.querySelector('.mobile-menu-toggle')) {
            initHeader();
            observer.disconnect();
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });

})();
