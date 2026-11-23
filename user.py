from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(UserMixin, db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    preferences = db.Column(db.JSON, default=lambda: {
        'voice_speed': 1.0,
        'voice_volume': 1.0,
        'auto_play_messages': True,
        'voice_commands_enabled': True
    })
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    messages = db.relationship('Message', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    sessions = db.relationship('UserSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
        # Ensure preferences are set with defaults
        if self.preferences is None:
            self.preferences = {
                'voice_speed': 1.0,
                'voice_volume': 1.0,
                'auto_play_messages': True,
                'voice_commands_enabled': True
            }
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def get_preference(self, key, default=None):
        """Get user preference value"""
        if self.preferences is None:
            return default
        return self.preferences.get(key, default)
    
    def set_preference(self, key, value):
        """Set user preference value"""
        if self.preferences is None:
            self.preferences = {}
        self.preferences[key] = value
        db.session.commit()
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'preferences': self.preferences,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<User {self.username}>'