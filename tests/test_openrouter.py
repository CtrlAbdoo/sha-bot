"""
Tests for OpenRouter API functionality.
"""
import os
import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import after loading environment variables
from app.openrouter_client import OpenRouterClient, OpenRouterError


@pytest.mark.asyncio
async def test_check_status():
    """Test OpenRouter status check"""
    client = OpenRouterClient()
    
    # Mock aiohttp.ClientSession.get
    with patch("aiohttp.ClientSession.get") as mock_get:
        # Configure the mock to return a response with a status code of 200
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Call the method under test
        result = await client.check_status()
        
        # Verify the method returns True when the status is 200
        assert result is True
        
        # Verify the method called aiohttp.ClientSession.get with the correct URL
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_check_status_error():
    """Test OpenRouter status check with error"""
    client = OpenRouterClient()
    
    # Mock aiohttp.ClientSession.get
    with patch("aiohttp.ClientSession.get") as mock_get:
        # Configure the mock to raise an exception
        mock_get.return_value.__aenter__.side_effect = Exception("Connection error")
        
        # Call the method under test
        result = await client.check_status()
        
        # Verify the method returns False when an exception is raised
        assert result is False
        
        # Verify the method called aiohttp.ClientSession.get with the correct URL
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_generate_completion():
    """Test generate completion with mocked response"""
    client = OpenRouterClient()
    
    # Define test messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, world!"}
    ]
    
    # Expected response from the API
    expected_response = {
        "id": "mock-id",
        "object": "chat.completion",
        "created": 1677858242,
        "model": "openai/gpt-4.1-mini",
        "usage": {
            "prompt_tokens": 20,
            "completion_tokens": 10,
            "total_tokens": 30
        },
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Hello! How can I assist you today?"
                },
                "index": 0,
                "finish_reason": "stop"
            }
        ]
    }
    
    # Mock aiohttp.ClientSession.post
    with patch("aiohttp.ClientSession.post") as mock_post:
        # Configure the mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = expected_response
        mock_response.text.return_value = "response text"
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Call the method under test
        result = await client.generate_completion(
            messages=messages,
            model_id="openai/gpt-3.5-turbo",
            max_tokens=100,
            temperature=0.7
        )
        
        # Verify the result is the expected response
        assert result == expected_response
        
        # Verify aiohttp.ClientSession.post was called with the correct arguments
        mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_generate_completion_error():
    """Test generate completion with error response"""
    client = OpenRouterClient()
    
    # Define test messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, world!"}
    ]
    
    # Mock aiohttp.ClientSession.post
    with patch("aiohttp.ClientSession.post") as mock_post:
        # Configure the mock to return an error response
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.text.return_value = "no auth credentials found"
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Verify the method raises an OpenRouterError
        with pytest.raises(OpenRouterError) as exc:
            await client.generate_completion(
                messages=messages,
                model_id="openai/gpt-3.5-turbo",
                max_tokens=100,
                temperature=0.7
            )
        
        # Verify the error has the correct status code and message
        assert exc.value.status_code == 401
        assert "Authentication failed" in exc.value.message
        
        # Verify aiohttp.ClientSession.post was called with the correct arguments
        mock_post.assert_called_once()


@pytest.mark.skipif(not os.getenv("OPENROUTER_API_KEY"), reason="API key not provided")
@pytest.mark.asyncio
async def test_real_openrouter_status():
    """Test OpenRouter status with real API connection (requires API key)"""
    client = OpenRouterClient()
    result = await client.check_status()
    assert result is True