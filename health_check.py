import requests

# API endpoint
url = "http://localhost:8000/health"

# Make the request
try:
    response = requests.get(url)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        # Get the response data
        data = response.json()
        
        # Print the response in a formatted way
        print("\nHealth Check Response:")
        print("---------------------")
        print(f"Status: {data['status']}")
        print(f"Service: {data['service']}")
        print(f"Database: {data['database']}")
        print(f"OpenRouter: {data['openrouter']}")
    else:
        print(f"Error response: {response.text}")
    
except requests.exceptions.RequestException as e:
    print(f"Error making request: {e}") 