/**
 * Investment plans related JavaScript for Investment Portal
 */

document.addEventListener('DOMContentLoaded', function() {
    // Plan selection
    const planCards = document.querySelectorAll('.plan-card');
    const buyButton = document.getElementById('buy-plan-button');
    
    planCards.forEach(card => {
        card.addEventListener('click', function() {
            // Remove 'selected' class from all cards
            planCards.forEach(c => c.classList.remove('border-primary', 'selected-plan'));
            
            // Add 'selected' class to clicked card
            this.classList.add('border-primary', 'selected-plan');
            
            // Enable buy button
            if (buyButton) {
                buyButton.removeAttribute('disabled');
                
                // Update button text with plan name and price
                const planName = this.querySelector('.plan-name').textContent;
                const planPrice = this.querySelector('.plan-price').textContent;
                buyButton.textContent = `Buy ${planName} for ${planPrice}`;
            }
            
            // Update hidden form field if it exists
            const selectedPlanInput = document.getElementById('selected_plan_id');
            if (selectedPlanInput) {
                selectedPlanInput.value = this.getAttribute('data-plan-id');
            }
        });
    });
    
    // Plan purchase form
    const purchaseForm = document.getElementById('purchase-plan-form');
    if (purchaseForm) {
        purchaseForm.addEventListener('submit', function(event) {
            // Get selected plan
            const selectedPlan = document.querySelector('.plan-card.selected-plan');
            
            if (!selectedPlan) {
                event.preventDefault();
                alert('Please select an investment plan before proceeding.');
                return;
            }
            
            // Get plan price and user balance
            const planPrice = parseFloat(selectedPlan.getAttribute('data-price'));
            const userBalance = parseFloat(document.getElementById('user-balance').getAttribute('data-balance'));
            
            // Check if user has enough balance
            if (userBalance < planPrice) {
                event.preventDefault();
                alert('You do not have enough balance to purchase this plan. Please deposit funds first.');
                
                // Redirect to deposit page if confirmed
                if (confirm('Would you like to go to the deposit page?')) {
                    window.location.href = '/deposit';
                }
            } else {
                // Confirm purchase
                if (!confirm(`Are you sure you want to invest in this plan? $${planPrice.toFixed(2)} will be deducted from your wallet.`)) {
                    event.preventDefault();
                }
            }
        });
    }
    
    // Calculate investment returns
    const investmentAmount = document.getElementById('investment-amount');
    const dailyReturnRate = document.getElementById('daily-return-rate');
    const durationDays = document.getElementById('duration-days');
    const dailyReturnDisplay = document.getElementById('daily-return');
    const totalReturnDisplay = document.getElementById('total-return');
    const netProfitDisplay = document.getElementById('net-profit');
    
    function calculateReturns() {
        if (investmentAmount && dailyReturnRate && durationDays &&
            dailyReturnDisplay && totalReturnDisplay && netProfitDisplay) {
            
            const amount = parseFloat(investmentAmount.value) || 0;
            const rate = parseFloat(dailyReturnRate.value) || 0;
            const days = parseInt(durationDays.value) || 0;
            
            const dailyReturn = amount * (rate / 100);
            const totalReturn = dailyReturn * days;
            const netProfit = totalReturn - amount;
            
            dailyReturnDisplay.textContent = formatCurrency(dailyReturn);
            totalReturnDisplay.textContent = formatCurrency(totalReturn);
            netProfitDisplay.textContent = formatCurrency(netProfit);
        }
    }
    
    // Add listeners to calculator inputs
    if (investmentAmount && dailyReturnRate && durationDays) {
        [investmentAmount, dailyReturnRate, durationDays].forEach(input => {
            input.addEventListener('input', calculateReturns);
        });
        
        // Initialize calculator
        calculateReturns();
    }
});

/**
 * Format currency with 2 decimal places
 * @param {number} amount - Amount to format
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2);
}
