# voice-based-messaging-system-for-visually-impaired
A voice-based messaging system designed for visually impaired users to send, read, and delete emails using voice commands. It uses speech recognition and text-to-speech technology with a Flask interface, Python, and PostgreSQL to provide an accessible and user-friendly communication experience.

🎤 Voice-Based Messaging System for Visually Impaired Users

📌 About the Project

The Voice-Based Messaging System is a web application designed to help visually impaired users communicate through voice instead of depending entirely on typing.

Users can compose messages using speech recognition, convert text into speech, send emails, and manage their messages through an accessible interface.

🎯 Objectives

- Make digital communication easier for visually impaired users.
- Reduce the need for keyboard-based typing.
- Provide voice-based message composition.
- Improve accessibility through audio feedback.

✨ Features

- Speech-to-Text: Converts spoken words into written text.
- Text-to-Speech: Reads text and provides audio feedback.
- Email Integration: Send messages through email.
- User Authentication: Registration and login functionality.
- Inbox Management: View received and sent messages.
- Message Management: Create, view, and delete messages.
- Accessible Interface: Voice interaction and keyboard navigation.

🛠️ Technologies Used

Technology| Purpose
Python| Backend programming
Flask| Web framework
HTML| Web page structure
CSS| Styling
JavaScript| Frontend interaction
PostgreSQL| Database
SQLAlchemy| Database management
SpeechRecognition| Speech-to-text
pyttsx3| Text-to-speech
Flask-Mail| Email integration

📂 Project Structure

Voice-Based-Messaging-System/
│
├── app.py
├── config.py
├── extensions.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── blueprints/
├── models/
├── templates/
├── static/
│   ├── css/
│   └── js/
│
├── utils/
├── migrations/
└── tests/

⚙️ Installation and Setup

1. Clone the Repository

git clone YOUR_GITHUB_REPOSITORY_URL

2. Navigate to the Project Folder

cd Voice-Based-Messaging-System

3. Create a Virtual Environment

python -m venv venv

4. Activate the Virtual Environment

Windows:

venv\Scripts\activate

5. Install Dependencies

pip install -r requirements.txt

6. Configure Environment Variables

Create a ".env" file using ".env.example".

Add your own:

- Flask secret key
- PostgreSQL database URL
- Email server configuration
- Email credentials

Do not upload your ".env" file to GitHub.

7. Initialize the Database

python -c "from app import create_app; from extensions import db; app=create_app(); app.app_context().push(); db.create_all()"

8. Run the Application

python app.py

Open your browser:

http://localhost:5000

🚀 How It Works

1. Register or log in to the application.
2. Open the message composition page.
3. Use the microphone to record your message.
4. Convert speech into text.
5. Enter the recipient's email address.
6. Send the message.
7. Access received and sent messages through the inbox.

🔮 Future Enhancements

- Support for multiple languages.
- Improved voice-only navigation.
- Offline speech recognition.
- Mobile application support.
- Integration with additional messaging platforms.

🎓 Project Information

Project Title: Voice-Based Messaging System for Visually Impaired Users

Project Type: Web Application

Domain: Web Development and Accessibility

❤️ Conclusion

This project aims to make communication more accessible and convenient for visually impaired individuals by using speech recognition and text-to-speech technologies.
