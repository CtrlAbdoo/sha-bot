#!/usr/bin/env python
"""
Test script for the SHA-Bot API
"""
import requests
import json
import sys

def test_api(query, port=8000):
    """Send a test query to the SHA-Bot API"""
    url = f"http://localhost:{port}/chat"
    
    payload = {
        "message": query,
        "model": "gpt-4.1-mini",
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            print(f"\nQuery: {query}")
            print("-" * 80)
            print(f"Response: {data['response']}")
            print("-" * 80)
            print(f"Model: {data['model']}")
            print(f"Tokens used: {data['tokens_used']}")
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Get the query from command line arguments or use default queries
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        test_api(query)
    else:
        # Test with some sample queries
        test_queries = [
            "Tell me about El-Shorouk Academy",
            "What courses are offered in the Computer Science department?",
            "ما هي مواد الفرقة الثانية في قسم علم الحاسب؟",
            "Tell me about the registration process at El-Shorouk Academy",
            "How many students are enrolled in the academy?"
        ]
        
        for query in test_queries:
            success = test_api(query)
            if not success:
                break
            print("\n" + "=" * 80 + "\n")