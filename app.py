from flask import Flask
from config import Config
from extensions import db, login_manager, mail, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    
    # Import models to ensure they are registered with SQLAlchemy
    from models import User, Message, AudioFile, UserSession
    
    # Register blueprints
    from blueprints.auth import auth_bp
    from blueprints.messages import messages_bp
    from blueprints.speech import speech_bp
    from blueprints.main import main_bp
    from blueprints.receive_message import receive_bp
    from blueprints.email_receiver import email_receiver_bp
    from blueprints.voice_control import voice_control_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(messages_bp, url_prefix='/api/messages')
    app.register_blueprint(speech_bp, url_prefix='/api/speech')
    app.register_blueprint(receive_bp, url_prefix='/api/messages')
    app.register_blueprint(email_receiver_bp, url_prefix='/api/email')
    app.register_blueprint(voice_control_bp, url_prefix='/api/voice')
    app.register_blueprint(main_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)