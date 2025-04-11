from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from datetime import datetime, timedelta
from chatbot_config import StoryPalsChatbot
import os
from dotenv import load_dotenv
from models import ParentGoal, ChildInsight, LearningProgress
from learning_activities import ActivityManager

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# Get the absolute path to the instance folder
basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')

# Ensure instance folder exists with proper permissions
os.makedirs(instance_path, exist_ok=True)

# Update database configuration with absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "storypals.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    children = db.relationship('Child', backref='parent', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    preferences = db.Column(db.JSON)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sessions = db.relationship('ChatSession', backref='child', lazy=True)
    stories = db.relationship('Story', backref='child', lazy=True)
    activities = db.relationship('LearningActivity', backref='child', lazy=True)
    vocabulary = db.relationship('VocabularyWord', backref='child', lazy=True)
    schedules = db.relationship('LearningSchedule', backref='child', lazy=True)

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # 'active' or 'completed'
    messages = db.relationship('ChatMessage', backref='session', lazy=True)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(20), nullable=False)  # 'user' or 'bot'
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    title = db.Column(db.String(200))
    messages = db.relationship('Message', backref='conversation', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'))
    status = db.Column(db.String(20), default='draft')  # 'draft', 'completed', 'archived'
    child = db.relationship('Child', backref='stories')

class LearningActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'game', 'puzzle', 'comprehension'
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'))
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.JSON, nullable=False)  # Store activity data
    completed_at = db.Column(db.DateTime)
    score = db.Column(db.Integer)
    child = db.relationship('Child', backref='activities')
    story = db.relationship('Story')

class VocabularyWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    word = db.Column(db.String(100), nullable=False)
    definition = db.Column(db.Text)
    example_sentence = db.Column(db.Text)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'))
    learned_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    mastery_level = db.Column(db.Integer, default=0)  # 0-5 scale
    child = db.relationship('Child', backref='vocabulary')
    story = db.relationship('Story')

class LearningSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # 'story_time', 'learning_session'
    scheduled_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # 'scheduled', 'completed', 'missed'
    child = db.relationship('Child', backref='schedules')

# Initialize chatbot
chatbot = StoryPalsChatbot()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_active_session(child_id):
    child = Child.query.get_or_404(child_id)
    active_session = ChatSession.query.filter_by(
        child_id=child_id,
        is_active=True
    ).first()
    
    if not active_session:
        active_session = ChatSession(child_id=child_id)
        db.session.add(active_session)
        db.session.commit()
    
    # Check if session has expired (2 hours)
    if datetime.utcnow() - active_session.start_time > timedelta(hours=2):
        active_session.is_active = False
        active_session.end_time = datetime.utcnow()
        db.session.commit()
        return None
    
    return active_session

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/child-details')
@login_required
def child_details_page():
    return render_template('child_details.html')

@app.route('/chat/<int:child_id>')
@login_required
def chat(child_id):
    child = Child.query.get_or_404(child_id)
    if child.user_id != current_user.id:
        return redirect(url_for('home'))
    return render_template('chat.html', child=child)

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print(f"Received registration data: {data}")  # Debug log
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            print("Missing email or password")  # Debug log
            return jsonify({'error': 'Email and password are required'}), 400
        
        print(f"Checking if email exists: {email}")  # Debug log
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"Email already registered: {email}")  # Debug log
            return jsonify({'error': 'Email already registered'}), 400
        
        print("Creating new user...")  # Debug log
        user = User(email=email, password=password)
        db.session.add(user)
        print("Committing to database...")  # Debug log
        db.session.commit()
        print(f"User registered successfully: {email}")  # Debug log
        
        print("Logging in user...")  # Debug log
        login_user(user)
        return jsonify({'message': 'Registration successful'})
    except Exception as e:
        print(f"Registration error: {str(e)}")  # Debug log
        print(f"Error type: {type(e)}")  # Debug log
        import traceback
        print(f"Traceback: {traceback.format_exc()}")  # Debug log
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    if user and user.password == password:  # In production, verify hashed password
        login_user(user)
        return jsonify({'message': 'Login successful'})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/child/create', methods=['POST'])
