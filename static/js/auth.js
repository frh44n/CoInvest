/**
 * Authentication related JavaScript for Investment Portal
 */

document.addEventListener('DOMContentLoaded', function() {
    // Password toggle visibility
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const passwordInput = document.querySelector(this.getAttribute('data-target'));
            
            // Toggle password visibility
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                this.innerHTML = '<i class="fas fa-eye-slash"></i>';
            } else {
                passwordInput.type = 'password';
                this.innerHTML = '<i class="fas fa-eye"></i>';
            }
        });
    });
    
    // Password strength meter
    const passwordInput = document.getElementById('password');
    const passwordStrength = document.getElementById('password-strength');
    
    if (passwordInput && passwordStrength) {
        passwordInput.addEventListener('input', function() {
            const strength = calculatePasswordStrength(this.value);
            updatePasswordStrengthUI(strength, passwordStrength);
        });
    }
    
    // Password confirmation validation
    const passwordConfirmInput = document.getElementById('confirm_password');
    if (passwordInput && passwordConfirmInput) {
        passwordConfirmInput.addEventListener('input', function() {
            validatePasswordMatch(passwordInput.value, this.value);
        });
    }
    
    // Registration form validation
    const registrationForm = document.getElementById('registration-form');
    if (registrationForm) {
        registrationForm.addEventListener('submit', function(event) {
            // Validate form fields
            const email = document.getElementById('email').value;
            const mobile = document.getElementById('mobile').value;
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            
            let isValid = true;
            
            // Email validation
            if (!isValidEmail(email)) {
                document.getElementById('email-feedback').textContent = 'Please enter a valid email address.';
                document.getElementById('email').classList.add('is-invalid');
                isValid = false;
            }
            
            // Mobile validation
            if (!isValidMobile(mobile)) {
                document.getElementById('mobile-feedback').textContent = 'Please enter a valid mobile number.';
                document.getElementById('mobile').classList.add('is-invalid');
                isValid = false;
            }
            
            // Username validation
            if (username.length < 3) {
                document.getElementById('username-feedback').textContent = 'Username must be at least 3 characters.';
                document.getElementById('username').classList.add('is-invalid');
                isValid = false;
            }
            
            // Password validation
            if (calculatePasswordStrength(password) < 2) {
                document.getElementById('password-feedback').textContent = 'Password is too weak.';
                document.getElementById('password').classList.add('is-invalid');
                isValid = false;
            }
            
            // Confirm password validation
            if (password !== confirmPassword) {
                document.getElementById('confirm-password-feedback').textContent = 'Passwords do not match.';
                document.getElementById('confirm_password').classList.add('is-invalid');
                isValid = false;
            }
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    }
});

/**
 * Calculate password strength
 * @param {string} password - Password to evaluate
 * @returns {number} Strength score (0-4)
 */
function calculatePasswordStrength(password) {
    let strength = 0;
    
    if (password.length === 0) {
        return strength;
    }
    
    // Length check
    if (password.length >= 8) {
        strength += 1;
    }
    
    // Complexity checks
    if (/[a-z]/.test(password)) {
        strength += 1;
    }
    
    if (/[A-Z]/.test(password)) {
        strength += 1;
    }
    
    if (/[0-9]/.test(password)) {
        strength += 1;
    }
    
    if (/[^a-zA-Z0-9]/.test(password)) {
        strength += 1;
    }
    
    return Math.min(strength, 4);
}

/**
 * Update password strength UI
 * @param {number} strength - Password strength score
 * @param {HTMLElement} element - UI element to update
 */
function updatePasswordStrengthUI(strength, element) {
    // Remove all classes
    element.className = 'progress-bar';
    
    // Set width based on strength
    element.style.width = (strength * 25) + '%';
    
    // Add appropriate color class
    switch (strength) {
        case 0:
            element.classList.add('bg-danger');
            element.textContent = 'Very Weak';
            break;
        case 1:
            element.classList.add('bg-danger');
            element.textContent = 'Weak';
            break;
        case 2:
            element.classList.add('bg-warning');
            element.textContent = 'Medium';
            break;
        case 3:
            element.classList.add('bg-info');
            element.textContent = 'Strong';
            break;
        case 4:
            element.classList.add('bg-success');
            element.textContent = 'Very Strong';
            break;
    }
}

/**
 * Validate password matching
 * @param {string} password - Original password
 * @param {string} confirmPassword - Confirmation password
 */
function validatePasswordMatch(password, confirmPassword) {
    const confirmInput = document.getElementById('confirm_password');
    const feedbackElement = document.getElementById('confirm-password-feedback');
    
    if (password === confirmPassword) {
        confirmInput.classList.remove('is-invalid');
        confirmInput.classList.add('is-valid');
        feedbackElement.textContent = 'Passwords match.';
        feedbackElement.classList.remove('invalid-feedback');
        feedbackElement.classList.add('valid-feedback');
    } else {
        confirmInput.classList.remove('is-valid');
        confirmInput.classList.add('is-invalid');
        feedbackElement.textContent = 'Passwords do not match.';
        feedbackElement.classList.remove('valid-feedback');
        feedbackElement.classList.add('invalid-feedback');
    }
}

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} Is valid email
 */
function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Validate mobile number
 * @param {string} mobile - Mobile to validate
 * @returns {boolean} Is valid mobile
 */
function isValidMobile(mobile) {
    // Allow different formats, but ensure it has at least 10 digits
    const digitsOnly = mobile.replace(/\D/g, '');
    return digitsOnly.length >= 10;
}
