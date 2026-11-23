"""
Standalone Voice-Controlled Email Application
Run this script for complete voice control from start to end
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.voice_commands import (
    VoiceCommandHandler,
    VoiceLoginHandler,
    VoiceRegistrationHandler,
    VoiceComposeHandler
)
from models import User, Message
from extensions import db
from app import create_app
from flask_login import login_user, logout_user, current_user
import time

class VoiceEmailApp:
    """Main voice-controlled email application"""
    
    def __init__(self):
        self.app = create_app()
        self.voice = VoiceCommandHandler()
        self.running = True
        self.logged_in_user = None
        
    def start(self):
        """Start the voice-controlled application"""
        self.voice.speak("Welcome to the fully voice-controlled email system!")
        self.voice.speak("You can control everything using just your voice.")
        time.sleep(0.5)
        
        # Main loop
        while self.running:
            try:
                if self.logged_in_user is None:
                    self.show_welcome_menu()
                else:
                    self.show_main_menu()
            except KeyboardInterrupt:
                self.voice.speak("Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                self.voice.speak("Sorry, there was an error. Let's try again.")
    
    def show_welcome_menu(self):
        """Show welcome menu for non-logged-in users"""
        self.voice.speak("You are not logged in. Would you like to login or register?")
        self.voice.speak("Say login to sign in, or say register to create a new account.")
        
        command = self.voice.listen()
        if command is None:
            return
        
        action, _ = self.voice.parse_command(command)
        
        if action == 'login':
            self.handle_login()
        elif action == 'register':
            self.handle_register()
        elif action == 'help':
            self.voice.provide_help()
        elif action in ['exit', 'quit', 'cancel']:
            self.voice.speak("Goodbye!")
            self.running = False
        else:
            self.voice.speak("I didn't understand that. Please say login or register.")
    
    def show_main_menu(self):
        """Show main menu for logged-in users"""
        self.voice.speak(f"Hello {self.logged_in_user.username}. What would you like to do?")
        self.voice.speak("You can compose email, check inbox, or logout.")
        
        command = self.voice.listen()
        if command is None:
            return
        
        action, _ = self.voice.parse_command(command)
        
        if action == 'compose':
            self.handle_compose()
        elif action == 'inbox':
            self.handle_inbox()
        elif action == 'logout':
            self.handle_logout()
        elif action == 'help':
            self.voice.provide_help()
        elif action in ['exit', 'quit']:
            self.voice.speak("Logging you out. Goodbye!")
            self.handle_logout()
            self.running = False
        else:
            self.voice.speak("I didn't understand that. Please try again.")
    
    def handle_login(self):
        """Handle voice login"""
        with self.app.app_context():
            login_handler = VoiceLoginHandler(self.voice)
            username, password = login_handler.voice_login()
            
            if username is None or password is None:
                self.voice.speak("Login cancelled.")
                return
            
            # Find user
            user = User.query.filter(
                (User.username == username) | (User.email == username.lower())
            ).first()
            
            if not user or not user.check_password(password):
                self.voice.speak("Invalid username or password. Please try again.")
                return
            
            self.logged_in_user = user
            user.update_last_login()
            db.session.commit()
            
            self.voice.speak(f"Welcome back {user.username}! You are now logged in.")
    
    def handle_register(self):
        """Handle voice registration"""
        with self.app.app_context():
            registration_handler = VoiceRegistrationHandler(self.voice)
            username, email, password = registration_handler.voice_register()
            
            if username is None or email is None or password is None:
                self.voice.speak("Registration cancelled.")
                return
            
            # Check if user exists
            existing_user = User.query.filter(
                (User.username == username) | (User.email == email.lower())
            ).first()
            
            if existing_user:
                self.voice.speak("This username or email is already registered. Please try logging in instead.")
                return
            
            # Create new user
            user = User(username, email, password)
            db.session.add(user)
            db.session.commit()
            
            self.logged_in_user = user
            
            self.voice.speak(f"Account created successfully! Welcome {username}. You are now logged in.")
    
    def handle_compose(self):
        """Handle voice email composition"""
        with self.app.app_context():
            compose_handler = VoiceComposeHandler(self.voice)
            email_data = compose_handler.voice_compose()
            
            if email_data is None:
                self.voice.speak("Email composition cancelled.")
                return
            
            # Create message
            message = Message(
                sender_id=self.logged_in_user.id,
                recipient_email=email_data['recipient'],
                subject=email_data['subject'],
                body=email_data['body']
            )
            
            db.session.add(message)
            db.session.commit()
            
            self.voice.speak("Your email has been sent successfully!")
    
    def handle_inbox(self):
        """Handle voice inbox reading"""
        with self.app.app_context():
            # Get user's messages
            messages = Message.query.filter_by(
                recipient_email=self.logged_in_user.email
            ).order_by(Message.created_at.desc()).limit(10).all()
            
            if not messages:
                self.voice.speak("You have no messages in your inbox.")
                return
            
            count = len(messages)
            self.voice.speak(f"You have {count} message{'s' if count > 1 else ''} in your inbox.")
            
            # Read each message
            for i, msg in enumerate(messages, 1):
                sender = User.query.get(msg.sender_id)
                sender_name = sender.username if sender else "Unknown sender"
                
                self.voice.speak(f"Message {i}. From {sender_name}. Subject: {msg.subject}")
                
                # Ask if user wants to hear the body
                self.voice.speak("Would you like me to read this message?")
                response = self.voice.get_voice_input("Say yes or no", input_type='confirmation')
                
                if response == 'yes':
                    self.voice.speak(f"Message body: {msg.body}")
                
                if i < count:
                    self.voice.speak("Would you like to hear the next message?")
                    response = self.voice.get_voice_input("Say yes or no", input_type='confirmation')
                    if response != 'yes':
                        break
            
            self.voice.speak("End of messages.")
    
    def handle_logout(self):
        """Handle logout"""
        if self.logged_in_user:
            username = self.logged_in_user.username
            self.logged_in_user = None
            self.voice.speak(f"Goodbye {username}. You have been logged out.")
        else:
            self.voice.speak("You are not logged in.")


def main():
    """Main entry point"""
    print("=" * 60)
    print("VOICE-CONTROLLED EMAIL SYSTEM")
    print("=" * 60)
    print("\nStarting voice control...")
    print("Make sure your microphone is connected and working.")
    print("Press Ctrl+C to exit at any time.\n")
    
    app = VoiceEmailApp()
    app.start()


if __name__ == '__main__':
    main()
