# SHA Bot - Course Information Chatbot

A chatbot API built with FastAPI that provides information about university courses using document-based knowledge and OpenRouter API integration.

## Features

- Document processing from text files
- MongoDB integration for storing conversation history
- OpenRouter API integration for AI responses
- RESTful API with FastAPI
- Health check endpoints
- Model selection support

## Requirements

- Python 3.10+
- MongoDB (optional)
- OpenRouter API key

## Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/sha-bot.git
cd sha-bot
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up your API key
```bash
python setup_api_key.py
```

4. Prepare your document files
   - Create text files with course information
   - Update the document paths in app/config.py

## Running the API

```bash
python chatbot_api.py
```

Or use the provided batch file:

```bash
start_api.bat
```

## Testing

Run tests with:

```bash
python test_course_queries.py
```

Or test the API with:

```bash
python simple_test.py
```

## API Endpoints

- POST `/chat` - Send a message to the chatbot
- GET `/models` - List available models
- GET `/health` - Check API health

## License

MIT 