/**
 * Team and referrals related JavaScript for Investment Portal
 */

document.addEventListener('DOMContentLoaded', function() {
    // Copy referral link functionality
    const copyReferralLinkBtn = document.getElementById('copy-referral-link');
    if (copyReferralLinkBtn) {
        copyReferralLinkBtn.addEventListener('click', function() {
            const referralLink = document.getElementById('referral-link');
            
            // Create a temporary input element
            const tempInput = document.createElement('input');
            tempInput.value = referralLink.value;
            document.body.appendChild(tempInput);
            
            // Select and copy the link
            tempInput.select();
            document.execCommand('copy');
            
            // Remove the temporary element
            document.body.removeChild(tempInput);
            
            // Show success message
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-check"></i> Copied!';
            
            // Reset button text after 2 seconds
            setTimeout(() => {
                this.innerHTML = originalText;
            }, 2000);
        });
    }
    
    // Copy referral code functionality
    const copyReferralCodeBtn = document.getElementById('copy-referral-code');
    if (copyReferralCodeBtn) {
        copyReferralCodeBtn.addEventListener('click', function() {
            const referralCode = document.getElementById('referral-code').textContent;
            
            // Copy to clipboard
            navigator.clipboard.writeText(referralCode).then(() => {
                // Show success message
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                
                // Reset button text after 2 seconds
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 2000);
            }).catch(err => {
                console.error('Could not copy text: ', err);
            });
        });
    }
    
    // Team filter functionality
    const teamFilter = document.getElementById('team-filter');
    if (teamFilter) {
        teamFilter.addEventListener('change', function() {
            const filterValue = this.value;
            const teamMembers = document.querySelectorAll('.team-member');
            
            teamMembers.forEach(member => {
                if (filterValue === 'all') {
                    member.style.display = '';
                } else {
                    const memberStatus = member.getAttribute('data-status');
                    member.style.display = (memberStatus === filterValue) ? '' : 'none';
                }
            });
        });
    }
    
    // Share referral link via social media
    const shareButtons = document.querySelectorAll('.share-referral');
    if (shareButtons.length > 0) {
        const referralLink = document.getElementById('referral-link').value;
        const referralMessage = encodeURIComponent(`Join my investment team and earn daily returns! Use my referral code: ${document.getElementById('referral-code').textContent}`);
        
        shareButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                const platform = this.getAttribute('data-platform');
                let shareUrl = '';
                
                switch (platform) {
                    case 'facebook':
                        shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(referralLink)}&quote=${referralMessage}`;
                        break;
                    case 'twitter':
                        shareUrl = `https://twitter.com/intent/tweet?text=${referralMessage}&url=${encodeURIComponent(referralLink)}`;
                        break;
                    case 'whatsapp':
                        shareUrl = `https://wa.me/?text=${referralMessage}%20${encodeURIComponent(referralLink)}`;
                        break;
                    case 'telegram':
                        shareUrl = `https://t.me/share/url?url=${encodeURIComponent(referralLink)}&text=${referralMessage}`;
                        break;
                }
                
                if (shareUrl) {
                    window.open(shareUrl, '_blank', 'width=600,height=400');
                }
            });
        });
    }
    
    // Team statistics
    const teamStatsElement = document.getElementById('team-stats');
    if (teamStatsElement) {
        // In a real app, this would come from the server via AJAX
        const teamMembersCount = document.querySelectorAll('.team-member').length;
        const activeMembers = document.querySelectorAll('.team-member[data-status="active"]').length;
        const inactiveMembers = teamMembersCount - activeMembers;
        
        const statsHTML = `
            <div class="row text-center mt-4">
                <div class="col-4">
                    <div class="border rounded p-2">
                        <h4>${teamMembersCount}</h4>
                        <small>Total</small>
                    </div>
                </div>
                <div class="col-4">
                    <div class="border rounded p-2">
                        <h4>${activeMembers}</h4>
                        <small>Active</small>
                    </div>
                </div>
                <div class="col-4">
                    <div class="border rounded p-2">
                        <h4>${inactiveMembers}</h4>
                        <small>Inactive</small>
                    </div>
                </div>
            </div>
        `;
        
        teamStatsElement.innerHTML = statsHTML;
    }
});

/**
 * Calculate team level for display
 * @param {number} referralCount - Number of referrals
 * @returns {string} Team level label
 */
function calculateTeamLevel(referralCount) {
    if (referralCount >= 50) {
        return 'Diamond';
    } else if (referralCount >= 25) {
        return 'Platinum';
    } else if (referralCount >= 10) {
        return 'Gold';
    } else if (referralCount >= 5) {
        return 'Silver';
    } else {
        return 'Bronze';
    }
}
