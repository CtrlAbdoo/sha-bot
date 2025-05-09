"""
Verification script for the Chatbot API.

This script performs basic verification of the application structure and configuration.
"""
import os
import sys
import importlib.util
from dotenv import load_dotenv

# Set up formatting
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
END = "\033[0m"

def print_success(message):
    print(f"{GREEN}✓ {message}{END}")

def print_warning(message):
    print(f"{YELLOW}⚠ {message}{END}")

def print_error(message):
    print(f"{RED}✗ {message}{END}")

def print_header(message):
    print(f"\n{BOLD}{message}{END}")

def check_module_exists(module_path):
    """Check if a Python module exists at the given path."""
    return importlib.util.find_spec(module_path) is not None

def verify_app_structure():
    """Verify the application structure."""
    print_header("Verifying Application Structure")
    
    # Check app structure
    required_modules = [
        "app", "app.api", "app.config", "app.database", 
        "app.document_processor", "app.models", "app.openrouter_client"
    ]
    
    all_exist = True
    for module in required_modules:
        if check_module_exists(module):
            print_success(f"Module '{module}' found")
        else:
            print_error(f"Module '{module}' not found")
            all_exist = False
    
    return all_exist

def verify_test_structure():
    """Verify the test structure."""
    print_header("Verifying Test Structure")
    
    # Check test structure
    required_test_modules = [
        "tests", "tests.test_api", "tests.test_openrouter"
    ]
    
    all_exist = True
    for module in required_test_modules:
        if check_module_exists(module):
            print_success(f"Test module '{module}' found")
        else:
            print_error(f"Test module '{module}' not found")
            all_exist = False
    
    return all_exist

def verify_api_key():
    """Verify the OpenRouter API key configuration."""
    print_header("Verifying API Key Configuration")
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key is set
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print_error("OpenRouter API key not found in environment variables")
        print("Run 'python setup_api_key.py' to configure your API key.")
        return False
    
    # Check API key format
    if not api_key.startswith("sk-or-"):
        print_warning(f"API key format may be incorrect (doesn't start with 'sk-or-')")
        print(f"Current key: {api_key[:4]}...{api_key[-4:]} (length: {len(api_key)})")
    else:
        print_success(f"API key found: {api_key[:4]}...{api_key[-4:]} (length: {len(api_key)})")
    
    return True

def verify_dependencies():
    """Verify that required dependencies are installed."""
    print_header("Verifying Dependencies")
    
    required_packages = [
        "fastapi", "uvicorn", "pydantic", "python-dotenv", 
        "pymongo", "loguru", "aiohttp", "pytest"
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            importlib.import_module(package)
            print_success(f"Package '{package}' is installed")
        except ImportError:
            print_error(f"Package '{package}' is not installed")
            all_installed = False
    
    if not all_installed:
        print("Run 'pip install -r requirements.txt' to install missing dependencies.")
    
    return all_installed

def main():
    """Main function."""
    print(f"{BOLD}Chatbot API Verification{END}")
    print("This script verifies the application structure and configuration.")
    print()
    
    # Run verification steps
    structure_ok = verify_app_structure()
    tests_ok = verify_test_structure()
    key_ok = verify_api_key()
    deps_ok = verify_dependencies()
    
    # Print summary
    print_header("Verification Summary")
    if structure_ok:
        print_success("Application structure: OK")
    else:
        print_error("Application structure: ISSUES FOUND")
    
    if tests_ok:
        print_success("Test structure: OK")
    else:
        print_error("Test structure: ISSUES FOUND")
    
    if key_ok:
        print_success("API key configuration: OK")
    else:
        print_error("API key configuration: ISSUES FOUND")
    
    if deps_ok:
        print_success("Dependencies: OK")
    else:
        print_error("Dependencies: ISSUES FOUND")
    
    # Overall status
    print()
    if structure_ok and tests_ok and key_ok and deps_ok:
        print(f"{GREEN}{BOLD}All checks passed. The application is ready to run.{END}")
        print(f"\nStart the API with: {BOLD}python chatbot_api.py{END}")
    else:
        print(f"{YELLOW}{BOLD}Issues were found. Please fix them before running the application.{END}")
    
    return 0 if (structure_ok and tests_ok and key_ok and deps_ok) else 1

if __name__ == "__main__":
    sys.exit(main()) 