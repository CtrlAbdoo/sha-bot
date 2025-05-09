#!/usr/bin/env python
"""
Test script for the fine-tuned SHA-Bot API.
This script sends test queries to the fine-tuned API and compares 
responses with the original document-retrieval approach.
"""
import requests
import json
import time
from colorama import Fore, Style, init

# Initialize colorama for colored output
init()

# API endpoints
FINETUNED_URL = "http://localhost:8000/chat"  # Fine-tuned API
ORIGINAL_URL = "http://localhost:8001/chat"   # Original API (if running on different port)

# Test queries in both Arabic and English
TEST_QUERIES = [
    # Arabic queries
    "ما هي مواد الفرقة الأولى؟",
    "عايز اعرف مواد الفرقة الثانية",
    "مواد السنة الثالثة",
    "المقررات الدراسية للفرقة الرابعة",
    # English queries
    "What are the first year courses?",
    "Show me the second year subjects",
    "List the courses for third year",
    "What are the fourth year courses?"
]

def test_api(url, query, model="fine-tuned-course-assistant"):
    """Test the API with a given query"""
    payload = {
        "message": query,
        "model": model,
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "response": data["response"],
                "tokens_used": data.get("tokens_used", "N/A"),
                "response_time": response_time
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}",
                "response_time": response_time
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response_time": 0
        }

def print_result(query, result, api_type):
    """Print the test result in a formatted way"""
    print(f"\n{Fore.CYAN}==== {api_type} API Response ===={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Query:{Style.RESET_ALL} {query}")
    
    if result["success"]:
        print(f"{Fore.GREEN}Success!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Response:{Style.RESET_ALL} {result['response']}")
        print(f"{Fore.YELLOW}Tokens used:{Style.RESET_ALL} {result['tokens_used']}")
        print(f"{Fore.YELLOW}Response time:{Style.RESET_ALL} {result['response_time']:.2f} seconds")
    else:
        print(f"{Fore.RED}Error!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Error message:{Style.RESET_ALL} {result['error']}")
        print(f"{Fore.YELLOW}Response time:{Style.RESET_ALL} {result['response_time']:.2f} seconds")

def compare_apis():
    """Compare the fine-tuned API with the original API"""
    print(f"{Fore.CYAN}============================================{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  SHA-Bot API Comparison Test{Style.RESET_ALL}")
    print(f"{Fore.CYAN}============================================{Style.RESET_ALL}")
    
    # Check if the fine-tuned API is running
    try:
        requests.get(FINETUNED_URL.replace("/chat", "/health"))
        finetuned_available = True
    except:
        finetuned_available = False
        print(f"{Fore.RED}Fine-tuned API not available at {FINETUNED_URL}{Style.RESET_ALL}")
    
    # Check if the original API is running
    try:
        requests.get(ORIGINAL_URL.replace("/chat", "/health"))
        original_available = True
    except:
        original_available = False
        print(f"{Fore.RED}Original API not available at {ORIGINAL_URL}{Style.RESET_ALL}")
    
    if not finetuned_available and not original_available:
        print(f"{Fore.RED}No APIs available for testing. Please start at least one API server.{Style.RESET_ALL}")
        return
    
    # Run tests for each query
    for i, query in enumerate(TEST_QUERIES):
        print(f"\n{Fore.CYAN}============ Test {i+1}/{len(TEST_QUERIES)} ============{Style.RESET_ALL}")
        
        # Test fine-tuned API
        if finetuned_available:
            finetuned_result = test_api(FINETUNED_URL, query)
            print_result(query, finetuned_result, "Fine-tuned")
        
        # Test original API if available
        if original_available:
            original_result = test_api(ORIGINAL_URL, query, "gpt-3.5")
            print_result(query, original_result, "Original")
        
        print(f"{Fore.CYAN}======================================={Style.RESET_ALL}")

if __name__ == "__main__":
    compare_apis() 