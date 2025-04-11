import ollama
from datetime import datetime, timedelta
import random
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from collections import Counter
import numpy as np
from textblob import TextBlob
import json
from flask_sqlalchemy import SQLAlchemy
from models import LearningProgress, ChatSession, ChatMessage, ChildInsight

# Initialize database
db = SQLAlchemy()


# Download required NLTK data
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

class StoryPalsChatbot:
    def __init__(self):
        self.model = "gemma:2b"
        self.max_session_duration = timedelta(hours=2)
        self.inappropriate_patterns = [
            # Add patterns to filter out inappropriate content
            # This is a basic example - you should expand this list
            "inappropriate_word1",
            "inappropriate_word2",
        ]
        
        # Enhanced memory tracking
        self.child_memories = {}  # Store child-specific memories
        self.story_history = {}   # Track stories told to each child
        self.conversation_context = {}  # Store conversation context
        
        self.age_appropriate_prompts = {
            "4-6": """You are StoryPals, a friendly AI companion for young children aged 4-6.
            Guidelines:
            1. Be warm, friendly, and encouraging
            2. Use simple words and short sentences
            3. Be playful and fun
            4. Use lots of emojis
            5. Keep responses short and engaging
            6. Be patient and understanding
            7. Share stories when appropriate, but don't force them
            8. Ask simple questions to engage the child
            9. Remember previous conversations and build upon them
            10. Track the child's interests and preferences""",
            
            "7-9": """You are StoryPals, a friendly AI companion for children aged 7-9.
            Guidelines:
            1. Be engaging and supportive
            2. Use age-appropriate vocabulary
            3. Be encouraging and positive
            4. Use some emojis for fun
            5. Keep responses clear and concise
            6. Share stories when the child is interested
            7. Ask thought-provoking questions
            8. Be patient and understanding
            9. Remember previous conversations and build upon them
            10. Track the child's interests and learning progress""",
            
            "10-12": """You are StoryPals, a friendly AI companion for pre-teens aged 10-12.
            Guidelines:
            1. Be engaging and supportive
            2. Use age-appropriate vocabulary
            3. Be encouraging and positive
            4. Use emojis sparingly
            5. Keep responses clear and concise
            6. Share stories when the child is interested
            7. Ask thought-provoking questions
            8. Be patient and understanding
            9. Remember previous conversations and build upon them
            10. Track the child's interests and learning progress"""
        }

        # Enhanced vocabulary tracking
        self.vocabulary_levels = {
            '4-6': set(['simple', 'basic', 'common']),
            '7-9': set(['intermediate', 'descriptive']),
            '10-12': set(['advanced', 'complex'])
        }
        
        # Word of the day tracking
        self.word_of_day = {}
        self.word_contexts = {}
        
        # Sleep time tracking
        self.sleep_schedules = {}
        
        # Learning progress thresholds
        self.progress_thresholds = {
            'vocabulary': {'low': 0.3, 'medium': 0.6, 'high': 0.8},
            'comprehension': {'low': 0.4, 'medium': 0.7, 'high': 0.9},
            'creativity': {'low': 0.3, 'medium': 0.6, 'high': 0.8}
        }

    def update_child_memory(self, child_id, key, value):
        """Update or add information about a child"""
        if child_id not in self.child_memories:
            self.child_memories[child_id] = {}
        self.child_memories[child_id][key] = value

    def get_child_memory(self, child_id, key=None):
        """Retrieve information about a child"""
        if child_id not in self.child_memories:
            return None
        if key:
            return self.child_memories[child_id].get(key)
        return self.child_memories[child_id]

    def track_story(self, child_id, story_title):
        """Track which stories have been told to a child"""
        if child_id not in self.story_history:
            self.story_history[child_id] = []
        self.story_history[child_id].append({
            'title': story_title,
            'timestamp': datetime.utcnow()
        })

    def get_story_history(self, child_id):
        """Get the history of stories told to a child"""
        return self.story_history.get(child_id, [])

    def update_conversation_context(self, child_id, context):
        """Update the conversation context for a child"""
        if child_id not in self.conversation_context:
            self.conversation_context[child_id] = []
        self.conversation_context[child_id].append({
            'timestamp': datetime.utcnow(),
            'context': context
        })
        # Keep only the last 10 conversations for context
        if len(self.conversation_context[child_id]) > 10:
            self.conversation_context[child_id] = self.conversation_context[child_id][-10:]

    def get_conversation_context(self, child_id):
        """Get the recent conversation context for a child"""
        return self.conversation_context.get(child_id, [])

    def get_system_prompt(self, child_id, child_age, context, available_stories):
        """Generate an age-appropriate system prompt with memory context"""
        # Determine age group
        if 4 <= child_age <= 6:
            age_group = "4-6"
        elif 7 <= child_age <= 9:
            age_group = "7-9"
        else:
            age_group = "10-12"
        
        base_prompt = self.age_appropriate_prompts[age_group]
        
        # Get child's memory and preferences
        child_memory = self.get_child_memory(child_id)
        story_history = self.get_story_history(child_id)
        conversation_history = self.get_conversation_context(child_id)
        
        # Build memory context
        memory_context = ""
        if child_memory:
            memory_context += "\nChild's preferences and interests:\n"
            for key, value in child_memory.items():
                memory_context += f"- {key}: {value}\n"
        
        if story_history:
            memory_context += "\nRecent stories told:\n"
            for story in story_history[-3:]:  # Last 3 stories
                memory_context += f"- {story['title']} (told on {story['timestamp'].strftime('%Y-%m-%d')})\n"
        
        if conversation_history:
            memory_context += "\nRecent conversation topics:\n"
            for conv in conversation_history[-3:]:  # Last 3 conversations
                memory_context += f"- {conv['context']}\n"
        
        # Add context
        prompt = f"""{base_prompt}
        
        {memory_context}
        
        Previous conversation: {context}
        
        Remember:
        1. Never share personal information
        2. Never make promises
        3. Never give medical advice
        4. Never share inappropriate content
        5. Always maintain a safe, friendly environment
        6. Be natural and conversational
        7. Share stories only when appropriate
        8. Focus on engaging with the child
        9. Build upon previous conversations
        10. Track the child's learning progress"""
        
        return prompt

    def is_appropriate(self, response):
        """Check if the response is appropriate for children"""
        # Check for inappropriate patterns
        for pattern in self.inappropriate_patterns:
            if pattern in response.lower():
                return False
        
        # Check response length (allow longer responses for stories)
        if len(response.split()) > 500:  # Increased from 100
            return False
        
        return True

    def format_response(self, response, child_age):
        """Format the response to be more engaging and child-friendly"""
        # Basic formatting
        formatted = response.replace('\n\n', '\n')
        formatted = formatted.replace('  ', ' ')
        
        # Add emojis based on age
        if child_age <= 6:
            emotion_mapping = {
                'happy': '😊',
                'sad': '😢',
                'excited': '🎉',
                'surprised': '😮',
                'love': '❤️',
                'star': '⭐',
                'moon': '🌙',
                'sun': '☀️',
                'heart': '💖',
                'story': '📚',
                'magic': '✨',
                'adventure': '🚀',
                'friend': '🤝',
                'learn': '📖',
                'fun': '🎮'
            }
        else:
            emotion_mapping = {
                'happy': '😊',
                'excited': '🎉',
                'star': '⭐',
                'heart': '💖',
                'story': '📚',
                'magic': '✨',
                'adventure': '🚀',
                'learn': '📖'
            }
        
        for emotion, emoji in emotion_mapping.items():
            if emotion in formatted.lower():
                formatted = formatted.replace(emotion, f"{emotion} {emoji}")
        
        return formatted

    def track_learning_progress(self, child_id, message, response):
        """Track learning progress from conversations"""
        # Analyze message and response for learning opportunities
        vocabulary_words = self.extract_vocabulary(message, response)
        comprehension_level = self.assess_comprehension(message, response)
        creativity_score = self.assess_creativity(message, response)
        
        # Store progress
        if vocabulary_words:
            progress = LearningProgress(
                child_id=child_id,
                category='vocabulary',
                metric='new_words',
                value=len(vocabulary_words),
                context={'words': vocabulary_words}
            )
            db.session.add(progress)
        
        if comprehension_level:
            progress = LearningProgress(
                child_id=child_id,
                category='comprehension',
                metric='level',
                value=comprehension_level,
                context={'message': message, 'response': response}
            )
            db.session.add(progress)
        
        if creativity_score:
            progress = LearningProgress(
                child_id=child_id,
                category='creativity',
                metric='score',
                value=creativity_score,
                context={'message': message, 'response': response}
            )
            db.session.add(progress)
        
        db.session.commit()

    def generate_insights(self, child_id):
        """Generate insights about the child's progress and preferences"""
        # Get recent progress data
        recent_progress = LearningProgress.query.filter_by(
            child_id=child_id
        ).order_by(LearningProgress.timestamp.desc()).limit(10).all()
        
        # Get recent conversations
        recent_sessions = ChatSession.query.filter_by(
            child_id=child_id
        ).order_by(ChatSession.start_time.desc()).limit(5).all()
        
        # Generate vocabulary insights
        vocabulary_insight = self.analyze_vocabulary_progress(recent_progress)
        if vocabulary_insight:
            insight = ChildInsight(
                child_id=child_id,
                insight_type='vocabulary',
                data=vocabulary_insight,
                confidence=0.8
            )
            db.session.add(insight)
        
        # Generate interest insights
        interest_insight = self.analyze_interests(recent_sessions)
        if interest_insight:
            insight = ChildInsight(
                child_id=child_id,
                insight_type='interests',
                data=interest_insight,
                confidence=0.7
            )
            db.session.add(insight)
        
        # Generate sleep pattern insights
        sleep_insight = self.analyze_sleep_patterns(recent_sessions)
        if sleep_insight:
            insight = ChildInsight(
                child_id=child_id,
                insight_type='sleep_pattern',
                data=sleep_insight,
                confidence=0.6
            )
            db.session.add(insight)
        
        db.session.commit()

    def extract_vocabulary(self, message, response):
        """Extract new vocabulary words using NLP techniques"""
        # Tokenize and tag parts of speech
        message_tokens = word_tokenize(message.lower())
        response_tokens = word_tokenize(response.lower())
        
        # Get age-appropriate vocabulary level
        age_group = self.get_age_group(self.get_child_age(message))
        target_level = self.vocabulary_levels[age_group]
        
        # Extract nouns, verbs, and adjectives
        message_tags = nltk.pos_tag(message_tokens)
        response_tags = nltk.pos_tag(response_tokens)
        
        new_words = set()
        
        # Check for new words in response
        for word, tag in response_tags:
            if tag.startswith(('NN', 'VB', 'JJ')):  # Nouns, verbs, adjectives
                # Check if word is new and age-appropriate
                if (word not in message_tokens and 
                    len(word) > 3 and  # Avoid very short words
                    self.is_age_appropriate(word, age_group)):
                    new_words.add(word)
        
        return list(new_words)

    def assess_comprehension(self, message, response):
        """Assess comprehension using multiple metrics"""
        # Calculate response relevance
        relevance_score = self.calculate_relevance(message, response)
        
        # Analyze response complexity
        complexity_score = self.analyze_complexity(response)
        
        # Check for understanding indicators
        understanding_score = self.check_understanding_indicators(message, response)
        
        # Combine scores
        comprehension_score = (relevance_score * 0.4 + 
                             complexity_score * 0.3 + 
                             understanding_score * 0.3)
        
        return comprehension_score

    def assess_creativity(self, message, response):
        """Assess creativity using multiple metrics"""
        # Calculate originality
        originality_score = self.calculate_originality(response)
        
        # Analyze language richness
        richness_score = self.analyze_language_richness(response)
        
        # Check for imaginative elements
        imagination_score = self.check_imagination(response)
        
        # Combine scores
        creativity_score = (originality_score * 0.4 + 
                          richness_score * 0.3 + 
                          imagination_score * 0.3)
        
        return creativity_score

    def analyze_vocabulary_progress(self, recent_progress):
        """Analyze vocabulary learning progress with detailed metrics"""
        if not recent_progress:
            return None
            
        vocabulary_data = [p for p in recent_progress if p.category == 'vocabulary']
        if not vocabulary_data:
            return None
            
        # Calculate metrics
        total_words = sum(p.value for p in vocabulary_data)
        unique_words = set()
        for progress in vocabulary_data:
            if progress.context and 'words' in progress.context:
                unique_words.update(progress.context['words'])
        
        # Calculate retention rate
        retention_rate = self.calculate_retention_rate(vocabulary_data)
        
        # Generate insight
        insight = {
            'total_words_learned': total_words,
            'unique_words': len(unique_words),
            'retention_rate': retention_rate,
            'trend': self.calculate_trend(vocabulary_data),
            'recommendations': self.generate_vocabulary_recommendations(vocabulary_data)
        }
        
        return insight

    def analyze_interests(self, recent_sessions):
        """Analyze child's interests using conversation patterns"""
        if not recent_sessions:
            return None
            
        # Extract topics and themes
        topics = []
        for session in recent_sessions:
            messages = ChatMessage.query.filter_by(session_id=session.id).all()
            for msg in messages:
                if msg.sender == 'user':
                    topics.extend(self.extract_topics(msg.content))
        
        # Calculate interest scores
        topic_counter = Counter(topics)
        total_topics = sum(topic_counter.values())
        
        # Generate interest profile
        interest_profile = {
            'primary_interests': dict(topic_counter.most_common(3)),
            'interest_diversity': len(topic_counter) / total_topics if total_topics > 0 else 0,
            'trending_topics': self.identify_trending_topics(topic_counter),
            'recommendations': self.generate_interest_recommendations(topic_counter)
        }
        
        return interest_profile

    def analyze_sleep_patterns(self, recent_sessions):
        """Analyze sleep patterns using chat session timing"""
        if not recent_sessions:
            return None
            
        # Extract session times
        session_times = [session.start_time for session in recent_sessions]
        
        # Calculate patterns
        patterns = {
            'average_start_time': self.calculate_average_time(session_times),
            'consistency_score': self.calculate_consistency(session_times),
            'late_night_sessions': self.count_late_night_sessions(session_times),
            'recommendations': self.generate_sleep_recommendations(session_times)
        }
        
        return patterns

    # Helper methods
    def get_age_group(self, age):
        if 4 <= age <= 6:
            return '4-6'
        elif 7 <= age <= 9:
            return '7-9'
        else:
            return '10-12'

    def is_age_appropriate(self, word, age_group):
        # Implement age-appropriate word checking
        # This is a simplified version - expand with more sophisticated checks
        word_length = len(word)
        if age_group == '4-6':
            return word_length <= 6
        elif age_group == '7-9':
            return word_length <= 8
        else:
            return True

    def calculate_relevance(self, message, response):
        # Implement relevance calculation
        message_vec = TextBlob(message).sentiment
        response_vec = TextBlob(response).sentiment
        return 1 - abs(message_vec.polarity - response_vec.polarity)

    def analyze_complexity(self, text):
        # Implement complexity analysis
        sentences = TextBlob(text).sentences
        if not sentences:
            return 0
        return min(1, len(sentences) / 5)  # Normalize to 0-1 range

    def check_understanding_indicators(self, message, response):
        # Implement understanding indicator checks
        indicators = ['because', 'why', 'how', 'explain', 'understand']
        score = sum(1 for indicator in indicators if indicator in response.lower())
        return min(1, score / len(indicators))

    def calculate_originality(self, text):
        # Implement originality calculation
        words = word_tokenize(text.lower())
        unique_words = set(words)
        return len(unique_words) / len(words) if words else 0

    def analyze_language_richness(self, text):
        # Implement language richness analysis
        blob = TextBlob(text)
        return min(1, len(blob.words) / 50)  # Normalize to 0-1 range

    def check_imagination(self, text):
        # Implement imagination check
        imagination_indicators = ['imagine', 'pretend', 'what if', 'magic', 'fantasy']
        score = sum(1 for indicator in imagination_indicators if indicator in text.lower())
        return min(1, score / len(imagination_indicators))

    def calculate_retention_rate(self, progress_data):
        # Implement retention rate calculation
        if not progress_data:
            return 0
        return sum(1 for p in progress_data if p.value > 0) / len(progress_data)

    def calculate_trend(self, data):
        # Implement trend calculation
        if len(data) < 2:
            return 'stable'
        values = [d.value for d in data]
        slope = np.polyfit(range(len(values)), values, 1)[0]
        return 'increasing' if slope > 0.1 else 'decreasing' if slope < -0.1 else 'stable'

    def extract_topics(self, text):
        # Implement topic extraction
        blob = TextBlob(text)
        return [word for word, tag in blob.tags if tag.startswith(('NN', 'VB'))]

    def identify_trending_topics(self, topic_counter):
        # Implement trending topic identification
        return dict(topic_counter.most_common(3))

    def generate_vocabulary_recommendations(self, progress_data):
        # Implement vocabulary recommendations
        return {
            'focus_areas': ['nouns', 'verbs', 'adjectives'],
            'learning_strategies': ['contextual learning', 'repetition', 'visual aids']
        }

    def generate_interest_recommendations(self, topic_counter):
        # Implement interest recommendations
        return {
            'explore_topics': list(topic_counter.keys())[:3],
            'diversify_interests': ['science', 'art', 'history']
        }

    def generate_sleep_recommendations(self, session_times):
        # Implement sleep recommendations
        return {
            'optimal_bedtime': '20:00',
            'consistency_tips': ['Set regular bedtime', 'Limit screen time', 'Create bedtime routine']
        }

    def calculate_average_time(self, times):
        # Implement average time calculation
        if not times:
            return None
        return sum(t.hour * 60 + t.minute for t in times) / len(times)

    def calculate_consistency(self, times):
        # Implement consistency calculation
        if len(times) < 2:
            return 0
        intervals = [abs((t2 - t1).total_seconds() / 3600) for t1, t2 in zip(times[:-1], times[1:])]
        return 1 - (np.std(intervals) / 24) if intervals else 0

    def count_late_night_sessions(self, times):
        # Implement late night session counting
        return sum(1 for t in times if t.hour >= 22 or t.hour <= 4)

    def get_response(self, message, child_id, child_age, context, available_stories):
        """Get a response from the model with safety checks"""
        system_prompt = self.get_system_prompt(child_id, child_age, context, available_stories)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        response = ollama.chat(model=self.model, messages=messages)
        bot_reply = response['message']['content']
        
        # Safety checks
        if not self.is_appropriate(bot_reply):
            bot_reply = "I'm here to chat and share fun stories! What would you like to talk about? 😊"
        
        # Format the response
        formatted_response = self.format_response(bot_reply, child_age)
        
        # Track learning progress
        self.track_learning_progress(child_id, message, formatted_response)
        
        # Generate insights periodically
        if random.random() < 0.1:  # 10% chance to generate insights
            self.generate_insights(child_id)
        
        return formatted_response 