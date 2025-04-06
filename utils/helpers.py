import random
import string
import qrcode
import io
import base64
from datetime import datetime, timedelta
from models import User, Investment, Transaction
from app import db

def generate_referral_code(length=6):
    """Generate a unique referral code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not User.query.filter_by(referral_code=code).first():
            return code

def generate_qr_code(data):
    """Generate a QR code for the given data and return as base64 image"""
    img = qrcode.make(data)
    buffer = io.BytesIO()
    img.save(buffer)
    buffer.seek(0)
    
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_str}"

def process_investment_returns():
    """Process all active investments and pay out returns"""
    active_investments = Investment.query.filter_by(is_active=True).all()
    now = datetime.utcnow()
    
    for investment in active_investments:
        # Check if investment period has ended
        if now > investment.end_date:
            investment.is_active = False
            db.session.add(investment)
            continue
            
        # Check if last payout was more than a day ago or if it's the first payout
        if not investment.last_payout or (now - investment.last_payout).days >= 1:
            user = User.query.get(investment.user_id)
            plan = investment.plan
            
            # Calculate daily return
            daily_return = investment.amount * (plan.daily_return_percentage / 100)
            
            # Add to user's balance
            user.wallet_balance += daily_return
            
            # Record transaction
            transaction = Transaction(
                user_id=user.id,
                amount=daily_return,
                transaction_type='investment_return',
                description=f'Daily return from {plan.name} investment'
            )
            
            # Update last payout time
            investment.last_payout = now
            
            db.session.add(user)
            db.session.add(transaction)
            db.session.add(investment)
    
    db.session.commit()

def calculate_referral_bonus(investment_amount):
    """Calculate referral bonus based on investment amount"""
    return investment_amount * 0.05  # 5% referral bonus

def format_currency(amount):
    """Format currency with 2 decimal places"""
    return f"${amount:.2f}"

def convert_datetime_to_string(dt):
    """Convert datetime object to formatted string"""
    if not dt:
        return "N/A"
    return dt.strftime('%Y-%m-%d %H:%M:%S')
