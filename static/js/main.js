/**
 * Main JavaScript file for Investment Portal
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize bottom navigation active state
    const currentPath = window.location.pathname;
    
    // Get all navigation links
    const navLinks = document.querySelectorAll('.bottom-nav .nav-link');
    
    // Check current path and set active class
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (currentPath === href || 
            (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        }
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('.copy-to-clipboard');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-clipboard-text');
            navigator.clipboard.writeText(textToCopy).then(() => {
                // Change button text temporarily
                const originalText = this.innerHTML;
                this.innerHTML = 'Copied!';
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 2000);
            }).catch(err => {
                console.error('Could not copy text: ', err);
            });
        });
    });
    
    // Home page slider initialization
    const sliderElement = document.querySelector('.carousel');
    if (sliderElement) {
        const carousel = new bootstrap.Carousel(sliderElement, {
            interval: 5000,
            wrap: true,
            keyboard: false
        });
    }
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // QR Code display toggle
    const qrToggleButtons = document.querySelectorAll('.toggle-qr-code');
    qrToggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const qrCode = document.getElementById(this.getAttribute('data-target'));
            if (qrCode.classList.contains('d-none')) {
                qrCode.classList.remove('d-none');
                this.textContent = 'Hide QR Code';
            } else {
                qrCode.classList.add('d-none');
                this.textContent = 'Show QR Code';
            }
        });
    });
    
    // Investment plan selection
    const planCards = document.querySelectorAll('.plan-card');
    planCards.forEach(card => {
        card.addEventListener('click', function() {
            // Remove 'selected' class from all cards
            planCards.forEach(c => c.classList.remove('border-primary'));
            // Add 'selected' class to clicked card
            this.classList.add('border-primary');
            
            // Get plan ID from data attribute
            const planId = this.getAttribute('data-plan-id');
            
            // Update hidden input for form submission
            const planInput = document.getElementById('selected_plan_id');
            if (planInput) {
                planInput.value = planId;
            }
        });
    });
});

/**
 * Format currency with 2 decimal places
 * @param {number} amount - Amount to format
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2);
}

/**
 * Format date to readable string
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date string
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

/**
 * Show confirmation dialog
 * @param {string} message - Confirmation message
 * @param {function} callback - Function to call on confirm
 */
function showConfirmation(message, callback) {
    if (confirm(message)) {
        callback();
    }
}
