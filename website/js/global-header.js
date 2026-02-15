(function () {
    'use strict';

    function loadHeader() {

        const existingHeader = document.querySelector('.global-header');
        if (existingHeader) return;

        fetch('components/header.html')
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const headerElement = doc.querySelector('.global-header');

                document.getElementById('header-container')
                    .appendChild(headerElement);
                
                // Load mobile dropdown script after header is inserted
                loadMobileDropdownScript();
            })
            .catch(error => {
                console.error("Header load failed:", error);
            });
    }
    
    function loadMobileDropdownScript() {
        // Check if already loaded
        if (document.querySelector('script[src="js/mobile-dropdown.js"]')) {
            return;
        }
        
        const script = document.createElement('script');
        script.src = 'js/mobile-dropdown.js';
        script.async = true;
        document.body.appendChild(script);
    }

    document.addEventListener('DOMContentLoaded', loadHeader);

})();
