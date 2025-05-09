import requests

# API endpoint
url = "http://localhost:8000/models"

# Make the request
try:
    response = requests.get(url)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        # Get the response data
        data = response.json()
        
        # Print the available models
        print("\nAvailable Models:")
        print("----------------")
        for model_name, model_info in data['models'].items():
            print(f"{model_name}:")
            print(f"  - ID: {model_info['id']}")
            print(f"  - Context Length: {model_info['context_length']}")
            print(f"  - Description: {model_info['description']}")
            print()
    else:
        print(f"Error response: {response.text}")
    
except requests.exceptions.RequestException as e:
    print(f"Error making request: {e}") 