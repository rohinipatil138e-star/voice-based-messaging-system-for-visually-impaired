def test_app_creation(app):
    """Test that the Flask app is created successfully"""
    assert app is not None
    assert app.config['TESTING'] is True

def test_index_route(client):
    """Test that the index route is accessible"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Voice-Based Messaging System' in response.data