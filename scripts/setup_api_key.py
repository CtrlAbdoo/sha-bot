"""
Interactive script to set up OpenRouter API key and other configuration.
"""
import os
import sys
import re
from dotenv import load_dotenv, set_key

# Load existing environment variables
load_dotenv()


# ANSI color codes for better formatting
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {text} ==={Colors.ENDC}")


def print_success(text):
    """Print a success message"""
    print(f"{Colors.GREEN}{text}{Colors.ENDC}")


def print_warning(text):
    """Print a warning message"""
    print(f"{Colors.WARNING}{text}{Colors.ENDC}")


def print_error(text):
    """Print an error message"""
    print(f"{Colors.FAIL}{text}{Colors.ENDC}")


def is_valid_openrouter_key(key):
    """Validate OpenRouter API key format"""
    if not key.strip():
        return False
    
    # OpenRouter keys should start with sk-or-
    if not key.startswith("sk-or-"):
        print_warning("Warning: API key doesn't start with the expected prefix 'sk-or-'")
        print_warning("This may cause authentication failures with the OpenRouter API")
        return True  # Still allow it, just show warning
    
    # Basic length check
    if len(key) < 20:
        return False
    
    return True


def setup_api_key():
    """Set up OpenRouter API key"""
    print_header("OpenRouter API Key Setup")
    print("This script will help you set up your OpenRouter API key.")
    print("Get your API key from: https://openrouter.ai/keys")
    
    # Check if key already exists
    current_key = os.getenv("OPENROUTER_API_KEY")
    if current_key:
        print(f"\nCurrent API key: {current_key[:4]}...{current_key[-4:]} (length: {len(current_key)})")
        change = input("Do you want to change this key? (y/n): ").lower()
        if change != 'y':
            print_success("Keeping existing API key.")
            return
    
    # Get and validate new key
    while True:
        api_key = input("\nEnter your OpenRouter API key: ").strip()
        
        if not api_key:
            print_error("No key entered. Please try again or press Ctrl+C to quit.")
            continue
        
        if is_valid_openrouter_key(api_key):
            break
        else:
            print_error("Invalid API key format. Please check and try again.")
    
    # Save key to .env file
    env_file = ".env"
    
    if not os.path.exists(env_file):
        with open(env_file, "w") as f:
            f.write("# Chatbot API environment variables\n")
    
    set_key(env_file, "OPENROUTER_API_KEY", api_key)
    print_success(f"\nAPI key saved to {env_file}")
    print_success(f"Key: {api_key[:4]}...{api_key[-4:]} (length: {len(api_key)})")


def setup_other_config():
    """Set up other configuration options"""
    print_header("Additional Configuration")
    
    # Ask about default model
    default_model = os.getenv("DEFAULT_MODEL", "gpt-4.1-mini")
    print(f"\nCurrent default model: {default_model}")
    print("Available models: gpt-4.1-mini, gpt-4, claude-3, mixtral, qwen")
    
    change = input("Do you want to change the default model? (y/n): ").lower()
    if change == 'y':
        while True:
            new_model = input("Enter new default model: ").strip()
            valid_models = ["gpt-4.1-mini", "gpt-4", "claude-3", "mixtral", "qwen"]
            if new_model in valid_models:
                set_key(".env", "DEFAULT_MODEL", new_model)
                print_success(f"Default model set to: {new_model}")
                break
            else:
                print_error(f"Invalid model. Please choose from: {', '.join(valid_models)}")


def test_api_key():
    """Test the configured API key"""
    import requests
    
    print_header("Testing API Key")
    
    # Get the API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print_error("No API key found in environment variables.")
        return False
    
    print(f"Testing API key: {api_key[:4]}...{api_key[-4:]}")
    
    # Create headers and minimal payload
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "openai/gpt-4.1-mini",
        "messages": [
            {"role": "user", "content": "Hello, just a quick test."}
        ],
        "max_tokens": 5
    }
    
    try:
        print("Sending test request to OpenRouter API...")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print_success("\nSuccess! API key is working correctly.")
            return True
        else:
            print_error(f"\nError {response.status_code}: {response.text}")
            
            if response.status_code == 401:
                print_error("\nAuthentication failed. Please check your API key.")
            return False
            
    except Exception as e:
        print_error(f"Error making request: {e}")
        return False


def main():
    """Main function to run the setup process"""
    try:
        print_header("Chatbot API Setup")
        print("This wizard will help you configure the Chatbot API with OpenRouter.")
        
        # Set up API key
        setup_api_key()
        
        # Set up other configuration
        setup_other_config()
        
        # Test the API key
        success = test_api_key()
        
        # Final instructions
        print_header("Setup Complete")
        if success:
            print_success("Your chatbot API is now configured and ready to use!")
            print("\nStart the API with:")
            print(f"{Colors.BOLD}python main.py{Colors.ENDC}")
        else:
            print_warning("Setup complete, but API key test failed.")
            print("\nPlease check your API key and try again.")
        
    except KeyboardInterrupt:
        print("\n\nSetup canceled by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()