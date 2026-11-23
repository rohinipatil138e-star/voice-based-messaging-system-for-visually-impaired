from functools import wraps
from flask import request, jsonify, current_app
from flask_login import current_user
from models import User, UserSession
import jwt

def token_required(f):
    """Decorator to require token authentication for API endpoints"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({
                    'error': {
                        'code': 'INVALID_TOKEN_FORMAT',
                        'message': 'Invalid token format',
                        'suggestions': ['Use Bearer <token> format']
                    }
                }), 401
        
        if not token:
            return jsonify({
                'error': {
                    'code': 'TOKEN_MISSING',
                    'message': 'Token is missing',
                    'suggestions': ['Provide Authorization header with Bearer token']
                }
            }), 401
        
        try:
            # Check if it's a session token
            user_session = UserSession.query.filter_by(session_token=token).first()
            
            if user_session and user_session.is_valid():
                # Get the user associated with this session
                user = User.query.get(user_session.user_id)
                if user and user.is_active:
                    # Set current_user for the request
                    from flask_login import login_user
                    login_user(user)
                    return f(*args, **kwargs)
            
            return jsonify({
                'error': {
                    'code': 'INVALID_TOKEN',
                    'message': 'Token is invalid or expired',
                    'suggestions': ['Please log in again to get a new token']
                }
            }), 401
            
        except Exception as e:
            current_app.logger.error(f"Token validation error: {e}")
            return jsonify({
                'error': {
                    'code': 'TOKEN_VALIDATION_ERROR',
                    'message': 'Error validating token',
                    'suggestions': ['Please log in again']
                }
            }), 401
    
    return decorated

def login_or_token_required(f):
    """Decorator that accepts either session-based or token-based authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check if user is already logged in via session
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        
        # If not logged in via session, try token authentication
        return token_required(f)(*args, **kwargs)
    
    return decorated