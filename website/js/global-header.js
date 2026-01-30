// Global Header Loading Script
document.addEventListener('DOMContentLoaded', function() {
    // Load global header
    fetch('components/header.html')
        .then(response => response.text())
        .then(html => {
            // Parse the HTML to extract just the header content
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const headerElement = doc.querySelector('.global-header');
            
            if (headerElement) {
                // Insert the header at the beginning of the body
                document.body.insertBefore(headerElement, document.body.firstChild);
                
                // Add mobile menu toggle functionality
                addMobileMenuToggle();
                
                // Add dropdown functionality
                addDropdownFunctionality();
            }
        })
        .catch(error => {
            console.error('Error loading global header:', error);
        });
});

function addMobileMenuToggle() {
    // Create mobile menu toggle button if it doesn't exist
    const existingToggle = document.querySelector('.mobile-menu-toggle');
    if (!existingToggle) {
        const header = document.querySelector('.global-header');
        if (header) {
            const toggleButton = document.createElement('button');
            toggleButton.className = 'mobile-menu-toggle';
            toggleButton.innerHTML = '<i class="fas fa-bars"></i>';
            toggleButton.setAttribute('aria-label', 'Toggle mobile menu');
            
            // Insert toggle button after the logo
            const logoContainer = header.querySelector('.header-left');
            if (logoContainer) {
                logoContainer.appendChild(toggleButton);
                
                // Add click event to toggle mobile menu
                toggleButton.addEventListener('click', function() {
                    const navMenu = header.querySelector('.nav-menu');
                    if (navMenu) {
                        navMenu.classList.toggle('mobile-active');
                        toggleButton.classList.toggle('active');
                    }
                });
            }
        }
    }
}

function addDropdownFunctionality() {
    // Bootstrap dropdowns are now handled by Bootstrap JS
    // This function is kept for potential future custom dropdown needs
    console.log('Dropdown functionality managed by Bootstrap JS');
}
