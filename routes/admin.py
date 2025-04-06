import logging
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import User, Plan, Investment, Transaction, Deposit, Withdrawal
from utils.decorators import admin_required

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
logger = logging.getLogger(__name__)

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get count statistics
    user_count = User.query.count()
    deposit_count = Deposit.query.count()
    withdrawal_count = Withdrawal.query.count()
    investment_count = Investment.query.count()
    
    # Get sum statistics
    total_deposits = db.session.query(db.func.sum(Deposit.amount).label('total')).filter_by(status='approved').scalar() or 0
    total_withdrawals = db.session.query(db.func.sum(Withdrawal.amount).label('total')).filter_by(status='approved').scalar() or 0
    total_investments = db.session.query(db.func.sum(Investment.amount).label('total')).scalar() or 0
    
    # Get pending counts
    pending_deposits = Deposit.query.filter_by(status='pending').count()
    pending_withdrawals = Withdrawal.query.filter_by(status='pending').count()
    
    return render_template('admin/dashboard.html', 
                          user=current_user,
                          user_count=user_count,
                          deposit_count=deposit_count,
                          withdrawal_count=withdrawal_count,
                          investment_count=investment_count,
                          total_deposits=total_deposits,
                          total_withdrawals=total_withdrawals,
                          total_investments=total_investments,
                          pending_deposits=pending_deposits,
                          pending_withdrawals=pending_withdrawals)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Manage users"""
    users_list = User.query.all()
    return render_template('admin/users.html', user=current_user, users=users_list)

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def view_user(user_id):
    """View user details"""
    user_to_view = User.query.get_or_404(user_id)
    return render_template('admin/view_user.html', user=current_user, user_to_view=user_to_view)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user"""
    user_to_edit = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        wallet_balance = float(request.form.get('wallet_balance', 0))
        is_admin = 'is_admin' in request.form
        
        try:
            user_to_edit.username = username
            user_to_edit.email = email
            user_to_edit.mobile = mobile
            user_to_edit.wallet_balance = wallet_balance
            user_to_edit.is_admin = is_admin
            
            db.session.add(user_to_edit)
            db.session.commit()
            
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin.users'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating user: {e}")
            flash('An error occurred while updating the user.', 'danger')
    
    return render_template('admin/edit_user.html', user=current_user, user_to_edit=user_to_edit)

@admin_bp.route('/deposits')
@login_required
@admin_required
def deposits():
    """Manage deposits"""
    # Get filter parameters
    status = request.args.get('status', 'all')
    
    # Apply filters
    if status != 'all':
        deposits_list = Deposit.query.filter_by(status=status).order_by(Deposit.created_at.desc()).all()
    else:
        deposits_list = Deposit.query.order_by(Deposit.created_at.desc()).all()
    
    return render_template('admin/deposits.html', user=current_user, deposits=deposits_list, current_filter=status)

