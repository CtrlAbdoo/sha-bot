# SHA-Bot - Advanced AI Assistant with MongoDB Integration

SHA-Bot is an intelligent chatbot that leverages OpenRouter's API and MongoDB data to provide comprehensive responses on any topic stored in your MongoDB Cluster0 database. It uses a simulated fine-tuning approach to provide fast, accurate answers in both Arabic and English.

## Features

- 🧠 Uses ALL data from MongoDB Cluster0 to train the model
- 🚀 Multiple AI model support through OpenRouter (GPT-4, Claude-3, Mixtral, etc.)
- 🔍 Simulated fine-tuning for faster, more accurate responses
- 🌐 Multi-language support (Arabic and English)
- 📚 Semantic matching to find relevant information
- 🔄 Fallback to OpenRouter's GPT-3.5-Turbo for unfamiliar questions
- 📊 Basic token usage analytics
- 🔌 Easy integration with web and mobile applications

## Project Structure

```
sha-bot/
│
├── app/               # Core application code
│   ├── __init__.py    # Package initialization
│   ├── api.py         # Standard API routes
│   ├── config.py      # Configuration settings
│   ├── database.py    # MongoDB database handling
│   ├── finetuned_api.py        # Fine-tuned API implementation
│   ├── document_processor.py   # Document content extraction
│   ├── models.py      # Pydantic models
│   ├── openrouter_client.py    # OpenRouter API client
│   └── response_generator.py   # Response generation
│
├── bin/               # Executable scripts
│   ├── run_simulation.bat      # Windows script to run simulation
│   ├── start_api.bat           # Windows API starter
│   ├── start_api.sh            # Unix API starter
│   └── start_finetuned_api.bat # Windows fine-tuned API starter
│
├── data/              # Data files
│   ├── finetuned_simulation.json  # Simulated fine-tuning data
│   ├── test_training_data.jsonl   # Test training data
│   └── training_data.jsonl        # Training data
│
├── docs/              # Documentation
│   ├── DOCUMENT_GUIDE.md          # Document management guide
│   ├── FINE_TUNING_README.md      # Fine-tuning documentation
│   ├── flutter_integration_guide.md # Mobile integration
│   ├── GITHUB_README.md           # GitHub documentation
│   ├── QUICK_FIX_GUIDE.md         # Troubleshooting guide
│   ├── README.md                  # Original documentation
│   └── REFACTORING_SUMMARY.md     # Refactoring notes
│
├── logs/              # Log files
│   ├── chatbot.log    # Main application logs
│   ├── finetune.log   # Fine-tuning logs
│   └── test_extract.log # Test extraction logs
│
├── scripts/           # Utility scripts
│   ├── add_document.py          # Add documents to MongoDB
│   ├── finetune_model.py        # Fine-tuning script
│   ├── health_check.py          # API health check
│   ├── list_models.py           # List available models
│   ├── setup_api_key.py         # API key setup
│   └── verify_app.py            # Verify application setup
│
├── tests/             # Test suite
│   ├── __init__.py    # Test package initialization
│   ├── run_simulation_test.py   # Simulation testing
│   ├── test_api.py    # API tests
│   ├── test_extract_training_data.py # Data extraction tests
│   ├── test_finetuned.py        # Fine-tuned model tests
│   └── test_openrouter.py       # OpenRouter client tests
│
├── .env               # Environment variables
├── .gitattributes     # Git attributes
├── .gitignore         # Git ignore patterns
└── main.py            # Main application entry point
```

## Quick Start

### Prerequisites

- Python 3.8 or higher
- MongoDB Atlas account with data in Cluster0 (or local MongoDB)
- OpenRouter API key from [openrouter.ai](https://openrouter.ai/keys)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sha-bot.git
   cd sha-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your API key:
   ```bash
   python scripts/setup_api_key.py
   ```

4. Generate the simulated fine-tuning data from your MongoDB:
   ```bash
   python main.py --train
   ```

5. Check the status of your simulation data:
   ```bash
   python main.py --status
   ```

6. Run the application:
   ```bash
   python main.py --run
   ```

The API will be available at `http://localhost:8000` with documentation at `/docs`.

## Available Commands

```bash
# Check status of simulation data
python main.py --status

# Train the model with all MongoDB data
python main.py --train

# Run the API server
python main.py --run

# Run in standard mode (no fine-tuning)
python main.py --run --mode standard

# Run on a different port
python main.py --run --port 8080
```

## How It Works

SHA-Bot uses a "simulated fine-tuning" approach that:

1. **Extracts ALL data from your MongoDB Cluster0**
2. **Generates diverse training examples** from the data
3. **Creates a lookup dictionary** for fast responses
4. **Uses advanced semantic matching** to find the best response
5. **Falls back to OpenRouter's GPT-3.5-Turbo** when needed

This approach gives you the benefits of a fine-tuned model without requiring OpenAI API keys or paying for dedicated fine-tuning.

## Deployment to Render.com

SHA-Bot is ready to be deployed to Render.com for creating an online API service:

1. **Fork or push this repository to your GitHub account**

2. **On Render.com dashboard:**
   - Click "New" and select "Web Service"
   - Connect your GitHub account and select this repository
   - Render will detect the `render.yaml` configuration automatically

3. **Configure environment variables:**
   - Set `OPENROUTER_API_KEY` with your OpenRouter API key
   - Set `MONGODB_URI` with your MongoDB connection string
   - Optionally customize `ALLOWED_ORIGINS` for CORS settings

4. **Deploy the service:**
   - Click "Create Web Service"
   - Render will automatically deploy your application
   - The API will be available at your Render URL (e.g., `https://sha-bot-api.onrender.com`)

5. **Upload your trained data:**
   - After the service is deployed, you need to upload your `data/finetuned_simulation.json` file
   - Use the Render disk file system or configure cloud storage

6. **Test your deployment:**
   - Visit `https://your-render-app.onrender.com/docs` to access the API docs
   - Test endpoints to verify everything is working

The API will be accessible through your Render URL, allowing other developers to integrate it into their applications.

## Development

### Running Tests

```bash
pytest tests/
```

### Extending the System

To add new data sources:
1. Add your documents to MongoDB
2. Run `python main.py --train` to update the simulation data
3. Restart the server with `python main.py --run`

## License

MIT License

## Acknowledgments

- OpenRouter for providing access to multiple LLM models
- FastAPI for the powerful API framework
- MongoDB for document storage 