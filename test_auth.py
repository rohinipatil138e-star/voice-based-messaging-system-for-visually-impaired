import pytest
import json
from models import User, UserSession
from extensions import db

class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_register_success(self, app, client):
        """Test successful user registration"""
        with app.app_context():
            db.create_all()
            
            response = client.post('/api/auth/register', 
                json={
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'password': 'password123'
                })
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['message'] == 'User registered successfully'
            assert data['user']['username'] == 'testuser'
            assert data['user']['email'] == 'test@example.com'
            
            # Verify user was created in database
            user = User.query.filter_by(username='testuser').first()
            assert user is not None
            assert user.email == 'test@example.com'
    
    def test_register_missing_fields(self, app, client):
        """Test registration with missing fields"""
        with app.app_context():
            db.create_all()
            
            response = client.post('/api/auth/register', 
                json={
                    'username': 'testuser'
                    # Missing email and password
                })
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['error']['code'] == 'MISSING_FIELDS'
    
    def test_register_invalid_email(self, app, client):
        """Test registration with invalid email"""
        with app.app_context():
            db.create_all()
            
            response = client.post('/api/auth/register', 
                json={
                    'username': 'testuser',
                    'email': 'invalid-email',
                    'password': 'password123'
                })
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['error']['code'] == 'INVALID_EMAIL'
    
    def test_register_weak_password(self, app, client):
        """Test registration with weak password"""
        with app.app_context():
            db.create_all()
            
            response = client.post('/api/auth/register', 
                json={
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'password': '123'  # Too short
                })
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['error']['code'] == 'INVALID_PASSWORD'
    
    def test_register_duplicate_username(self, app, client):
        """Test registration with duplicate username"""
        with app.app_context():
            db.create_all()
            
            # Create first user
            user = User('testuser', 'test1@example.com', 'password123')
            db.session.add(user)
            db.session.commit()
            
            # Try to register with same username
            response = client.post('/api/auth/register', 
                json={
                    'username': 'testuser',
                    'email': 'test2@example.com',
                    'password': 'password123'
                })
            
            assert response.status_code == 409
            data = json.loads(response.data)
            assert data['error']['code'] == 'USERNAME_EXISTS'
    
    def test_login_success(self, app, client):
        """Test successful login"""
        with app.app_context():
            db.create_all()
            
            # Create user
            user = User('testuser', 'test@example.com', 'password123')
            db.session.add(user)
            db.session.commit()
            
            response = client.post('/api/auth/login', 
                json={
                    'username': 'testuser',
                    'password': 'password123'
                })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Login successful'
            assert data['user']['username'] == 'testuser'
            assert 'session_token' in data
    
    def test_login_with_email(self, app, client):
        """Test login with email instead of username"""
        with app.app_context():
            db.create_all()
            
            # Create user
            user = User('testuser', 'test@example.com', 'password123')
            db.session.add(user)
            db.session.commit()
            
            response = client.post('/api/auth/login', 
                json={
                    'username': 'test@example.com',  # Using email
                    'password': 'password123'
                })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Login successful'
    
    def test_login_invalid_credentials(self, app, client):
        """Test login with invalid credentials"""
        with app.app_context():
            db.create_all()
            
            # Create user
            user = User('testuser', 'test@example.com', 'password123')
            db.session.add(user)
            db.session.commit()
            
            response = client.post('/api/auth/login', 
                json={
                    'username': 'testuser',
                    'password': 'wrongpassword'
                })
            
            assert response.status_code == 401
            data = json.loads(response.data)
            assert data['error']['code'] == 'INVALID_CREDENTIALS'
    
    def test_login_missing_credentials(self, app, client):
        """Test login with missing credentials"""
        with app.app_context():
            db.create_all()
            
            response = client.post('/api/auth/login', 
                json={
                    'username': 'testuser'
                    # Missing password
                })
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['error']['code'] == 'MISSING_CREDENTIALS'
    
    def test_login_inactive_user(self, app, client):
        """Test login with inactive user"""
        with app.app_context():
            db.create_all()
            
            # Create inactive user
            user = User('testuser', 'test@example.com', 'password123')
            user.is_active = False
            db.session.add(user)
            db.session.commit()
            
            response = client.post('/api/auth/login', 
                json={
                    'username': 'testuser',
                    'password': 'password123'
                })
            
            assert response.status_code == 403
            data = json.loads(response.data)
            assert data['error']['code'] == 'ACCOUNT_DISABLED'