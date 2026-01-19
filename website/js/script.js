// Mobile navigation toggle


document.addEventListener('DOMContentLoaded', function() {
    // Header scroll effect
    const header = document.querySelector('header');
    let lastScrollY = window.scrollY;

    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;

        if (currentScrollY > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }

        lastScrollY = currentScrollY;
    });

    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerOffset = 100;
                const elementPosition = target.offsetTop;
                const offsetPosition = elementPosition - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    const navToggle = document.createElement('div');
    navToggle.innerHTML = '☰';
    navToggle.style.cssText = `
        display: none;
        font-size: 1.5rem;
        cursor: pointer;
        position: absolute;
        right: 2rem;
        top: 50%;
        transform: translateY(-50%);
        color: #1e293b;
        z-index: 1001;
        transition: all 0.3s ease;
    `;

    const nav = document.querySelector('nav');
    const navMenu = document.querySelector('.nav-menu');
    
    // Add toggle button for mobile
    if (window.innerWidth <= 768) {
        nav.style.position = 'relative';
        nav.appendChild(navToggle);
        navToggle.style.display = 'block';

        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });

        // Mobile dropdown click handlers
        const mobileDropdowns = navMenu.querySelectorAll('.dropdown');
        mobileDropdowns.forEach(dropdown => {
            const link = dropdown.querySelector('a');
            const menu = dropdown.querySelector('.dropdown-menu');

            link.addEventListener('click', function(e) {
                e.preventDefault();

                // Close all other submenus (accordion behavior)
                mobileDropdowns.forEach(otherDropdown => {
                    if (otherDropdown !== dropdown) {
                        const otherMenu = otherDropdown.querySelector('.dropdown-menu');
                        if (otherMenu) {
                            otherMenu.classList.remove('open');
                        }
                    }
                });

                // Toggle current submenu
                if (menu) {
                    menu.classList.toggle('open');
                }
            });
        });
    }
    
    // Dropdown click handlers for both desktop and mobile
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        const link = dropdown.querySelector('a');
        const menu = dropdown.querySelector('.dropdown-menu');

        link.addEventListener('click', function(e) {
            e.preventDefault();

            // Close all other submenus (accordion behavior)
            dropdowns.forEach(otherDropdown => {
                if (otherDropdown !== dropdown) {
                    const otherMenu = otherDropdown.querySelector('.dropdown-menu');
                    if (otherMenu) {
                        otherMenu.classList.remove('open');
                    }
                }
            });

            // Toggle current submenu
            if (menu) {
                menu.classList.toggle('open');
            }
        });
    });
    
    // Form submission with email sending
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault(); // Always prevent default submission

            const requiredInputs = form.querySelectorAll('input[required], select[required], textarea[required]');
            let isValid = true;

            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    input.style.borderColor = '#e74c3c';
                    isValid = false;
                } else {
                    input.style.borderColor = '#ddd';
                }
            });

            if (!isValid) {
                alert('Please fill in all required fields.');
                return;
            }

            // Collect form data
            const formData = new FormData(form);

            // Send email via PHP
            fetch('send_email.php', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Message sent successfully!');
                    form.reset(); // Clear the form
                } else {
                    alert('Failed to send message: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to send message. Please try again.');
            });
        });
    });
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // FAQ accordion
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        const question = item.querySelector('h3');
        const answer = item.querySelector('p');
        
        // Initially hide answers
        answer.style.display = 'none';
        
        question.addEventListener('click', function() {
            const isVisible = answer.style.display === 'block';
            answer.style.display = isVisible ? 'none' : 'block';
            
            // Add/remove active class for styling
            this.classList.toggle('active');
        });
    });
    
    // Image lazy loading placeholder
    const images = document.querySelectorAll('img[src*="placeholder"]');
    images.forEach(img => {
        img.style.backgroundColor = '#f0f0f0';
        img.style.display = 'block';
        img.style.width = '100%';
        img.style.height = 'auto';
        img.style.minHeight = '200px';
        img.style.borderRadius = '8px';
        
        // Add placeholder text
        const placeholderText = document.createElement('div');
        placeholderText.textContent = 'Image Placeholder';
        placeholderText.style.cssText = `
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #888;
            font-size: 0.9rem;
            pointer-events: none;
        `;
        
        const container = document.createElement('div');
        container.style.position = 'relative';
        img.parentNode.insertBefore(container, img);
        container.appendChild(img);
        container.appendChild(placeholderText);
    });

    // Video modal functionality
    const videoModal = document.getElementById('video-modal');
    const modalVideo = document.getElementById('modal-video');
    const modalBackdrop = document.getElementById('video-modal-backdrop');
    const modalClose = document.getElementById('video-modal-close');

    // Function to open video modal
    function openVideoModal(videoSrc) {
        modalVideo.src = videoSrc;
        modalVideo.currentTime = 0;
        videoModal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent background scrolling

        // Play video when modal opens
        modalVideo.play().catch(function(error) {
            console.log('Video play failed:', error);
            // Fallback: show alert for video hosting issues
            alert('Video playback requires proper hosting configuration. Please ensure video files are correctly uploaded and server supports video streaming.');
        });
    }

    // Function to close video modal
    function closeVideoModal() {
        videoModal.style.display = 'none';
        modalVideo.pause();
        modalVideo.src = ''; // Clear src to stop loading
        document.body.style.overflow = ''; // Restore scrolling
    }

    // Close modal when clicking backdrop
    modalBackdrop.addEventListener('click', closeVideoModal);

    // Close modal when clicking close button
    modalClose.addEventListener('click', closeVideoModal);

    // Close modal on ESC key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && videoModal.style.display === 'block') {
            closeVideoModal();
        }
    });

    // Video playback functionality for home page and gallery videos
    const allVideoContainers = document.querySelectorAll('.video-item, .video-item-gallery');
    allVideoContainers.forEach(container => {
        const video = container.querySelector('video');
        const playButton = container.querySelector('.play-button, .play-button-gallery');
        const playOverlay = container.querySelector('.play-overlay, .play-overlay-gallery');

        if (video && playButton) {
            // Handle play button click - now opens modal
            playButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                const videoSrc = video.querySelector('source').src;
                openVideoModal(videoSrc);
            });

            // Handle container click to open modal
            container.addEventListener('click', function(e) {
                // Only open modal if not clicking on play button directly
                if (!e.target.closest('.play-button, .play-button-gallery')) {
                    const videoSrc = video.querySelector('source').src;
                    openVideoModal(videoSrc);
                }
            });

            // Auto-play on hover for muted videos (if supported) - keep this for thumbnail preview
            if (video.muted && video.loop) {
                container.addEventListener('mouseenter', function() {
                    video.play().catch(function(error) {
                        // Silent fail for auto-play restrictions
                        console.log('Auto-play failed:', error);
                    });
                });

                container.addEventListener('mouseleave', function() {
                    video.pause();
                    video.currentTime = 0;
                });
            }
        }
    });

    // Responsive adjustments
    window.addEventListener('resize', function() {
        if (window.innerWidth <= 768) {
            navToggle.style.display = 'block';
            navMenu.classList.remove('active');
        } else {
            navToggle.style.display = 'none';
            navMenu.classList.add('active'); // Ensure menu is always visible on desktop
        }
    });

    // Search Chefs functionality
    const searchChefsBtn = document.getElementById('search-chefs-btn');
    if (searchChefsBtn) {
        searchChefsBtn.addEventListener('click', function() {
            performChefSearch();
        });

        // Also trigger search on Enter key in input fields
        const searchInputs = document.querySelectorAll('#location-search, #cuisine-search, #dietary-search');
        searchInputs.forEach(input => {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    performChefSearch();
                }
            });
        });
    }

    function performChefSearch() {
        const location = document.getElementById('location-search').value.trim().toLowerCase();
        const cuisine = document.getElementById('cuisine-search').value;
        const dietary = document.getElementById('dietary-search').value;

        // Get all chef cards and no results element
        const chefCards = document.querySelectorAll('.chef-card');
        const noResults = document.getElementById('no-results');
        const chefCardsContainer = document.querySelector('.chef-cards');

        let visibleCount = 0;

        chefCards.forEach(card => {
            let showCard = true;

            // Location filter - expand to include more California cities
            if (location && location !== '') {
                const cardLocation = card.getAttribute('data-location') || '';
                const validLocations = ['california', 'ca', 'san jose', 'san francisco', 'los angeles', 'la', 'sacramento', 'fresno', 'bakersfield'];
                if (!validLocations.some(loc => loc.includes(location) || location.includes(loc))) {
                    showCard = false;
                }
            }

            // Cuisine filter
            if (cuisine && cuisine !== '') {
                const cardCuisine = card.getAttribute('data-cuisine');
                if (cardCuisine !== cuisine) {
                    showCard = false;
                }
            }

            // Dietary filter
            if (dietary && dietary !== '') {
                const cardDiet = card.getAttribute('data-diet') || '';
                if (!cardDiet.includes(dietary)) {
                    showCard = false;
                }
            }

            // Show/hide card with animation
            if (showCard) {
                card.style.display = 'block';
                card.style.opacity = '0';
                setTimeout(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, 50);
                visibleCount++;
            } else {
                card.style.display = 'none';
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
            }
        });

        // Show/hide no results message with better styling
        if (visibleCount === 0) {
            noResults.style.display = 'block';
            noResults.innerHTML = `
                <div style="padding: 40px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <i class="fas fa-search" style="font-size: 3rem; color: #ccc; margin-bottom: 20px;"></i>
                    <h3 style="color: #666; margin-bottom: 10px;">No chefs found matching your criteria</h3>
                    <p style="color: #999; margin-bottom: 20px;">Try adjusting your search filters or browse all available chefs.</p>
                    <button onclick="resetSearch()" style="background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer;">Show All Chefs</button>
                </div>
            `;
            if (chefCardsContainer) chefCardsContainer.style.display = 'none';
        } else {
            noResults.style.display = 'none';
            if (chefCardsContainer) chefCardsContainer.style.display = 'grid';
        }

        // Provide user feedback
        const feedback = document.createElement('div');
        feedback.id = 'search-feedback';
        feedback.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: #007bff;
            color: white;
            padding: 10px 20px;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            z-index: 1000;
            opacity: 0;
            transform: translateY(-20px);
            transition: all 0.3s ease;
        `;

        // Remove existing feedback
        const existingFeedback = document.getElementById('search-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        feedback.textContent = `Found ${visibleCount} chef${visibleCount !== 1 ? 's' : ''} matching your criteria`;
        document.body.appendChild(feedback);

        // Animate feedback
        setTimeout(() => {
            feedback.style.opacity = '1';
            feedback.style.transform = 'translateY(0)';
        }, 100);

        // Remove feedback after 3 seconds
        setTimeout(() => {
            feedback.style.opacity = '0';
            feedback.style.transform = 'translateY(-20px)';
            setTimeout(() => feedback.remove(), 300);
        }, 3000);
    }

    // Function to reset search
    function resetSearch() {
        document.getElementById('location-search').value = '';
        document.getElementById('cuisine-search').value = '';
        document.getElementById('dietary-search').value = '';

        const chefCards = document.querySelectorAll('.chef-card');
        const noResults = document.getElementById('no-results');
        const chefCardsContainer = document.querySelector('.chef-cards');

        chefCards.forEach(card => {
            card.style.display = 'block';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        });

        noResults.style.display = 'none';
        if (chefCardsContainer) chefCardsContainer.style.display = 'grid';
    }
});

// Utility function for creating placeholders
function createPlaceholderImage(alt, width = 300, height = 200) {
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    
    // Background
    ctx.fillStyle = '#f0f0f0';
    ctx.fillRect(0, 0, width, height);
    
    // Border
    ctx.strokeStyle = '#ddd';
    ctx.lineWidth = 2;
    ctx.strokeRect(0, 0, width, height);
    
    // Text
    ctx.fillStyle = '#888';
    ctx.font = '16px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Placeholder', width/2, height/2 - 10);
    ctx.fillText('Image', width/2, height/2 + 10);
    
    return canvas.toDataURL();
}
