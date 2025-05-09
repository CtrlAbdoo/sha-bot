#!/bin/bash
# OpenRouter Chatbot API Launcher for Unix-like systems

echo "===== OpenRouter Chatbot API Launcher ====="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not found in your PATH."
    echo "Please install Python 3 and make sure it's added to your PATH."
    exit 1
fi

# Check for required directories
if [ ! -d "app" ]; then
    echo "Creating app directory structure..."
    mkdir -p app
    mkdir -p logs
    mkdir -p tests
fi

# Check if required packages are installed
if ! python3 -c "import fastapi, uvicorn, dotenv, pymongo, loguru" &> /dev/null; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install requirements."
        echo "Please run: pip3 install -r requirements.txt"
        exit 1
    fi
fi

# Check for .env file and API key
if [ ! -f ".env" ]; then
    echo "No .env file found."
    echo "Running API key setup..."
    python3 setup_api_key.py
    if [ $? -ne 0 ]; then
        echo "Failed to set up API key."
        exit 1
    fi
else
    # Check for API key in .env file
    if ! grep -q "OPENROUTER_API_KEY" .env; then
        echo "No API key found in .env file."
        echo "Running API key setup..."
        python3 setup_api_key.py
        if [ $? -ne 0 ]; then
            echo "Failed to set up API key."
            exit 1
        fi
    fi
fi

# Make script executable
chmod +x start_api.sh

# Start the API server
echo
echo "Starting the API server..."
echo "Press Ctrl+C to stop the server."
echo

python3 chatbot_api.py 