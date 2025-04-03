import requests
import json

BASE_URL = 'http://localhost:5000'

def test_endpoints():
    # Test home endpoint
    print("Testing home endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Home response: {response.text}\n")

    # Create a child profile
    print("Creating child profile...")
    child_data = {
        "name": "Alex",
        "age": 8,
        "preferences": {"favorite_topics": ["space", "animals"]}
    }
    response = requests.put(f"{BASE_URL}/child/profile", json=child_data)
    print(f"Profile creation response: {response.text}\n")

    # Test chat endpoint
    print("Testing chat endpoint...")
    chat_data = {"message": "Tell me a story about space!"}
    response = requests.post(f"{BASE_URL}/chat", json=chat_data)
    print(f"Chat response: {response.text}\n")

    # Get available stories
    print("Getting available stories...")
    response = requests.get(f"{BASE_URL}/stories")
    print(f"Stories response: {response.text}\n")

if __name__ == "__main__":
    print("🚀 Starting StoryPals API tests...")
    test_endpoints()
    print("✅ Tests completed!") 