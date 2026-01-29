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
    // Add dropdown functionality for desktop hover and mobile click
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        const link = dropdown.querySelector('a');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        // Show dropdown on hover for desktop
        dropdown.addEventListener('mouseenter', () => {
            if (window.innerWidth > 768) {
                menu.style.display = 'block';
                dropdown.classList.add('hover');
            }
        });
        
        dropdown.addEventListener('mouseleave', () => {
            if (window.innerWidth > 768) {
                menu.style.display = 'none';
                dropdown.classList.remove('hover');
            }
        });
        
        // Toggle dropdown on click for mobile
        link.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                const isVisible = menu.style.display === 'block';
                // Hide all other dropdowns
                document.querySelectorAll('.dropdown-menu').forEach(m => {
                    if (m !== menu) m.style.display = 'none';
                });
                // Toggle current dropdown
                menu.style.display = isVisible ? 'none' : 'block';
                dropdown.classList.toggle('active', !isVisible);
            }
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 && !e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.style.display = 'none';
            });
            document.querySelectorAll('.dropdown').forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    });
}
