from typing import Dict, List, Any
import random
import json

class LearningActivityGenerator:
    @staticmethod
    def generate_comprehension_questions(story_content: str) -> List[Dict[str, Any]]:
        """Generate reading comprehension questions based on story content."""
        # This is a simplified version. In a real implementation, you would use NLP
        # to generate more sophisticated questions.
        questions = [
            {
                "type": "multiple_choice",
                "question": "What was the main character's name?",
                "options": ["Luna", "Leo", "Whiskers", "Melody"],
                "correct_answer": 0
            },
            {
                "type": "true_false",
                "question": "The story took place in space.",
                "correct_answer": True
            },
            {
                "type": "short_answer",
                "question": "What was the main problem in the story?",
                "correct_answer": "The rocket was running out of fuel"
            }
        ]
        return questions

    @staticmethod
    def generate_vocabulary_quiz(words: List[str]) -> List[Dict[str, Any]]:
        """Generate vocabulary quiz questions."""
        quiz = []
        for word in words:
            quiz.append({
                "type": "vocabulary",
                "word": word,
                "question": f"What is the meaning of '{word}'?",
                "options": [
                    "Option 1",
                    "Option 2",
                    "Option 3",
                    "Option 4"
                ],
                "correct_answer": 0
            })
        return quiz

    @staticmethod
    def generate_puzzle(story_content: str) -> Dict[str, Any]:
        """Generate a puzzle based on story content."""
        return {
            "type": "word_search",
            "title": "Find the Story Words",
            "grid_size": 10,
            "words": ["rocket", "moon", "stars", "space", "adventure"],
            "grid": [
                ["r", "o", "c", "k", "e", "t", "a", "b", "c", "d"],
                ["e", "f", "g", "h", "i", "j", "k", "l", "m", "n"],
                ["o", "p", "q", "r", "s", "t", "u", "v", "w", "x"],
                ["y", "z", "a", "b", "c", "d", "e", "f", "g", "h"],
                ["i", "j", "k", "l", "m", "n", "o", "p", "q", "r"],
                ["s", "t", "u", "v", "w", "x", "y", "z", "a", "b"],
                ["c", "d", "e", "f", "g", "h", "i", "j", "k", "l"],
                ["m", "n", "o", "p", "q", "r", "s", "t", "u", "v"],
                ["w", "x", "y", "z", "a", "b", "c", "d", "e", "f"],
                ["g", "h", "i", "j", "k", "l", "m", "n", "o", "p"]
            ]
        }

    @staticmethod
    def generate_memory_game(words: List[str]) -> Dict[str, Any]:
        """Generate a memory matching game with vocabulary words."""
        pairs = []
        for word in words:
            pairs.append({
                "word": word,
                "definition": f"Definition of {word}",
                "image_url": f"/api/placeholder/100/100?text={word}"
            })
        
        # Duplicate pairs for matching
        cards = pairs * 2
        random.shuffle(cards)
        
        return {
            "type": "memory_game",
            "title": "Match the Words",
            "cards": cards
        }

    @staticmethod
    def generate_story_sequencing(story_content: str) -> Dict[str, Any]:
        """Generate a story sequencing activity."""
        events = [
            "The rocket launched into space",
            "They saw the moon getting closer",
            "They landed on the moon",
            "They explored the surface",
            "They returned to Earth"
        ]
        random.shuffle(events)
        
        return {
            "type": "sequencing",
            "title": "Put the Story in Order",
            "events": events,
            "correct_order": [0, 1, 2, 3, 4]
        }

class ActivityManager:
    def __init__(self):
        self.generator = LearningActivityGenerator()

    def create_activity(self, activity_type: str, story_content: str = None, words: List[str] = None) -> Dict[str, Any]:
        """Create a new learning activity based on type and content."""
        if activity_type == "comprehension":
            return self.generator.generate_comprehension_questions(story_content)
        elif activity_type == "vocabulary":
            return self.generator.generate_vocabulary_quiz(words)
        elif activity_type == "puzzle":
            return self.generator.generate_puzzle(story_content)
        elif activity_type == "memory_game":
            return self.generator.generate_memory_game(words)
        elif activity_type == "sequencing":
            return self.generator.generate_story_sequencing(story_content)
        else:
            raise ValueError(f"Unknown activity type: {activity_type}")

    def validate_answer(self, activity: Dict[str, Any], answer: Any) -> bool:
        """Validate an answer for an activity."""
        if activity["type"] == "multiple_choice":
            return answer == activity["correct_answer"]
        elif activity["type"] == "true_false":
            return answer == activity["correct_answer"]
        elif activity["type"] == "short_answer":
            return answer.lower() == activity["correct_answer"].lower()
        elif activity["type"] == "sequencing":
            return answer == activity["correct_order"]
        else:
            raise ValueError(f"Unknown activity type: {activity['type']}")

# Example usage:
if __name__ == "__main__":
    manager = ActivityManager()
    
    # Example story content
    story = "Once upon a time, Luna the Star Fairy went on a space adventure..."
    
    # Create different types of activities
    comprehension = manager.create_activity("comprehension", story)
    vocabulary = manager.create_activity("vocabulary", words=["rocket", "moon", "stars"])
    puzzle = manager.create_activity("puzzle", story)
    memory_game = manager.create_activity("memory_game", words=["rocket", "moon", "stars"])
    sequencing = manager.create_activity("sequencing", story)
    
    # Print examples
    print("Comprehension Questions:")
    print(json.dumps(comprehension, indent=2))
    
    print("\nVocabulary Quiz:")
    print(json.dumps(vocabulary, indent=2))
    
    print("\nPuzzle:")
    print(json.dumps(puzzle, indent=2))
    
    print("\nMemory Game:")
    print(json.dumps(memory_game, indent=2))
    
    print("\nStory Sequencing:")
    print(json.dumps(sequencing, indent=2)) 