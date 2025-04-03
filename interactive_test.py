import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def register_and_login():
    print("\n=== Registration and Login ===")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    
    # Register
    print("\nRegistering...")
    response = requests.post(
        f'{BASE_URL}/register',
        json={'email': email, 'password': password}
    )
    print(f"Registration Response: {response.json()}")
    
    # Login
    print("\nLogging in...")
    response = requests.post(
        f'{BASE_URL}/login',
        json={'email': email, 'password': password}
    )
    print(f"Login Response: {response.json()}")
    
    return response.json().get('parent_id')

def create_child_profile(parent_id):
    print("\n=== Create Child Profile ===")
    name = input("Enter child's name: ")
    age = int(input("Enter child's age (4-12): "))
    
    print("\nSelect interests (y/n):")
    interests = {
        'space': input("Space? ").lower() == 'y',
        'animals': input("Animals? ").lower() == 'y',
        'science': input("Science? ").lower() == 'y'
    }
    
    response = requests.post(
        f'{BASE_URL}/child/create',
        json={
            'name': name,
            'age': age,
            'preferences': interests
        }
    )
    print(f"Child Creation Response: {response.json()}")
    
    return response.json().get('child_id')

def chat_with_bot(child_id):
    print("\n=== Chat with StoryPals ===")
    print("Type 'quit' to exit, 'sessions' to check session status")
    
    while True:
        message = input("\nYou: ")
        
        if message.lower() == 'quit':
            break
        elif message.lower() == 'sessions':
            response = requests.get(f'{BASE_URL}/sessions/{child_id}')
            print("\nSession Status:")
            print(json.dumps(response.json(), indent=2))
            continue
        
        response = requests.post(
            f'{BASE_URL}/chat',
            json={
                'message': message,
                'child_id': child_id
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nBot: {data['response']}")
            print(f"Time remaining: {data['time_remaining']}")
        else:
            print(f"\nError: {response.json().get('error', 'Unknown error')}")

def main():
    print("🚀 Welcome to StoryPals Interactive Test!")
    
    # Register and login
    parent_id = register_and_login()
    if not parent_id:
        print("❌ Registration/Login failed")
        return
    
    # Create child profile
    child_id = create_child_profile(parent_id)
    if not child_id:
        print("❌ Child profile creation failed")
        return
    
    # Start chat
    chat_with_bot(child_id)
    
    print("\n👋 Thank you for testing StoryPals!")

if __name__ == "__main__":
    main() 