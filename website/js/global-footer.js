// Global Footer Component
// This file injects a consistent footer across all pages

document.addEventListener('DOMContentLoaded', function() {
    const footerHTML = `
    <footer>
        <div class="footer-content">
            <div class="footer-column">
                <h3>Maharaja Chef Services</h3>
                <p>Premium live counters and catering services. Bringing authentic Indian street food to your events.</p>
            </div>
            <div class="footer-column">
                <h3>Live Counters</h3>
                <ul>
                    <li><a href="pani-puri.html">Pani Puri</a></li>
                    <li><a href="dahi-puri.html">Dahi Puri</a></li>
                    <li><a href="dahi-vada.html">Dahi Vada</a></li>
                    <li><a href="papdi-chaat.html">Papdi Chaat</a></li>
                </ul>
            </div>
            <div class="footer-column">
                <h3>Quick Links</h3>
                <ul>
                    <li><a href="index.html">Home</a></li>
                    <li><a href="about-us.html">About Us</a></li>
                    <li><a href="contact-us.html">Contact Us</a></li>
                    <li><a href="enquiry-form.html">Enquiry</a></li>
                </ul>
            </div>
            <div class="footer-column">
                <h3>Contact Us</h3>
                <div class="contact-info" style="color: #333;">
                    <p><i class="fas fa-phone"></i> 408-690-1610</p>
                    <p><i class="fas fa-envelope"></i> info@maharajachef.com</p>
                </div>
                <div class="social-media">
                    <a href="https://www.facebook.com/profile.php?id=61587294953271" target="_blank" aria-label="Facebook"><i class="fab fa-facebook-f"></i></a>
                    <a href="https://www.instagram.com/maharajachef/?hl=en" target="_blank" aria-label="Instagram"><i class="fab fa-instagram"></i></a>
                    <a href="https://x.com/maharajachef" target="_blank" aria-label="Twitter"><i class="fab fa-twitter"></i></a>
                </div>
            </div>
        </div>
        <hr>
        <div class="footer-bottom">
            <p>&copy; 2026 Maharaja Chef Services. All rights reserved.</p>
        </div>
    </footer>
    `;
    
    // Find existing footer and replace it, or append to body if no footer exists
    const existingFooter = document.querySelector('footer');
    if (existingFooter) {
        existingFooter.outerHTML = footerHTML;
    } else {
        document.body.insertAdjacentHTML('beforeend', footerHTML);
    }
});