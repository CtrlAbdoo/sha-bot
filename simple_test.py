import requests
import json

# API endpoint
url = "http://localhost:8000/chat"

# Request payload with a simple query using mixtral model
payload = {
    "message": "ما هي مواد الفرقة الثالثة؟",
    "model": "mixtral",
    "max_tokens": 500,
    "temperature": 0.7
}

# Make the request
try:
    response = requests.post(url, json=payload)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        # Get the response data
        data = response.json()
        
        # Print the response in a formatted way
        print("\nResponse from API:")
        print("------------------")
        print(f"Response text: {data['response']}")
        print(f"Model used: {data['model']}")
        print(f"Tokens used: {data['tokens_used']}")
        print(f"Conversation ID: {data['conversation_id']}")
    else:
        print(f"Error response: {response.text}")
    
except requests.exceptions.RequestException as e:
    print(f"Error making request: {e}")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON response: {e}")
    print(f"Raw response: {response.text}") 