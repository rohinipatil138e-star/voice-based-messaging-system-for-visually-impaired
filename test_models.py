import pytest
from datetime import datetime, timedelta
from models import User, Message, AudioFile, UserSession, MessageType
from extensions import db

class TestUser:
    """Test User model"""
    
    def test_user_creation(self, app):
        """Test user creation"""
        with app.app_context():
            user = User('testuser', 'test@example.com', 'password123')
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.check_password('password123')
            assert not user.check_password('wrongpassword')
    
    def test_password_hashing(self, app):
        """Test password hashing"""
        with app.app_context():
            user = User('testuser', 'test@example.com', 'password123')
            assert user.password_hash != 'password123'
            assert user.check_password('password123')
    
    def test_user_preferences(self, app):
        """Test user preferences"""
        with app.app_context():
            user = User('testuser', 'test@example.com', 'password123')
            assert user.get_preference('voice_speed') == 1.0
            user.set_preference('voice_speed', 1.5)
            assert user.get_preference('voice_speed') == 1.5
    
    def test_user_to_dict(self, app):
        """Test user serialization"""
        with app.app_context():
            user = User('testuser', 'test@example.com', 'password123')
            user_dict = user.to_dict()
            assert user_dict['username'] == 'testuser'
            assert user_dict['email'] == 'test@example.com'
            assert 'password_hash' not in user_dict

class TestMessage:
    """Test Message model"""
    
    def test_message_creation(self, app):
        """Test message creation"""
        with app.app_context():
            db.create_all()
            user = User('testuser', 'test@example.com', 'password123')
            db.session.add(user)
            db.session.commit()
            
            message = Message(user.id, 'Test message content', 'recipient@example.com', 'Test Subject')
            assert message.content == 'Test message content'
            assert message.recipient_email == 'recipient@example.com'
            assert message.subject == 'Test Subject'
            assert message.is_draft()
    
    def test_message_status_changes(self, app):
        """Test message status changes"""
        with app.app_context():
            db.create_all()
            user = User('testuser', 'test@example.com', 'password123')
            db.session.add(user)
            db.session.commit()
            
            message = Message(user.id, 'Test message')
            db.session.add(message)
            db.session.commit()
            
            assert message.is_draft()
            message.mark_as_sent()
            assert message.is_sent()
            assert message.sent_at is not None
    
    def test_message_to_dict(self, app):
        """Test message serialization"""
        with app.app_context():
            db.create_all()
            user = User('testuser', 'test@example.com', 'password123')
            db.session.add(user)
            db.session.commit()
            
            message = Message(user.id, 'Test message')
            message_dict = message.to_dict()
            assert message_dict['content'] == 'Test message'
            assert message_dict['message_type'] == 'draft'

class TestAudioFile:
    """Test AudioFile model"""
    
    def test_audio_file_creation(self, app):
        """Test audio file creation"""
        with app.app_context():
            db.create_all()
            user = User('testuser', 'test@example.com', 'password123')
            db.session.add(user)
            db.session.commit()
            
            message = Message(user.id, 'Test message')
            db.session.add(message)
            db.session.commit()
            
            audio_file = AudioFile(message.id, '/path/to/audio.wav', 1024, 30.5, 'wav')
            assert audio_file.file_path == '/path/to/audio.wav'
            assert audio_file.file_size == 1024
            assert audio_file.duration == 30.5
            assert audio_file.format == 'wav'
    
    def test_audio_file_methods(self, app):
        """Test audio file utility methods"""
        with app.app_context():
            db.create_all()
            user = User('testuser', 'test@example.com', 'password123')
            db.session.add(user)
            db.session.commit()
            
            message = Message(user.id, 'Test message')
            db.session.add(message)
            db.session.commit()
            
            audio_file = AudioFile(message.id, '/path/to/audio.wav', 1048576, 125.5, 'wav')
            assert audio_file.get_file_name() == 'audio.wav'
            assert audio_file.get_file_extension() == '.wav'
            assert audio_file.get_file_size_mb() == 1.0
            assert audio_file.get_duration_formatted() == '02:05'

class TestUserSession:
    """Test UserSession model"""
    
    def test_session_creation(self, app):
        """Test session creation"""
        with app.app_context():
            db.create_all()
            user = User('testuser', 'test@example.com', 'password123')
            db.session.add(user)
            db.session.commit()
            
            session = UserSession(user.id)
            assert session.user_id == user.id
            assert session.session_token is not None
            assert session.is_active
            assert not session.is_expired()
            assert session.is_valid()
    
    def test_session_expiration(self, app):
        """Test session expiration"""
        with app.app_context():
            db.create_all()
            user = User('testuser', 'test@example.com', 'password123')
            db.session.add(user)
            db.session.commit()
            
            # Create expired session
            session = UserSession(user.id, expires_in_hours=-1)
            assert session.is_expired()
            assert not session.is_valid()
    
    def test_session_token_generation(self, app):
        """Test session token generation"""
        with app.app_context():
            token1 = UserSession.generate_token()
            token2 = UserSession.generate_token()
            assert token1 != token2
            assert len(token1) > 20  # Should be a reasonable length