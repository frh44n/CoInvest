import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models import User, Referral
from utils.helpers import generate_referral_code
from utils.supabase import sync_user_to_supabase

# Create blueprint
auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))
    
    if request.method == 'POST':
        # Get form data
        identifier = request.form.get('identifier')  # Email or mobile
        password = request.form.get('password')
        
        # Validate form data
        if not identifier or not password:
            flash('Please provide all required fields.', 'danger')
            return render_template('login.html')
        
        # Find user by email or mobile
        user = User.query.filter((User.email == identifier) | (User.mobile == identifier)).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            
            # Redirect to the next page or home
            next_page = request.args.get('next')
            return redirect(next_page or url_for('user.home'))
        else:
            flash('Invalid email/mobile or password. Please try again.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))
    
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        invitation_code = request.form.get('invitation_code')
        
        # Validate form data
        if not email or not mobile or not username or not password:
            flash('Please provide all required fields.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(mobile=mobile).first():
            flash('Mobile number already registered.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('register.html')
        
        # Generate referral code
        referral_code = generate_referral_code()
        
        # Create new user
        new_user = User(
            email=email,
            mobile=mobile,
            username=username,
            referral_code=referral_code,
            wallet_balance=0.0
        )
        new_user.set_password(password)
        
        # Check invitation code
        referrer = None
        if invitation_code:
            referrer = User.query.filter_by(referral_code=invitation_code).first()
            if not referrer:
                flash('Invalid invitation code.', 'warning')
            else:
                # Set referrer
                new_user.invited_by = referrer.id
        
        try:
            # Add user to database
            db.session.add(new_user)
            db.session.flush()  # Get ID without committing
            
            # Create referral record if applicable
            if referrer:
                referral = Referral(
                    referrer_id=referrer.id,
                    referred_id=new_user.id,
                    bonus_amount=0.0  # Will be updated when user makes an investment
                )
                db.session.add(referral)
            
            # Commit changes
            db.session.commit()
            
            # Sync user to Supabase if available
            sync_user_to_supabase(new_user)
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error registering user: {e}")
            flash('An error occurred during registration. Please try again.', 'danger')
    
    # For GET requests or form validation errors
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Password reset request route"""
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Please provide your email address.', 'danger')
            return render_template('reset_password.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Send password reset email (implementation required)
            flash('Password reset instructions sent to your email.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('Email not found in our records.', 'danger')
    
    return render_template('reset_password.html')
