from datetime import datetime, timedelta
from extensions import db
import secrets

class UserSession(db.Model):
    """UserSession model for managing user sessions"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    def __init__(self, user_id, expires_in_hours=24):
        self.user_id = user_id
        self.session_token = self.generate_token()
        self.expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        self.is_active = True  # Ensure default is set
    
    @staticmethod
    def generate_token():
        """Generate a secure random session token"""
        return secrets.token_urlsafe(32)
    
    def is_expired(self):
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Check if session is valid (active and not expired)"""
        return self.is_active and not self.is_expired()
    
    def extend_session(self, hours=24):
        """Extend session expiration time"""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        db.session.commit()
    
    def deactivate(self):
        """Deactivate the session"""
        self.is_active = False
        db.session.commit()
    
    def refresh_token(self):
        """Generate new session token"""
        self.session_token = self.generate_token()
        db.session.commit()
    
    @classmethod
    def cleanup_expired_sessions(cls):
        """Remove expired sessions from database"""
        expired_sessions = cls.query.filter(cls.expires_at < datetime.utcnow()).all()
        for session in expired_sessions:
            db.session.delete(session)
        db.session.commit()
        return len(expired_sessions)
    
    @classmethod
    def get_active_session(cls, token):
        """Get active session by token"""
        session = cls.query.filter_by(session_token=token, is_active=True).first()
        if session and session.is_valid():
            return session
        return None
    
    def to_dict(self):
        """Convert session to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_token': self.session_token,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'is_expired': self.is_expired(),
            'is_valid': self.is_valid()
        }
    
    def __repr__(self):
        return f'<UserSession {self.id} - User {self.user_id}>'