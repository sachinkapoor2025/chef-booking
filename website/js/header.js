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
