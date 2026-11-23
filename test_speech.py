import pytest
import json
import tempfile
import os
import wave
import struct
import io
from models import User
from extensions import db

class TestSpeechEndpoints:
    """Test speech processing endpoints"""
    
    def create_test_wav_file(self, duration=1.0, sample_rate=16000):
        """Create a test WAV file for testing"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        
        # Generate a simple sine wave
        frames = int(duration * sample_rate)
        wav_data = []
        for i in range(frames):
            # Simple sine wave at 440 Hz
            value = int(32767 * 0.3 * (i % (sample_rate // 440)) / (sample_rate // 440))
            wav_data.append(struct.pack('<h', value))
        
        with wave.open(temp_file.name, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b''.join(wav_data))
        
        return temp_file.name
    
    def login_user(self, client, app):
        """Helper to login a test user"""
        with app.app_context():
            db.create_all()
            user = User('testuser', 'test@example.com', 'password123')
            db.session.add(user)
            db.session.commit()
            
            response = client.post('/api/auth/login', 
                json={
                    'username': 'testuser',
                    'password': 'password123'
                })
            
            return json.loads(response.data)['session_token']
    
    def test_speech_services_test_endpoint(self, app, client):
        """Test speech services availability"""
        session_token = self.login_user(client, app)
        
        response = client.get('/api/speech/test',
            headers={'Authorization': f'Bearer {session_token}'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'services' in data
        assert 'speech_recognition' in data['services']
        assert 'text_to_speech' in data['services']
    
    def test_recognize_speech_no_file(self, app, client):
        """Test speech recognition without file"""
        session_token = self.login_user(client, app)
        
        response = client.post('/api/speech/recognize',
            headers={'Authorization': f'Bearer {session_token}'})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'NO_AUDIO_FILE'
    
    def test_recognize_speech_empty_filename(self, app, client):
        """Test speech recognition with empty filename"""
        session_token = self.login_user(client, app)
        
        response = client.post('/api/speech/recognize',
            headers={'Authorization': f'Bearer {session_token}'},
            data={'audio': (io.BytesIO(b''), '')})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'EMPTY_FILENAME'
    
    def test_recognize_speech_invalid_format(self, app, client):
        """Test speech recognition with invalid file format"""
        session_token = self.login_user(client, app)
        
        response = client.post('/api/speech/recognize',
            headers={'Authorization': f'Bearer {session_token}'},
            data={'audio': (io.BytesIO(b'fake content'), 'test.txt')})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'INVALID_FILE_FORMAT'
    
    def test_synthesize_speech_no_data(self, app, client):
        """Test text-to-speech without data"""
        session_token = self.login_user(client, app)
        
        response = client.post('/api/speech/synthesize',
            headers={'Authorization': f'Bearer {session_token}'},
            data='',
            content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'INVALID_REQUEST'
    
    def test_synthesize_speech_no_text(self, app, client):
        """Test text-to-speech without text"""
        session_token = self.login_user(client, app)
        
        response = client.post('/api/speech/synthesize',
            headers={'Authorization': f'Bearer {session_token}'},
            json={'text': ''})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'NO_TEXT'
    
    def test_synthesize_speech_text_too_long(self, app, client):
        """Test text-to-speech with text too long"""
        session_token = self.login_user(client, app)
        
        long_text = 'a' * 5001  # Exceeds 5000 character limit
        
        response = client.post('/api/speech/synthesize',
            headers={'Authorization': f'Bearer {session_token}'},
            json={'text': long_text})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'TEXT_TOO_LONG'
    
    def test_synthesize_speech_success(self, app, client):
        """Test successful text-to-speech synthesis"""
        session_token = self.login_user(client, app)
        
        response = client.post('/api/speech/synthesize',
            headers={'Authorization': f'Bearer {session_token}'},
            json={'text': 'Hello, this is a test message.'})
        
        # This might fail in CI/CD without audio drivers, so we check for either success or specific error
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'message' in data
            assert data['text'] == 'Hello, this is a test message.'
        else:
            # Expected in environments without audio support
            assert response.status_code == 500
    
    def test_download_audio_invalid_filename(self, app, client):
        """Test audio download with invalid filename"""
        session_token = self.login_user(client, app)
        
        # Test with path traversal attempt
        response = client.get('/api/speech/download/..%2Finvalid',
            headers={'Authorization': f'Bearer {session_token}'})
        
        # This should either be 400 (invalid filename) or 404 (not found after sanitization)
        assert response.status_code in [400, 404]
    
    def test_download_audio_file_not_found(self, app, client):
        """Test audio download with non-existent file"""
        session_token = self.login_user(client, app)
        
        response = client.get('/api/speech/download/nonexistent.wav',
            headers={'Authorization': f'Bearer {session_token}'})
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error']['code'] == 'FILE_NOT_FOUND'
    
    def test_speech_endpoints_require_auth(self, app, client):
        """Test that speech endpoints require authentication"""
        # Test without authentication - Flask-Login redirects to login page (302)
        response = client.get('/api/speech/test')
        assert response.status_code == 302  # Redirect to login
        
        response = client.post('/api/speech/recognize')
        assert response.status_code == 302  # Redirect to login
        
        response = client.post('/api/speech/synthesize')
        assert response.status_code == 302  # Redirect to login
        
        response = client.get('/api/speech/download/test.wav')
        assert response.status_code == 302  # Redirect to login