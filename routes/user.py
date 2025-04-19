import logging
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import User, Plan, Investment, Transaction, Deposit, Withdrawal, Referral, SystemSetting
from utils.helpers import generate_qr_code, calculate_referral_bonus, format_currency
from utils.decorators import admin_required

# Create blueprint
user_bp = Blueprint('user', __name__)
logger = logging.getLogger(__name__)

@user_bp.route('/')
def index():
    """Main landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))
    return render_template('home.html', user=None)

@user_bp.route('/home')
@login_required
def home():
    """User dashboard home page"""
    # Get user's active investments
    active_investments = Investment.query.filter_by(user_id=current_user.id, is_active=True).all()
    
    # Get user's recent transactions
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.created_at.desc()).limit(5).all()
    
    # Check if user can claim daily reward
    can_claim_reward = current_user.can_claim_daily_reward()
    
    return render_template('home.html', 
                          user=current_user, 
                          active_investments=active_investments,
                          recent_transactions=recent_transactions,
                          can_claim_reward=can_claim_reward)

@user_bp.route('/buy')
@login_required
def buy():
    """Investment plans page"""
    plans = Plan.query.filter_by(is_active=True).all()
    return render_template('buy.html', user=current_user, plans=plans)

@user_bp.route('/buy/<int:plan_id>', methods=['GET', 'POST'])
@login_required
def buy_plan(plan_id):
    """Purchase specific investment plan"""
    plan = Plan.query.get_or_404(plan_id)
    
    if request.method == 'POST':
        # Validate user has enough balance
        if current_user.wallet_balance < plan.price:
            flash('Insufficient balance. Please deposit funds to your wallet.', 'danger')
            return redirect(url_for('user.deposit'))
        
        try:
            # Calculate end date based on plan duration
            start_date = datetime.utcnow()
            end_date = start_date + datetime.timedelta(days=plan.duration_days)
            
            # Create investment
            investment = Investment(
                user_id=current_user.id,
                plan_id=plan.id,
                amount=plan.price,
                start_date=start_date,
                end_date=end_date,
                is_active=True
            )
            
            # Deduct amount from user's wallet
            current_user.wallet_balance -= plan.price
            
            # Record transaction
            transaction = Transaction(
                user_id=current_user.id,
                amount=plan.price,
                transaction_type='investment',
                description=f'Investment in {plan.name} plan'
            )
            
            # Check for referral bonus
            referral = Referral.query.filter_by(referred_id=current_user.id).first()
            if referral:
                # Calculate and add referral bonus to referrer
                referrer = User.query.get(referral.referrer_id)
                bonus_amount = calculate_referral_bonus(plan.price)
                
                referrer.wallet_balance += bonus_amount
                
                # Record referral bonus transaction
                referral_transaction = Transaction(
                    user_id=referrer.id,
                    amount=bonus_amount,
                    transaction_type='referral',
                    description=f'Referral bonus from {current_user.username}'
                )
                
                # Update referral bonus amount
                referral.bonus_amount += bonus_amount
                
                db.session.add(referrer)
                db.session.add(referral)
                db.session.add(referral_transaction)
            
            db.session.add(investment)
            db.session.add(current_user)
            db.session.add(transaction)
            db.session.commit()
            
            flash(f'Successfully invested in {plan.name} plan!', 'success')
            return redirect(url_for('user.home'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error purchasing plan: {e}")
            flash('An error occurred while processing your investment. Please try again.', 'danger')
    
    return render_template('buy_plan.html', user=current_user, plan=plan)

@user_bp.route('/team')
@login_required
def team():
    """User's referral team page"""
    # Get all users referred by current user
    team_members = current_user.get_team_members()
    
    # Get referral earnings
    total_referral_earnings = Referral.query.filter_by(referrer_id=current_user.id).with_entities(
        db.func.sum(Referral.bonus_amount)).scalar() or 0
    
    return render_template('team.html', 
                          user=current_user, 
                          team_members=team_members,
                          total_referral_earnings=total_referral_earnings,
                          referral_code=current_user.referral_code)

