from datetime import datetime
from enum import Enum
from extensions import db

class MessageType(Enum):
    """Enum for message types"""
    DRAFT = 'draft'
    SENT = 'sent'
    RECEIVED = 'received'

class Message(db.Model):
    """Message model for storing voice messages and email content"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text)
    audio_file_path = db.Column(db.String(255))
    recipient_email = db.Column(db.String(120))
    subject = db.Column(db.String(200))
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    message_type = db.Column(db.Enum(MessageType), default=MessageType.DRAFT)
    is_read = db.Column(db.Boolean, default=False)
    
    # Relationships
    audio_files = db.relationship('AudioFile', backref='message', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, user_id, content=None, recipient_email=None, subject=None):
        self.user_id = user_id
        self.content = content
        self.recipient_email = recipient_email
        self.subject = subject
        self.message_type = MessageType.DRAFT  # Ensure default is set
    
    def mark_as_sent(self):
        """Mark message as sent"""
        self.message_type = MessageType.SENT
        self.sent_at = datetime.utcnow()
        db.session.commit()
    
    def mark_as_read(self):
        """Mark message as read"""
        self.is_read = True
        db.session.commit()
    
    def is_draft(self):
        """Check if message is a draft"""
        return self.message_type == MessageType.DRAFT
    
    def is_sent(self):
        """Check if message is sent"""
        return self.message_type == MessageType.SENT
    
    def is_received(self):
        """Check if message is received"""
        return self.message_type == MessageType.RECEIVED
    
    def has_audio(self):
        """Check if message has audio file"""
        return self.audio_file_path is not None
    
    def get_audio_duration(self):
        """Get total duration of audio files"""
        total_duration = 0
        for audio_file in self.audio_files:
            if audio_file.duration:
                total_duration += audio_file.duration
        return total_duration
    
    def to_dict(self):
        """Convert message to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'audio_file_path': self.audio_file_path,
            'recipient_email': self.recipient_email,
            'subject': self.subject,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'message_type': self.message_type.value if self.message_type else 'draft',
            'is_read': self.is_read,
            'has_audio': self.has_audio(),
            'audio_duration': self.get_audio_duration()
        }
    
    def __repr__(self):
        return f'<Message {self.id} - {self.message_type.value if self.message_type else "unknown"}>'