from app import app
from story_manager import StoryManager

def populate_stories():
    with app.app_context():
        # Space stories
        StoryManager.add_story(
            title="The Space Adventure",
            content="Once upon a time, there was a brave little astronaut named Luna. She loved exploring the stars and planets. One day, she discovered a friendly alien who taught her about the wonders of space! 🌟",
            category="space",
            age_range="7-9"
        )

        # Animal stories
        StoryManager.add_story(
            title="The Friendly Forest",
            content="In a magical forest, there lived a wise owl named Oliver. He helped all the forest animals learn about friendship and sharing. 🦉",
            category="animals",
            age_range="4-6"
        )

        # Educational stories
        StoryManager.add_story(
            title="The Math Adventure",
            content="Meet Max, a curious robot who loved solving puzzles. He helped his friends learn about numbers and shapes in a fun way! 🤖",
            category="educational",
            age_range="7-9"
        )

        print("✅ Sample stories added to the database!")

if __name__ == "__main__":
    print("🚀 Populating database with sample stories...")
    populate_stories() 