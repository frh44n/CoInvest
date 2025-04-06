import os
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    """
    Create and return a Supabase client.
    
    Returns:
        Client: Supabase client instance
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        logger.warning("Supabase credentials not found, some functionality may be limited")
        return None
    
    try:
        return create_client(url, key)
    except Exception as e:
        logger.error(f"Error creating Supabase client: {e}")
        return None

supabase = get_supabase_client()

def sync_user_to_supabase(user):
    """
    Sync a user to Supabase Auth.
    
    Args:
        user: User model instance to sync
    
    Returns:
        bool: Success status
    """
    if not supabase:
        return False
    
    try:
        # Check if user exists in Supabase
        response = supabase.auth.admin.get_user_by_email(user.email)
        
        # If user doesn't exist, create them
        if not response:
            result = supabase.auth.admin.create_user({
                'email': user.email,
                'password': user.password_hash,
                'user_metadata': {
                    'username': user.username,
                    'mobile': user.mobile,
                    'referral_code': user.referral_code
                }
            })
            return result is not None
        
        return True
    except Exception as e:
        logger.error(f"Error syncing user to Supabase: {e}")
        return False
