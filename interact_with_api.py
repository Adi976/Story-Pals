import requests
import json

class StoryPalsAPI:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.child_id = None

    def update_profile(self, name, age, preferences):
        """Update or create a child profile"""
        url = f"{self.base_url}/child/profile"
        data = {
            "name": name,
            "age": age,
            "preferences": preferences
        }
        response = self.session.put(url, json=data)
        print(f"Profile Update Response: {response.text}")
        return response.json()

    def chat(self, message):
        """Send a message to StoryPals"""
        url = f"{self.base_url}/chat"
        data = {"message": message}
        response = self.session.post(url, json=data)
        print(f"Chat Response: {response.text}")
        return response.json()

    def get_stories(self):
        """Get available stories"""
        url = f"{self.base_url}/stories"
        response = self.session.get(url)
        print(f"Stories Response: {response.text}")
        return response.json()

def main():
    # Create API client
    api = StoryPalsAPI()
    
    # Example 1: Create a child profile
    print("\n1. Creating child profile...")
    profile = api.update_profile(
        name="Alex",
        age=8,
        preferences={
            "favorite_topics": ["space", "animals"],
            "favorite_characters": ["astronauts", "robots"]
        }
    )
    
    # Example 2: Chat with StoryPals
    print("\n2. Starting a chat...")
    chat_responses = [
        "Tell me a story about space!",
        "What did Luna learn from the alien?",
        "Can you tell me about the planets?"
    ]
    
    for message in chat_responses:
        print(f"\nSending message: {message}")
        response = api.chat(message)
        print(f"Bot's response: {response.get('response', 'No response')}")
    
    # Example 3: Get available stories
    print("\n3. Getting available stories...")
    stories = api.get_stories()
    print(f"Available stories: {json.dumps(stories, indent=2)}")

if __name__ == "__main__":
    print("🚀 Starting StoryPals API interaction demo...")
    main()
    print("\n✅ Demo completed!") 