import ollama
from datetime import datetime, timedelta

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
            8. Ask simple questions to engage the child""",
            
            "7-9": """You are StoryPals, a friendly AI companion for children aged 7-9.
            Guidelines:
            1. Be engaging and supportive
            2. Use age-appropriate vocabulary
            3. Be encouraging and positive
            4. Use some emojis for fun
            5. Keep responses clear and concise
            6. Share stories when the child is interested
            7. Ask thought-provoking questions
            8. Be patient and understanding""",
            
            "10-12": """You are StoryPals, a friendly AI companion for pre-teens aged 10-12.
            Guidelines:
            1. Be engaging and supportive
            2. Use age-appropriate vocabulary
            3. Be encouraging and positive
            4. Use emojis sparingly
            5. Keep responses clear and concise
            6. Share stories when the child is interested
            7. Ask thought-provoking questions
            8. Be patient and understanding"""
        }

    def get_system_prompt(self, child_age, context, available_stories):
        """Generate an age-appropriate system prompt"""
        # Determine age group
        if 4 <= child_age <= 6:
            age_group = "4-6"
        elif 7 <= child_age <= 9:
            age_group = "7-9"
        else:
            age_group = "10-12"
        
        base_prompt = self.age_appropriate_prompts[age_group]
        
        # Add context
        prompt = f"""{base_prompt}
        
        Previous conversation: {context}
        
        Remember:
        1. Never share personal information
        2. Never make promises
        3. Never give medical advice
        4. Never share inappropriate content
        5. Always maintain a safe, friendly environment
        6. Be natural and conversational
        7. Share stories only when appropriate
        8. Focus on engaging with the child"""
        
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

    def get_response(self, message, child_age, context, available_stories):
        """Get a response from the model with safety checks"""
        system_prompt = self.get_system_prompt(child_age, context, available_stories)
        
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
        return self.format_response(bot_reply, child_age) 