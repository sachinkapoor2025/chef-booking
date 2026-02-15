// Mobile Dropdown Toggle Functionality
// This script handles dropdown menus on mobile devices

(function() {
    'use strict';

    let isInitialized = false;

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMobileDropdowns);
    } else {
        initMobileDropdowns();
    }

    function initMobileDropdowns() {
        // Wait until header is loaded (for dynamic headers)
        const observer = new MutationObserver(function(mutations) {
            const headerLoaded = document.querySelector('.global-header');
            const navMenu = document.querySelector('.nav-menu');
            if (headerLoaded && navMenu && !isInitialized) {
                setupDropdownListeners();
            }
        });

        observer.observe(document.body, { childList: true, subtree: true });

        // Also try immediately in case header is already there
        setupDropdownListeners();
    }

    function setupDropdownListeners() {
        const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
        
        if (dropdownToggles.length === 0) return;
        
        isInitialized = true;
        
        dropdownToggles.forEach(function(toggle) {
            // Remove existing listeners to avoid duplicates
            toggle.removeEventListener('click', handleDropdownClick);
            toggle.addEventListener('click', handleDropdownClick);
        });
        
        console.log('Mobile dropdown listeners attached to', dropdownToggles.length, 'dropdowns');
    }

    function handleDropdownClick(e) {
        // Only handle on mobile (screen width <= 992px)
        if (window.innerWidth > 992) return;

        e.preventDefault();
        e.stopPropagation();

        const dropdown = this.closest('.dropdown');
        if (!dropdown) return;
        
        const menu = dropdown.querySelector('.dropdown-menu');
        if (!menu) return;
        
        const isOpen = dropdown.classList.contains('active');

        // Close all other dropdowns
        document.querySelectorAll('.dropdown').forEach(function(d) {
            d.classList.remove('active');
        });

        // Toggle current dropdown
        if (!isOpen) {
            dropdown.classList.add('active');
        }
    }

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown').forEach(function(d) {
                d.classList.remove('active');
            });
        }
    });

    // Handle window resize - close mobile dropdowns when going to desktop
    window.addEventListener('resize', function() {
        if (window.innerWidth > 992) {
            document.querySelectorAll('.dropdown').forEach(function(d) {
                d.classList.remove('active');
            });
        }
    });

})();
