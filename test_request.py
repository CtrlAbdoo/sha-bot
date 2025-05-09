import requests
import json

# API endpoint
url = "http://localhost:8000/chat"

# Request payload
payload = {
    "message": "Based on the documents, please provide: 1) The structure of the Computer Science curriculum (categories of courses), AND 2) Any specific course names or codes that are explicitly mentioned in the documents. List as many specific course titles as you can find. RESPOND IN ENGLISH ONLY.",
    "model": "gpt-3.5",
    "max_tokens": 1200,
    "temperature": 0.2
}

# Make the request
try:
    response = requests.post(url, json=payload)
    response.raise_for_status()  # Raise an exception for HTTP errors
    
    # Get the response data
    data = response.json()
    
    # Print the response in a formatted way
    print("\nResponse from API:")
    print("------------------")
    print(f"Response text: {data['response']}")
    print(f"Model used: {data['model']}")
    print(f"Tokens used: {data['tokens_used']}")
    print(f"Conversation ID: {data['conversation_id']}")
    
except requests.exceptions.RequestException as e:
    print(f"Error making request: {e}")
except json.JSONDecodeError:
    print(f"Error decoding JSON response: {response.text}") 