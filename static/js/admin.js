/**
 * Admin panel JavaScript for Investment Portal
 */

document.addEventListener('DOMContentLoaded', function() {
    // Data tables initialization
    const tables = document.querySelectorAll('.data-table');
    tables.forEach(table => {
        $(table).DataTable({
            responsive: true,
            order: [[0, 'desc']]
        });
    });
    
    // Confirm actions (delete, approve, reject)
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });
    
    // Status filter for deposits/withdrawals
    const statusFilter = document.getElementById('status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            window.location.href = window.location.pathname + '?status=' + this.value;
        });
    }
    
    // Toggle user admin status
    const adminToggleCheckboxes = document.querySelectorAll('.admin-toggle');
    adminToggleCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const userId = this.getAttribute('data-user-id');
            const isAdmin = this.checked;
            
            if (confirm(`Are you sure you want to ${isAdmin ? 'make' : 'remove'} this user ${isAdmin ? 'an' : 'from being an'} administrator?`)) {
                // Submit form or make AJAX request
                document.getElementById('toggle-admin-form-' + userId).submit();
            } else {
                // Revert checkbox state
                this.checked = !isAdmin;
            }
        });
    });
    
    // User search
    const userSearchInput = document.getElementById('user-search');
    if (userSearchInput) {
        userSearchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const userRows = document.querySelectorAll('.user-row');
            
            userRows.forEach(row => {
                const username = row.querySelector('.user-username').textContent.toLowerCase();
                const email = row.querySelector('.user-email').textContent.toLowerCase();
                const mobile = row.querySelector('.user-mobile').textContent.toLowerCase();
                
                if (username.includes(searchTerm) || email.includes(searchTerm) || mobile.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
    
    // Plan form validation
    const planForm = document.getElementById('plan-form');
    if (planForm) {
        planForm.addEventListener('submit', function(event) {
            const name = document.getElementById('plan-name').value;
            const price = parseFloat(document.getElementById('plan-price').value);
            const dailyReturn = parseFloat(document.getElementById('daily-return-percentage').value);
            const duration = parseInt(document.getElementById('duration-days').value);
            
            let isValid = true;
            let errorMessage = '';
            
            if (!name) {
                errorMessage += 'Plan name is required.\n';
                isValid = false;
            }
            
            if (isNaN(price) || price <= 0) {
                errorMessage += 'Plan price must be a positive number.\n';
                isValid = false;
            }
            
            if (isNaN(dailyReturn) || dailyReturn <= 0) {
                errorMessage += 'Daily return percentage must be a positive number.\n';
                isValid = false;
            }
            
            if (isNaN(duration) || duration <= 0) {
                errorMessage += 'Duration days must be a positive integer.\n';
                isValid = false;
            }
            
            if (!isValid) {
                event.preventDefault();
                alert('Please fix the following errors:\n\n' + errorMessage);
            }
        });
    }
    
    // Dashboard stats charts
    const investmentsChart = document.getElementById('investments-chart');
    if (investmentsChart) {
        // Sample data - in a real app, this would come from the server
        const ctx = investmentsChart.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Investments',
                    data: [12, 19, 3, 5, 2, 3],
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
});

/**
 * Format date for admin display
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date string
 */
function formatAdminDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Approve deposit or withdrawal
 * @param {string} type - 'deposit' or 'withdrawal'
 * @param {number} id - Item ID
 * @param {string} token - CSRF token
 */
function approveItem(type, id, token) {
    if (confirm(`Are you sure you want to approve this ${type}?`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/${type}s/${id}/approve`;
        
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrf_token';
        csrfInput.value = token;
        
        form.appendChild(csrfInput);
        document.body.appendChild(form);
        form.submit();
    }
}

/**
 * Reject deposit or withdrawal
 * @param {string} type - 'deposit' or 'withdrawal'
 * @param {number} id - Item ID
 * @param {string} token - CSRF token
 */
function rejectItem(type, id, token) {
    if (confirm(`Are you sure you want to reject this ${type}?`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/${type}s/${id}/reject`;
        
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrf_token';
        csrfInput.value = token;
        
        form.appendChild(csrfInput);
        document.body.appendChild(form);
        form.submit();
    }
}