@admin_bp.route('/deposits/<int:deposit_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_deposit(deposit_id):
    """Approve deposit"""
    deposit = Deposit.query.get_or_404(deposit_id)
    
    if deposit.status != 'pending':
        flash('This deposit has already been processed.', 'warning')
        return redirect(url_for('admin.deposits'))
    
    try:
        # Update deposit status
        deposit.status = 'approved'
        
        # Update user's balance
        user = User.query.get(deposit.user_id)
        user.wallet_balance += deposit.amount
        
        # Create transaction record
        transaction = Transaction(
            user_id=user.id,
            amount=deposit.amount,
            transaction_type='deposit',
            description='Deposit approved'
        )
        
        db.session.add(deposit)
        db.session.add(user)
        db.session.add(transaction)
        db.session.commit()
        
        flash('Deposit approved successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error approving deposit: {e}")
        flash('An error occurred while approving the deposit.', 'danger')
    
    return redirect(url_for('admin.deposits'))

@admin_bp.route('/deposits/<int:deposit_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_deposit(deposit_id):
    """Reject deposit"""
    deposit = Deposit.query.get_or_404(deposit_id)
    
    if deposit.status != 'pending':
        flash('This deposit has already been processed.', 'warning')
        return redirect(url_for('admin.deposits'))
    
    try:
        # Update deposit status
        deposit.status = 'rejected'
        
        db.session.add(deposit)
        db.session.commit()
        
        flash('Deposit rejected successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error rejecting deposit: {e}")
        flash('An error occurred while rejecting the deposit.', 'danger')
    
    return redirect(url_for('admin.deposits'))

@admin_bp.route('/withdrawals')
@login_required
@admin_required
def withdrawals():
    """Manage withdrawals"""
    # Get filter parameters
    status = request.args.get('status', 'all')
    
    # Apply filters
    if status != 'all':
        withdrawals_list = Withdrawal.query.filter_by(status=status).order_by(Withdrawal.created_at.desc()).all()
    else:
        withdrawals_list = Withdrawal.query.order_by(Withdrawal.created_at.desc()).all()
    
    return render_template('admin/withdrawals.html', user=current_user, withdrawals=withdrawals_list, current_filter=status)

@admin_bp.route('/withdrawals/<int:withdrawal_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_withdrawal(withdrawal_id):
    """Approve withdrawal"""
    withdrawal = Withdrawal.query.get_or_404(withdrawal_id)
    
    if withdrawal.status != 'pending':
        flash('This withdrawal has already been processed.', 'warning')
        return redirect(url_for('admin.withdrawals'))
    
    try:
        # Update withdrawal status
        withdrawal.status = 'approved'
        withdrawal.processed_at = datetime.utcnow()
        
        # Create transaction record
        transaction = Transaction(
            user_id=withdrawal.user_id,
            amount=withdrawal.amount,
            transaction_type='withdrawal',
            description='Withdrawal approved'
        )
        
        db.session.add(withdrawal)
        db.session.add(transaction)
        db.session.commit()
        
        flash('Withdrawal approved successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error approving withdrawal: {e}")
        flash('An error occurred while approving the withdrawal.', 'danger')
    
    return redirect(url_for('admin.withdrawals'))

@admin_bp.route('/withdrawals/<int:withdrawal_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_withdrawal(withdrawal_id):
    """Reject withdrawal"""
    withdrawal = Withdrawal.query.get_or_404(withdrawal_id)
    
    if withdrawal.status != 'pending':
        flash('This withdrawal has already been processed.', 'warning')
        return redirect(url_for('admin.withdrawals'))
    
    try:
        # Update withdrawal status
        withdrawal.status = 'rejected'
        withdrawal.processed_at = datetime.utcnow()
        
        # Refund the amount to user's balance
        user = User.query.get(withdrawal.user_id)
        user.wallet_balance += withdrawal.amount
        
        # Create transaction record
        transaction = Transaction(
            user_id=user.id,
            amount=withdrawal.amount,
            transaction_type='refund',
            description='Withdrawal rejected - funds returned to wallet'
        )
        
        db.session.add(withdrawal)
        db.session.add(user)
        db.session.add(transaction)
        db.session.commit()
        
        flash('Withdrawal rejected and funds returned to user wallet.', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error rejecting withdrawal: {e}")
        flash('An error occurred while rejecting the withdrawal.', 'danger')
    
    return redirect(url_for('admin.withdrawals'))

@admin_bp.route('/plans')
@login_required
@admin_required
def plans():
    """Manage investment plans"""
    plans_list = Plan.query.all()
    return render_template('admin/plans.html', user=current_user, plans=plans_list)

@admin_bp.route('/plans/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_plan():
    """Create investment plan"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price', 0))
        daily_return_percentage = float(request.form.get('daily_return_percentage', 0))
        duration_days = int(request.form.get('duration_days', 0))
        is_active = 'is_active' in request.form
        
        if not name or price <= 0 or daily_return_percentage <= 0 or duration_days <= 0:
            flash('Please provide all required fields with valid values.', 'danger')
            return render_template('admin/create_plan.html', user=current_user)
        
        try:
            plan = Plan(
                name=name,
                description=description,
                price=price,
                daily_return_percentage=daily_return_percentage,
                duration_days=duration_days,
                is_active=is_active
            )
            
            db.session.add(plan)
            db.session.commit()
            
            flash('Investment plan created successfully!', 'success')
            return redirect(url_for('admin.plans'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating plan: {e}")
            flash('An error occurred while creating the investment plan.', 'danger')
    
    return render_template('admin/create_plan.html', user=current_user)

@admin_bp.route('/plans/<int:plan_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_plan(plan_id):
    """Edit investment plan"""
    plan = Plan.query.get_or_404(plan_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price', 0))
        daily_return_percentage = float(request.form.get('daily_return_percentage', 0))
        duration_days = int(request.form.get('duration_days', 0))
        is_active = 'is_active' in request.form
        
        if not name or price <= 0 or daily_return_percentage <= 0 or duration_days <= 0:
            flash('Please provide all required fields with valid values.', 'danger')
            return render_template('admin/edit_plan.html', user=current_user, plan=plan)
        
        try:
            plan.name = name
            plan.description = description
            plan.price = price
            plan.daily_return_percentage = daily_return_percentage
            plan.duration_days = duration_days
            plan.is_active = is_active
            
            db.session.add(plan)
            db.session.commit()
            
            flash('Investment plan updated successfully!', 'success')
            return redirect(url_for('admin.plans'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating plan: {e}")
            flash('An error occurred while updating the investment plan.', 'danger')
    
    return render_template('admin/edit_plan.html', user=current_user, plan=plan)

@admin_bp.route('/plans/<int:plan_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_plan(plan_id):
    """Delete investment plan"""
    plan = Plan.query.get_or_404(plan_id)
    
    # Check if plan has active investments
    active_investments = Investment.query.filter_by(plan_id=plan.id, is_active=True).count()
    if active_investments > 0:
        flash('Cannot delete plan with active investments.', 'danger')
        return redirect(url_for('admin.plans'))
    
    try:
        db.session.delete(plan)
        db.session.commit()
        flash('Investment plan deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting plan: {e}")
        flash('An error occurred while deleting the investment plan.', 'danger')
    
    return redirect(url_for('admin.plans'))
