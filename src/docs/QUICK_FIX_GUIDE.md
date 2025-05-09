# Quick Fix Guide for OpenRouter Authentication Issues

## The Problem
You're seeing a 401 error with message "No auth credentials found" when making requests to OpenRouter.

## Immediate Solution

1. **Check your application configuration**:
   ```
   python verify_app.py
   ```
   This script will check your API key and other configurations.

2. **Get a valid OpenRouter API key**:
   - Go to [OpenRouter Keys Page](https://openrouter.ai/keys)
   - Create a new API key (should start with `sk-or-`)
   - Copy the key

3. **Set up your API key**:
   ```
   python setup_api_key.py
   ```
   This interactive script will guide you through setting up your API key and other configurations.

4. **Start the API with the launcher**:
   ```
   # Windows
   start_api.bat
   
   # Linux/macOS
   python chatbot_api.py
   ```
   This will check for a valid key and install any missing packages.

## Common Issues

### 1. Invalid API Key

**Symptoms:**
- 401 authentication errors
- "No auth credentials found" message

**Solutions:**
- Make sure your API key starts with `sk-or-`
- Check for whitespace or newlines in your API key
- Generate a fresh key from OpenRouter

### 2. Configuration Issues

**Symptoms:**
- Module import errors
- Missing files or directories

**Solutions:**
- Run `verify_app.py` to check your configuration
- Ensure all required packages are installed: `pip install -r requirements.txt`
- Make sure the app directory structure is correct

### 3. MongoDB Connection

**Symptoms:**
- Database connection errors
- Missing document data

**Solutions:**
- Check your MongoDB connection string in .env file
- Ensure you have network access to MongoDB Atlas
- Verify that necessary documents are loaded

## Advanced Troubleshooting

If you continue to have issues:

1. **Check the logs**:
   - Look in the `logs/chatbot.log` file for detailed error messages
   
2. **Run the tests**:
   ```
   pytest
   ```
   
3. **Check specific component**:
   ```
   # Test OpenRouter client only
   pytest tests/test_openrouter.py
   
   # Test API endpoints
   pytest tests/test_api.py
   ```

## Need More Help?

See the full README.md for comprehensive documentation or create an issue in the project repository. 