@login_required
def create_child():
    try:
        data = request.get_json()
        print(f"Received child data: {data}")  # Debug log
        
        child = Child(
            name=data['name'],
            age=data['age'],
            preferences={'interests': data.get('interests', [])},
            user_id=current_user.id
        )
        db.session.add(child)
        db.session.commit()
        print(f"Child created successfully with ID: {child.id}")  # Debug log
        return jsonify({'child_id': child.id})
    except Exception as e:
        print(f"Error creating child: {str(e)}")  # Debug log
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/<int:child_id>/message', methods=['POST'])
@login_required
def send_message(child_id):
    try:
        data = request.get_json()
        message = data.get('message')
        if not message:
            return jsonify({'error': 'Message is required'}), 400

        child = Child.query.get_or_404(child_id)
        if child.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403

        # Create or get active session
        active_session = ChatSession.query.filter_by(
            child_id=child_id,
            status='active'
        ).first()

        if not active_session:
            active_session = ChatSession(
                child_id=child_id,
                start_time=datetime.utcnow(),
                status='active'
            )
            db.session.add(active_session)
            db.session.commit()

        # Get recent conversation history (last 3 messages for better context)
        recent_messages = ChatMessage.query.filter_by(
            session_id=active_session.id
        ).order_by(ChatMessage.timestamp.desc()).limit(3).all()
        recent_messages.reverse()

        # Create user message
        user_message = ChatMessage(
            session_id=active_session.id,
            content=message,
            sender='user'
        )
        db.session.add(user_message)
        db.session.commit()

        # Get bot response
        bot = StoryPalsChatbot()
        
        # Get available stories based on interests
        available_stories = []
        interests = child.preferences.get('interests', []) if child.preferences else []
        for interest in interests:
            # Remove emoji from interest name for matching
            interest_name = interest.split()[0].lower()
            if interest_name == 'space':
                available_stories.extend([
                    "The Space Adventure",
                    "Journey to Mars",
                    "The Starry Night"
                ])
            elif interest_name == 'science':
                available_stories.extend([
                    "The Magic of Science",
                    "The Curious Scientist",
                    "Science Experiments"
                ])
            elif interest_name == 'mystery':
                available_stories.extend([
                    "The Mystery Box",
                    "The Detective's Clue",
                    "The Hidden Treasure"
                ])
        
        # Remove duplicates
        available_stories = list(set(available_stories))

        # Prepare conversation context with clear formatting
        context = "Previous conversation:\n"
        for msg in recent_messages:
            role = "User" if msg.sender == 'user' else "StoryPals"
            context += f"{role}: {msg.content}\n"
        context += f"\nCurrent message: {message}"

        # Get bot response with correct parameters and timeout
        try:
            bot_response = bot.get_response(
                message=message,
                child_age=child.age,
                context=context,
                available_stories=available_stories
            )
        except Exception as e:
            print(f"Error getting bot response: {str(e)}")
            # Fallback response if the bot fails
            bot_response = "I'm here to tell you stories! Would you like to hear about space adventures, science experiments, or mystery tales? 😊"

        # Create bot message
        bot_message = ChatMessage(
            session_id=active_session.id,
            content=bot_response,
            sender='bot'
        )
        db.session.add(bot_message)
        db.session.commit()

        return jsonify({
            'message': bot_response,
            'session_id': active_session.id
        })

    except Exception as e:
        print(f"Error in send_message: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/<int:child_id>/end', methods=['POST'])
@login_required
def end_chat(child_id):
    try:
        child = Child.query.get_or_404(child_id)
        if child.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403

        active_session = ChatSession.query.filter_by(
            child_id=child_id,
            status='active'
        ).first()

        if active_session:
            active_session.status = 'completed'
            active_session.end_time = datetime.utcnow()
            db.session.commit()

        return jsonify({'message': 'Chat session ended successfully'})

    except Exception as e:
        print(f"Error in end_chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<int:child_id>')
@login_required
def get_sessions(child_id):
    sessions = ChatSession.query.filter_by(child_id=child_id).all()
    return jsonify({
        'sessions': [{
            'id': session.id,
            'start_time': session.start_time.isoformat(),
            'is_active': session.is_active
        } for session in sessions]
    })

@app.route('/api/conversations/<int:child_id>')
@login_required
def get_conversations(child_id):
    conversations = Conversation.query.join(ChatSession).filter(
        ChatSession.child_id == child_id
    ).all()
    return jsonify([{
        'id': conv.id,
        'title': conv.title
    } for conv in conversations])

@app.route('/api/conversations/<int:child_id>/<int:conversation_id>')
@login_required
def get_conversation(child_id, conversation_id):
    conversation = Conversation.query.join(ChatSession).filter(
        ChatSession.child_id == child_id,
        Conversation.id == conversation_id
    ).first_or_404()
    
    return jsonify({
        'id': conversation.id,
        'title': conversation.title,
        'messages': [{
            'role': msg.role,
            'content': msg.content
        } for msg in conversation.messages]
    })

@app.route('/api/conversations/create', methods=['POST'])
@login_required
def create_conversation():
    data = request.get_json()
    child_id = data.get('child_id')
    
    if not child_id:
        return jsonify({'error': 'Child ID is required'}), 400
    
    active_session = get_active_session(child_id)
    if not active_session:
        return jsonify({'error': 'Session expired'}), 401
    
    conversation = Conversation(session_id=active_session.id)
    db.session.add(conversation)
    db.session.commit()
    
    return jsonify({
        'conversation_id': conversation.id
    })

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/api/parent/goals/<int:child_id>', methods=['GET', 'POST'])
@login_required
def manage_goals(child_id):
    child = Child.query.get_or_404(child_id)
    if child.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'GET':
        goals = ParentGoal.query.filter_by(child_id=child_id).all()
        return jsonify({
            'goals': [{
                'id': goal.id,
                'type': goal.goal_type,
                'target': goal.target,
                'start_date': goal.start_date.isoformat(),
                'end_date': goal.end_date.isoformat() if goal.end_date else None,
                'status': goal.status,
                'progress': goal.progress
            } for goal in goals]
        })

    if request.method == 'POST':
        data = request.get_json()
        goal = ParentGoal(
            child_id=child_id,
            goal_type=data['type'],
            target=data['target'],
            start_date=datetime.utcnow(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d') if 'end_date' in data else None,
            progress={}
        )
        db.session.add(goal)
        db.session.commit()
        return jsonify({'message': 'Goal created successfully', 'goal_id': goal.id})

@app.route('/api/parent/insights/<int:child_id>')
@login_required
def get_insights(child_id):
    child = Child.query.get_or_404(child_id)
    if child.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    insights = ChildInsight.query.filter_by(child_id=child_id).order_by(ChildInsight.timestamp.desc()).all()
    return jsonify({
        'insights': [{
            'id': insight.id,
            'type': insight.insight_type,
            'data': insight.data,
            'timestamp': insight.timestamp.isoformat(),
            'confidence': insight.confidence
        } for insight in insights]
    })

@app.route('/api/parent/progress/<int:child_id>')
@login_required
def get_progress(child_id):
    child = Child.query.get_or_404(child_id)
    if child.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    progress = LearningProgress.query.filter_by(child_id=child_id).order_by(LearningProgress.timestamp.desc()).all()
    return jsonify({
        'progress': [{
            'id': p.id,
            'category': p.category,
            'metric': p.metric,
            'value': p.value,
            'timestamp': p.timestamp.isoformat(),
            'context': p.context
        } for p in progress]
    })

@app.route('/api/parent/chat-history/<int:child_id>')
@login_required
def get_chat_history(child_id):
    child = Child.query.get_or_404(child_id)
    if child.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    sessions = ChatSession.query.filter_by(child_id=child_id).order_by(ChatSession.start_time.desc()).all()
    chat_history = []
    
    for session in sessions:
        messages = ChatMessage.query.filter_by(session_id=session.id).order_by(ChatMessage.timestamp).all()
        chat_history.append({
            'session_id': session.id,
            'start_time': session.start_time.isoformat(),
            'end_time': session.end_time.isoformat() if session.end_time else None,
            'messages': [{
                'content': msg.content,
                'sender': msg.sender,
                'timestamp': msg.timestamp.isoformat()
            } for msg in messages]
        })
    
    return jsonify({'chat_history': chat_history})

@app.route('/api/parent/sleep-schedule/<int:child_id>', methods=['GET', 'POST'])
@login_required
def manage_sleep_schedule(child_id):
    child = Child.query.get_or_404(child_id)
    if child.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'GET':
        sleep_goal = ParentGoal.query.filter_by(
            child_id=child_id,
            goal_type='sleep_time'
        ).first()
        
        if sleep_goal:
            return jsonify({
                'bedtime': sleep_goal.target,
                'status': sleep_goal.status,
                'progress': sleep_goal.progress
            })
        return jsonify({'message': 'No sleep schedule set'})

    if request.method == 'POST':
        data = request.get_json()
        bedtime = data.get('bedtime')
        
        # Update or create sleep goal
        sleep_goal = ParentGoal.query.filter_by(
            child_id=child_id,
            goal_type='sleep_time'
        ).first()
        
        if sleep_goal:
            sleep_goal.target = bedtime
            sleep_goal.status = 'active'
        else:
            sleep_goal = ParentGoal(
                child_id=child_id,
                goal_type='sleep_time',
                target=bedtime,
                start_date=datetime.utcnow()
            )
            db.session.add(sleep_goal)
        
        db.session.commit()
        return jsonify({'message': 'Sleep schedule updated successfully'})

@app.route('/api/stories/<int:child_id>', methods=['GET', 'POST'])
@login_required
def manage_stories(child_id):
    child = Child.query.get_or_404(child_id)
    if child.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'GET':
        stories = Story.query.filter_by(child_id=child_id).order_by(Story.created_at.desc()).all()
        return jsonify({
            'stories': [{
                'id': story.id,
                'title': story.title,
                'created_at': story.created_at.isoformat(),
                'status': story.status,
                'character_id': story.character_id
            } for story in stories]
        })

    if request.method == 'POST':
        data = request.get_json()
        story = Story(
            child_id=child_id,
            title=data['title'],
            content=data['content'],
            character_id=data.get('character_id')
        )
        db.session.add(story)
        db.session.commit()
        return jsonify({'message': 'Story created successfully', 'story_id': story.id})

@app.route('/api/stories/<int:child_id>/<int:story_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_story(child_id, story_id):
    child = Child.query.get_or_404(child_id)
    if child.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    story = Story.query.filter_by(id=story_id, child_id=child_id).first_or_404()

    if request.method == 'GET':
        return jsonify({
            'id': story.id,
            'title': story.title,
            'content': story.content,
            'created_at': story.created_at.isoformat(),
            'last_modified': story.last_modified.isoformat(),
            'status': story.status,
            'character_id': story.character_id
        })

    if request.method == 'PUT':
        data = request.get_json()
        story.title = data.get('title', story.title)
        story.content = data.get('content', story.content)
        story.status = data.get('status', story.status)
        story.last_modified = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Story updated successfully'})

    if request.method == 'DELETE':
        db.session.delete(story)
        db.session.commit()
        return jsonify({'message': 'Story deleted successfully'})

@app.route('/api/activities/<int:child_id>', methods=['GET', 'POST'])
@login_required
def manage_activities(child_id):
    child = Child.query.get_or_404(child_id)
    if child.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'GET':
        activities = LearningActivity.query.filter_by(child_id=child_id).order_by(LearningActivity.created_at.desc()).all()
        return jsonify({
            'activities': [{
                'id': activity.id,
                'type': activity.type,
                'title': activity.title,
                'completed_at': activity.completed_at.isoformat() if activity.completed_at else None,
                'score': activity.score
            } for activity in activities]
        })

    if request.method == 'POST':
        data = request.get_json()
        activity = LearningActivity(
            child_id=child_id,
            type=data['type'],
            story_id=data.get('story_id'),
            title=data['title'],
            content=data['content']
        )
        db.session.add(activity)
        db.session.commit()
        return jsonify({'message': 'Activity created successfully', 'activity_id': activity.id})

@app.route('/api/vocabulary/<int:child_id>', methods=['GET', 'POST'])
@login_required
def manage_vocabulary(child_id):
    child = Child.query.get_or_404(child_id)
    if child.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'GET':
        words = VocabularyWord.query.filter_by(child_id=child_id).order_by(VocabularyWord.learned_at.desc()).all()
        return jsonify({
            'vocabulary': [{
                'id': word.id,
                'word': word.word,
                'definition': word.definition,
                'example_sentence': word.example_sentence,
                'mastery_level': word.mastery_level,
                'learned_at': word.learned_at.isoformat()
            } for word in words]
        })

    if request.method == 'POST':
        data = request.get_json()
        word = VocabularyWord(
            child_id=child_id,
            word=data['word'],
            definition=data.get('definition'),
            example_sentence=data.get('example_sentence'),
            story_id=data.get('story_id')
        )
        db.session.add(word)
        db.session.commit()
        return jsonify({'message': 'Vocabulary word added successfully', 'word_id': word.id})

@app.route('/api/schedule/<int:child_id>', methods=['GET', 'POST'])
@login_required
def manage_schedule(child_id):
    child = Child.query.get_or_404(child_id)
    if child.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'GET':
        schedules = LearningSchedule.query.filter_by(child_id=child_id).order_by(LearningSchedule.scheduled_time).all()
        return jsonify({
            'schedules': [{
                'id': schedule.id,
                'activity_type': schedule.activity_type,
                'scheduled_time': schedule.scheduled_time.isoformat(),
                'duration_minutes': schedule.duration_minutes,
                'status': schedule.status
            } for schedule in schedules]
        })

    if request.method == 'POST':
        data = request.get_json()
        schedule = LearningSchedule(
            child_id=child_id,
            activity_type=data['activity_type'],
            scheduled_time=datetime.fromisoformat(data['scheduled_time']),
            duration_minutes=data['duration_minutes']
        )
        db.session.add(schedule)
        db.session.commit()
        return jsonify({'message': 'Schedule created successfully', 'schedule_id': schedule.id})

@app.route('/api/analytics/<int:child_id>')
@login_required
def get_analytics(child_id):
    child = Child.query.get_or_404(child_id)
    if child.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get story statistics
    total_stories = Story.query.filter_by(child_id=child_id).count()
    completed_stories = Story.query.filter_by(child_id=child_id, status='completed').count()

    # Get activity statistics
    activities = LearningActivity.query.filter_by(child_id=child_id).all()
    activity_types = {}
    for activity in activities:
        activity_types[activity.type] = activity_types.get(activity.type, 0) + 1

    # Get vocabulary statistics
    vocabulary_words = VocabularyWord.query.filter_by(child_id=child_id).all()
    mastery_levels = {}
    for word in vocabulary_words:
        mastery_levels[word.mastery_level] = mastery_levels.get(word.mastery_level, 0) + 1

    # Get schedule statistics
    total_scheduled = LearningSchedule.query.filter_by(child_id=child_id).count()
    completed_scheduled = LearningSchedule.query.filter_by(child_id=child_id, status='completed').count()

    return jsonify({
        'stories': {
            'total': total_stories,
            'completed': completed_stories,
            'completion_rate': (completed_stories / total_stories * 100) if total_stories > 0 else 0
        },
        'activities': {
            'by_type': activity_types,
            'total': len(activities)
        },
        'vocabulary': {
            'total_words': len(vocabulary_words),
            'mastery_distribution': mastery_levels
        },
        'schedule': {
            'total_scheduled': total_scheduled,
            'completed': completed_scheduled,
            'completion_rate': (completed_scheduled / total_scheduled * 100) if total_scheduled > 0 else 0
        }
    })

@app.route('/api/activities/<int:child_id>/create', methods=['POST'])
@login_required
def create_learning_activity(child_id):
    child = Child.query.get_or_404(child_id)
    if child.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    activity_type = data.get('type')
    story_id = data.get('story_id')
    
    if not activity_type:
        return jsonify({'error': 'Activity type is required'}), 400

    # Get story content if story_id is provided
    story_content = None
    if story_id:
        story = Story.query.filter_by(id=story_id, child_id=child_id).first()
        if story:
            story_content = story.content

    # Get vocabulary words if needed
    words = None
    if activity_type in ['vocabulary', 'memory_game']:
        words = [word.word for word in VocabularyWord.query.filter_by(child_id=child_id).all()]

    # Create activity using ActivityManager
    activity_manager = ActivityManager()
    try:
        activity_content = activity_manager.create_activity(
            activity_type=activity_type,
            story_content=story_content,
            words=words
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    # Save activity to database
    activity = LearningActivity(
        child_id=child_id,
        type=activity_type,
        story_id=story_id,
        title=f"{activity_type.title()} Activity",
        content=activity_content
    )
    db.session.add(activity)
    db.session.commit()

    return jsonify({
        'message': 'Activity created successfully',
        'activity_id': activity.id,
        'content': activity_content
    })

@app.route('/api/activities/<int:child_id>/<int:activity_id>/submit', methods=['POST'])
@login_required
def submit_activity_answer(child_id, activity_id):
    child = Child.query.get_or_404(child_id)
    if child.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    activity = LearningActivity.query.filter_by(id=activity_id, child_id=child_id).first_or_404()
    data = request.get_json()
    answer = data.get('answer')

    if not answer:
        return jsonify({'error': 'Answer is required'}), 400

    # Validate answer using ActivityManager
    activity_manager = ActivityManager()
    try:
        is_correct = activity_manager.validate_answer(activity.content, answer)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    # Update activity status
    activity.completed_at = datetime.utcnow()
    activity.score = 100 if is_correct else 0
    db.session.commit()

    return jsonify({
        'message': 'Answer submitted successfully',
        'is_correct': is_correct,
        'score': activity.score
    })

if __name__ == '__main__':
    print("Creating database tables...")  # Debug log
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")  # Debug log
        except Exception as e:
            print(f"Error creating database tables: {str(e)}")  # Debug log
            import traceback
            print(f"Traceback: {traceback.format_exc()}")  # Debug log
    print("Starting Flask application...")  # Debug log
    app.run(debug=True)
