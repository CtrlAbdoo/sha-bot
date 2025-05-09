# Advanced Chatbot API

A Python-based chatbot API that utilizes OpenRouter to access various LLM models with custom document data from MongoDB.

## Features

- 🚀 Multiple AI model support (GPT-4, Claude-3, Mixtral, Qwen, GPT-3.5)
- 📚 MongoDB integration for custom document storage
- 🔍 Relevant content extraction from documents
- 🌐 RESTful API with FastAPI
- 🧪 Comprehensive test suite
- 📝 Detailed logging
- 🔒 Secure API key handling
- 📱 Flutter integration support

## Quick Start

### Prerequisites

- Python 3.8 or higher
- MongoDB Atlas account (or local MongoDB)
- OpenRouter API key from [openrouter.ai](https://openrouter.ai/keys)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/chatbot-api.git
   cd chatbot-api
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your API key:
   ```bash
   python setup_api_key.py
   ```

4. Start the API server:
   ```bash
   python main.py
   ```
   
   Or on Windows:
   ```
   start_api.bat
   ```

The API will be available at `http://localhost:8000`.

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Main Endpoints

- `GET /health` - Check API health status
- `GET /models` - List available models
- `POST /chat` - Send a message to the chatbot
- `GET /export-documents` - Export documents for fine-tuning

### Example Chat Request

```json
POST /chat
{
  "message": "ما هي مواد الفرقة الثانية في قسم علم الحاسب؟",
  "model": "gpt-3.5",
  "max_tokens": 500,
  "temperature": 0.7
}
```

## Project Structure

```
├── app/                       # Main application package
│   ├── __init__.py            # Package initialization
│   ├── api.py                 # FastAPI routes and endpoints
│   ├── config.py              # Configuration settings
│   ├── database.py            # MongoDB database handling
│   ├── document_processor.py  # Document content extraction
│   ├── models.py              # Pydantic models for requests/responses
│   └── openrouter_client.py   # OpenRouter API client
├── tests/                     # Test package
│   ├── __init__.py
│   ├── test_api.py            # API endpoint tests
│   └── test_openrouter.py     # OpenRouter client tests
├── logs/                      # Log files
├── .env                       # Environment variables (create with setup_api_key.py)
├── main.py                    # Main application entry point
├── requirements.txt           # Python dependencies
├── setup_api_key.py           # API key setup script
├── start_api.bat              # Windows starter script
└── README.md                  # This file
```

## Configuration

Configuration is handled through environment variables, which can be set in a `.env` file:

- `OPENROUTER_API_KEY` - Your OpenRouter API key
- `DEFAULT_MODEL` - Default model to use (gpt-3.5, gpt-4, claude-3, mixtral, qwen)
- `MONGO_URI` - MongoDB connection string
- `PORT` - Port to run the API server on (default: 8000)
- `LOG_LEVEL` - Logging level (INFO, DEBUG, etc.)

## Mobile Integration

For Flutter integration, see the [flutter_integration_guide.md](flutter_integration_guide.md) file.

## Troubleshooting

If you encounter authentication issues with OpenRouter:

1. Run the test utility:
   ```bash
   python test_env.py
   ```

2. Verify your API key:
   ```bash
   python verify_openrouter_key.py
   ```

3. See [QUICK_FIX_GUIDE.md](QUICK_FIX_GUIDE.md) for common solutions.

## Testing

Run the test suite:

```bash
pytest
```

Or for verbose output:

```bash
pytest -v
```

## License

MIT License

## Acknowledgments

- OpenRouter for providing access to multiple LLM models
- FastAPI for the powerful API framework
- MongoDB for document storage 