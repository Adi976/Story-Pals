import json
from datetime import datetime
from models import db, Story

class StoryManager:
    @staticmethod
    def add_story(title, content, category, age_range):
        """Add a new story to the database."""
        story = Story(
            title=title,
            content=content,
            category=category,
            age_range=age_range
        )
        db.session.add(story)
        db.session.commit()
        return story

    @staticmethod
    def get_stories_by_age(age):
        """Get stories appropriate for a specific age group."""
        age_ranges = {
            (0, 3): "0-3",
            (4, 6): "4-6",
            (7, 9): "7-9",
            (10, 12): "10-12"
        }
        
        # Determine appropriate age range
        for (min_age, max_age), range_str in age_ranges.items():
            if min_age <= age <= max_age:
                return Story.query.filter_by(age_range=range_str).all()
        
        return []

    @staticmethod
    def get_stories_by_category(category):
        """Get stories by category."""
        return Story.query.filter_by(category=category).all()

    @staticmethod
    def filter_content(content):
        """Filter inappropriate content and ensure child-friendly language."""
        # Add your content filtering logic here
        # This is a basic example - you should implement more sophisticated filtering
        inappropriate_words = set()  # Add your list of inappropriate words
        filtered_content = content
        
        for word in inappropriate_words:
            filtered_content = filtered_content.replace(word, '*' * len(word))
        
        return filtered_content

    @staticmethod
    def format_story_for_response(story):
        """Format a story for the chatbot response."""
        return {
            "title": story.title,
            "content": story.content,
            "category": story.category,
            "age_range": story.age_range
        }

class ContentModerator:
    @staticmethod
    def is_appropriate(response):
        """Check if the response is appropriate for children."""
        # Add your content moderation logic here
        # This is a basic example - you should implement more sophisticated moderation
        inappropriate_patterns = [
            # Add your patterns here
        ]
        
        for pattern in inappropriate_patterns:
            if pattern in response.lower():
                return False
        
        return True

    @staticmethod
    def format_response(response):
        """Format the response to be more engaging and child-friendly."""
        # Add your response formatting logic here
        # This is a basic example - you should implement more sophisticated formatting
        formatted = response.replace('\n\n', '\n')  # Remove extra newlines
        formatted = formatted.replace('  ', ' ')    # Remove extra spaces
        
        # Add emojis for common emotions
        emotion_mapping = {
            'happy': '😊',
            'sad': '😢',
            'excited': '🎉',
            'surprised': '😮',
            # Add more mappings as needed
        }
        
        for emotion, emoji in emotion_mapping.items():
            if emotion in formatted.lower():
                formatted = formatted.replace(emotion, f"{emotion} {emoji}")
        
        return formatted 