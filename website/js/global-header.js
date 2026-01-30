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
    // Add click event listeners to dropdown triggers
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        const trigger = dropdown.querySelector('a');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (trigger && menu) {
            // Prevent default link behavior for dropdown triggers
            trigger.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Toggle dropdown visibility
                dropdown.classList.toggle('active');
                
                // Close other dropdowns
                dropdowns.forEach(otherDropdown => {
                    if (otherDropdown !== dropdown) {
                        otherDropdown.classList.remove('active');
                    }
                });
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (!dropdown.contains(e.target)) {
                    dropdown.classList.remove('active');
                }
            });
        }
    });
}
