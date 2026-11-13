"""
UZHAVAR AI – Kannada Voice Bridge
Permanent SQLite Database Models with SQLAlchemy ORM
Manages Persistent Conversations, Chronological Messages & Rolling Context Memory
"""

import os
import sys
import uuid
from datetime import datetime

# Load pure-Python vendor SQLAlchemy to comply with Windows security policies
vendor_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'vendor')
if os.path.exists(vendor_dir) and vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)

os.environ['DISABLE_SQLALCHEMY_CEXT'] = '1'

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Conversation(db.Model):
    __tablename__ = 'conversations'

    conversation_id = db.Column(db.String(64), primary_key=True)
    conversation_title = db.Column(
        db.String(255),
        nullable=False,
        default="ಹೊಸ ಕೃಷಿ ಸಮಾಲೋಚನೆ (New Farming Consultation)"
    )
    selected_language = db.Column(db.String(16), nullable=False, default="kn")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        index=True
    )
    conversation_summary = db.Column(db.Text, nullable=True)

    # One-to-many relationship with cascade delete
    messages = db.relationship(
        'Message',
        backref='conversation',
        cascade='all, delete-orphan',
        order_by='Message.timestamp.asc()',
        lazy='select'
    )

    def to_dict(self, include_messages=False):
        data = {
            'conversation_id': self.conversation_id,
            'conversation_title': self.conversation_title,
            'selected_language': self.selected_language,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'conversation_summary': self.conversation_summary,
            'message_count': len(self.messages) if self.messages else 0
        }
        if include_messages:
            data['messages'] = [m.to_dict() for m in self.messages]
        return data


class Message(db.Model):
    __tablename__ = 'messages'

    message_id = db.Column(
        db.String(64),
        primary_key=True,
        default=lambda: f"msg_{uuid.uuid4().hex[:12]}"
    )
    conversation_id = db.Column(
        db.String(64),
        db.ForeignKey('conversations.conversation_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    sender = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    message_text = db.Column(db.Text, nullable=False)
    original_language = db.Column(db.String(16), nullable=False, default="kn")
    message_type = db.Column(db.String(20), nullable=False, default="text")  # 'text' or 'voice'
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    audio_reference = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'message_id': self.message_id,
            'conversation_id': self.conversation_id,
            'sender': self.sender,
            'message_text': self.message_text,
            'original_language': self.original_language,
            'message_type': self.message_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'audio_reference': self.audio_reference
        }
