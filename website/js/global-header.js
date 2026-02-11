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
            })
            .catch(error => {
                console.error("Header load failed:", error);
            });
    }

    document.addEventListener('DOMContentLoaded', loadHeader);

})();
