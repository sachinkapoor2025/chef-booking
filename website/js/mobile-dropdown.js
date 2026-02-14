// Mobile Dropdown Toggle Functionality
// This script handles dropdown menus on mobile devices

(function() {
    'use strict';

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMobileDropdowns);
    } else {
        initMobileDropdowns();
    }

    function initMobileDropdowns() {
        // Wait until header is loaded (for dynamic headers)
        const observer = new MutationObserver(function() {
            setupDropdownListeners();
        });

        observer.observe(document.body, { childList: true, subtree: true });

        // Also try immediately in case header is already there
        setupDropdownListeners();
    }

    function setupDropdownListeners() {
        const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
        
        dropdownToggles.forEach(function(toggle) {
            // Remove existing listeners to avoid duplicates
            toggle.removeEventListener('click', handleDropdownClick);
            toggle.addEventListener('click', handleDropdownClick);
        });
    }

    function handleDropdownClick(e) {
        // Only handle on mobile (screen width <= 992px)
        if (window.innerWidth > 992) return;

        e.preventDefault();
        e.stopPropagation();

        const dropdown = this.closest('.dropdown');
        const menu = dropdown.querySelector('.dropdown-menu');
        const isOpen = menu.style.display === 'block';

        // Close all other dropdowns
        document.querySelectorAll('.dropdown-menu').forEach(function(m) {
            m.style.display = 'none';
        });
        document.querySelectorAll('.dropdown').forEach(function(d) {
            d.classList.remove('active');
        });

        // Toggle current dropdown
        if (!isOpen) {
            menu.style.display = 'block';
            dropdown.classList.add('active');
        }
    }

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu').forEach(function(m) {
                m.style.display = 'none';
            });
            document.querySelectorAll('.dropdown').forEach(function(d) {
                d.classList.remove('active');
            });
        }
    });

})();