@user_bp.route('/menu')
@login_required
def menu():
    """User menu page"""
    return render_template('menu.html', user=current_user)

@user_bp.route('/wallet')
@login_required
def wallet():
    """User wallet page"""
    # Get all transactions
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.created_at.desc()).all()
    
    # Get pending deposits and withdrawals
    pending_deposits = Deposit.query.filter_by(user_id=current_user.id, status='pending').all()
    pending_withdrawals = Withdrawal.query.filter_by(user_id=current_user.id, status='pending').all()
    
    return render_template('wallet.html', 
                          user=current_user, 
                          transactions=transactions,
                          pending_deposits=pending_deposits,
                          pending_withdrawals=pending_withdrawals)

@user_bp.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    """Deposit funds page"""
    if request.method == 'POST':
        amount = float(request.form.get('amount', 0))
        payment_method = request.form.get('payment_method')
        
        if amount <= 0:
            flash('Please enter a valid amount to deposit.', 'danger')
            return redirect(url_for('user.deposit'))
        
        try:
            # Create deposit request
            deposit = Deposit(
                user_id=current_user.id,
                amount=amount,
                payment_method=payment_method,
                status='pending'
            )
            
            db.session.add(deposit)
            db.session.commit()
            
            # Generate QR code for crypto deposits
            qr_data = None
            if payment_method in ['bitcoin', 'ethereum', 'usdt']:
                # In a real app, generate actual wallet addresses
                wallet_address = "DEMO_WALLET_ADDRESS_FOR_" + payment_method.upper()
                qr_data = generate_qr_code(wallet_address)
            
            flash('Deposit request created successfully. Please complete the payment.', 'success')
            return render_template('deposit_confirmation.html', 
                                  deposit=deposit, 
                                  qr_data=qr_data)
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating deposit: {e}")
            flash('An error occurred while processing your deposit. Please try again.', 'danger')
    
    return render_template('deposit.html', user=current_user)

@user_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    """Withdraw funds page"""
    if request.method == 'POST':
        amount = float(request.form.get('amount', 0))
        wallet_address = request.form.get('wallet_address')
        
        if amount <= 0:
            flash('Please enter a valid amount to withdraw.', 'danger')
            return redirect(url_for('user.withdraw'))
        
        if current_user.wallet_balance < amount:
            flash('Insufficient balance for this withdrawal.', 'danger')
            return redirect(url_for('user.withdraw'))
        
        if not wallet_address:
            flash('Please provide a valid wallet address.', 'danger')
            return redirect(url_for('user.withdraw'))
        
        try:
            # Create withdrawal request
            withdrawal = Withdrawal(
                user_id=current_user.id,
                amount=amount,
                wallet_address=wallet_address,
                status='pending'
            )
            
            # Deduct from user's available balance
            current_user.wallet_balance -= amount
            
            db.session.add(withdrawal)
            db.session.add(current_user)
            db.session.commit()
            
            flash('Withdrawal request submitted successfully. It will be processed soon.', 'success')
            return redirect(url_for('user.wallet'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating withdrawal: {e}")
            flash('An error occurred while processing your withdrawal. Please try again.', 'danger')
    
    return render_template('withdraw.html', user=current_user)

@user_bp.route('/claim-reward', methods=['POST'])
@login_required
def claim_reward():
    """Claim daily reward"""
    if not current_user.can_claim_daily_reward():
        flash('You have already claimed your daily reward today.', 'warning')
        return redirect(url_for('user.home'))
    
    try:
        # Set daily reward amount
        reward_amount = 0.5  # $0.50 as an example
        
        # Update user's balance
        current_user.wallet_balance += reward_amount
        
        # Update last reward claim time
        current_user.last_reward_claim = datetime.utcnow()
        
        # Record transaction
        transaction = Transaction(
            user_id=current_user.id,
            amount=reward_amount,
            transaction_type='reward',
            description='Daily reward claim'
        )
        
        db.session.add(current_user)
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Successfully claimed ${reward_amount:.2f} daily reward!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error claiming reward: {e}")
        flash('An error occurred while claiming your reward. Please try again.', 'danger')
    
    return redirect(url_for('user.home'))
