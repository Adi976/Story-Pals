from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from datetime import datetime, timedelta
from chatbot_config import StoryPalsChatbot
import os
from dotenv import load_dotenv

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
