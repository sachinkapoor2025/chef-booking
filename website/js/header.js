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

        hamburger.onclick = null;

        hamburger.addEventListener('click', function (e) {
            e.preventDefault();

            const isMenuOpen = navMenu.classList.contains('mobile-active');

            if (isMenuOpen) {
                navMenu.classList.remove('mobile-active');
                hamburger.classList.remove('active');
                body.style.overflow = '';
            } else {
                navMenu.classList.add('mobile-active');
                hamburger.classList.add('active');
                body.style.overflow = 'hidden';
            }
        });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                navMenu.classList.remove('mobile-active');
                hamburger.classList.remove('active');
                body.style.overflow = '';
            }
        });
    }

    document.addEventListener("DOMContentLoaded", initHeader);

})();
