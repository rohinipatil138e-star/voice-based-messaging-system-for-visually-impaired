from datetime import datetime
from extensions import db
import os

class AudioFile(db.Model):
    """AudioFile model for managing recorded voice messages"""
    __tablename__ = 'audio_files'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False, index=True)
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)  # Size in bytes
    duration = db.Column(db.Float)     # Duration in seconds
    format = db.Column(db.String(10))  # File format (wav, mp3, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, message_id, file_path, file_size=None, duration=None, format=None):
        self.message_id = message_id
        self.file_path = file_path
        self.file_size = file_size
        self.duration = duration
        self.format = format
    
    def get_file_name(self):
        """Get filename from file path"""
        return os.path.basename(self.file_path)
    
    def get_file_extension(self):
        """Get file extension"""
        return os.path.splitext(self.file_path)[1].lower()
    
    def file_exists(self):
        """Check if the audio file exists on disk"""
        return os.path.exists(self.file_path)
    
    def get_file_size_mb(self):
        """Get file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None
    
    def get_duration_formatted(self):
        """Get duration in MM:SS format"""
        if self.duration:
            minutes = int(self.duration // 60)
            seconds = int(self.duration % 60)
            return f"{minutes:02d}:{seconds:02d}"
        return "00:00"
    
    def delete_file(self):
        """Delete the audio file from disk"""
        try:
            if self.file_exists():
                os.remove(self.file_path)
                return True
        except OSError:
            pass
        return False
    
    def to_dict(self):
        """Convert audio file to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'message_id': self.message_id,
            'file_path': self.file_path,
            'file_name': self.get_file_name(),
            'file_size': self.file_size,
            'file_size_mb': self.get_file_size_mb(),
            'duration': self.duration,
            'duration_formatted': self.get_duration_formatted(),
            'format': self.format,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'file_exists': self.file_exists()
        }
    
    def __repr__(self):
        return f'<AudioFile {self.id} - {self.get_file_name()}>'