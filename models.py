from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_login import UserMixin

db = SQLAlchemy()

class Parent(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    children = db.relationship('Child', backref='parent', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Child(db.Model):
    id = db.Column(db.String(36), primary_key=True)  # UUID
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    preferences = db.Column(db.String(500))  # JSON string of preferences
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sessions = db.relationship('ChatSession', backref='child', lazy=True)
    goals = db.relationship('ParentGoal', backref='child', lazy=True)
    insights = db.relationship('ChildInsight', backref='child', lazy=True)
    progress = db.relationship('LearningProgress', backref='child', lazy=True)

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.String(36), db.ForeignKey('child.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    conversations = db.relationship('Conversation', backref='session', lazy=True)

    @property
    def duration(self):
        if self.end_time:
            return self.end_time - self.start_time
        return datetime.utcnow() - self.start_time

    @property
    def is_expired(self):
        return self.duration > timedelta(hours=2)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    user_input = db.Column(db.String(500))
    bot_response = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    context = db.Column(db.String(1000))  # JSON string of conversation context

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    category = db.Column(db.String(100))
    age_range = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ParentGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    goal_type = db.Column(db.String(50), nullable=False)  # 'word_of_day', 'sleep_time', 'learning_goal'
    target = db.Column(db.String(200), nullable=False)  # The actual goal (word, time, etc.)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'failed'
    progress = db.Column(db.JSON)  # Track progress for each goal

class ChildInsight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    insight_type = db.Column(db.String(50), nullable=False)  # 'vocabulary', 'interests', 'sleep_pattern'
    data = db.Column(db.JSON, nullable=False)  # The actual insight data
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    confidence = db.Column(db.Float)  # Confidence score of the insight

class LearningProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'vocabulary', 'comprehension', 'creativity'
    metric = db.Column(db.String(50), nullable=False)  # Specific metric being tracked
    value = db.Column(db.Float, nullable=False)  # The actual progress value
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    context = db.Column(db.JSON)  # Additional context about the progress

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(20), nullable=False)  # 'user' or 'bot'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) 