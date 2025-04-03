import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def test_registration():
    print("\n1. Testing Registration...")
    response = requests.post(
        f'{BASE_URL}/register',
        json={
            'email': 'test6@example.com',
            'password': 'test123'
        }
    )
    print(f"Registration Response: {response.json()}")
    return response.status_code == 200

def test_login():
    print("\n2. Testing Login...")
    response = requests.post(
        f'{BASE_URL}/login',
        json={
            'email': 'test6@example.com',
            'password': 'test123'
        }
    )
    print(f"Login Response: {response.json()}")
    return response.json().get('parent_id')

def test_child_creation(parent_id):
    print("\n3. Testing Child Profile Creation...")
    response = requests.post(
        f'{BASE_URL}/child/create',
        json={
            'name': 'TestChild',
            'age': 8,
            'preferences': {
                'space': True,
                'animals': True,
                'science': False
            }
        }
    )
    print(f"Child Creation Response: {response.json()}")
    return response.json().get('child_id')

def test_chat(child_id):
    print("\n4. Testing Chat Functionality...")
    
    # Test basic conversation
    print("\nTesting basic conversation:")
    response = requests.post(
        f'{BASE_URL}/chat',
        json={
            'message': 'Hello! Can you tell me a story about space?',
            'child_id': child_id
        }
    )
    print(f"Bot Response: {response.json()['response']}")
    
    # Test story continuity
    print("\nTesting story continuity:")
    response = requests.post(
        f'{BASE_URL}/chat',
        json={
            'message': 'What happens next?',
            'child_id': child_id
        }
    )
    print(f"Bot Response: {response.json()['response']}")
    
    # Test age-appropriate responses
    print("\nTesting age-appropriate responses:")
    response = requests.post(
        f'{BASE_URL}/chat',
        json={
            'message': 'Can you explain quantum physics?',
            'child_id': child_id
        }
    )
    print(f"Bot Response: {response.json()['response']}")
    
    # Test interest-based responses
    print("\nTesting interest-based responses:")
    response = requests.post(
        f'{BASE_URL}/chat',
        json={
            'message': 'Tell me about animals!',
            'child_id': child_id
        }
    )
    print(f"Bot Response: {response.json()['response']}")

def test_session_management(child_id):
    print("\n5. Testing Session Management...")
    response = requests.get(f'{BASE_URL}/sessions/{child_id}')
    print(f"Sessions Response: {response.json()}")

def main():
    print("🚀 Starting StoryPals Chatbot Tests...")
    
    # Test registration
    if not test_registration():
        print("❌ Registration failed")
        return
    
    # Test login
    parent_id = test_login()
    if not parent_id:
        print("❌ Login failed")
        return
    
    # Test child creation
    child_id = test_child_creation(parent_id)
    if not child_id:
        print("❌ Child creation failed")
        return
    
    # Test chat functionality
    test_chat(child_id)
    
    # Test session management
    test_session_management(child_id)
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main() 