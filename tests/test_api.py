"""
Tests for the FastAPI endpoints.
"""
import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import after loading environment variables
from app.api import app
from app.models import ChatRequest
from app.openrouter_client import OpenRouterError


# Test client setup
client = TestClient(app)


def test_health_endpoint():
    """Test the health endpoint"""
    # Mock the OpenRouterClient.check_status method
    with patch('app.openrouter_client.OpenRouterClient.check_status', AsyncMock(return_value=True)):
        response = client.get("/health")
        
        # Verify the response
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["service"] == "Chatbot API"
        assert response.json()["database"] == "connected"
        assert response.json()["openrouter"] is True


def test_list_models_endpoint():
    """Test the models endpoint"""
    response = client.get("/models")
    
    # Verify the response
    assert response.status_code == 200
    assert "models" in response.json()
    
    # Check if the models contain the expected fields
    models = response.json()["models"]
    assert "gpt-3.5" in models
    assert "id" in models["gpt-3.5"]
    assert "context_length" in models["gpt-3.5"]
    assert "description" in models["gpt-3.5"]


def test_chat_endpoint_invalid_model():
    """Test the chat endpoint with an invalid model"""
    request_data = {
        "message": "Hello, world!",
        "model": "non-existent-model"
    }
    
    response = client.post("/chat", json=request_data)
    
    # Verify the response
    assert response.status_code == 400
    assert "Invalid model" in response.json()["detail"]


def test_chat_endpoint_success():
    """Test the chat endpoint with a successful response"""
    # Mock response from OpenRouter
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": "مرحبا! كيف يمكنني مساعدتك اليوم؟"
                }
            }
        ],
        "usage": {
            "total_tokens": 30
        }
    }
    
    # Test request data
    request_data = {
        "message": "مرحبا",
        "model": "gpt-3.5",
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    # Mock the MongoDB and OpenRouter clients
    with patch('app.database.mongodb.get_all_document_content', return_value="Test document content"), \
         patch('app.document_processor.document_processor.extract_relevant_section', return_value="Relevant content"), \
         patch('app.openrouter_client.openrouter_client.generate_completion', AsyncMock(return_value=mock_response)):
        
        response = client.post("/chat", json=request_data)
        
        # Verify the response
        assert response.status_code == 200
        assert response.json()["response"] == "مرحبا! كيف يمكنني مساعدتك اليوم؟"
        assert response.json()["model"] == "gpt-3.5"
        assert response.json()["tokens_used"] == 30


def test_chat_endpoint_openrouter_error():
    """Test the chat endpoint with an OpenRouter error"""
    # Test request data
    request_data = {
        "message": "Hello, world!",
        "model": "gpt-3.5"
    }
    
    # Mock the MongoDB and OpenRouter clients
    with patch('app.database.mongodb.get_all_document_content', return_value="Test document content"), \
         patch('app.document_processor.document_processor.extract_relevant_section', return_value="Relevant content"), \
         patch('app.openrouter_client.openrouter_client.generate_completion', 
               AsyncMock(side_effect=OpenRouterError(401, "Authentication failed"))):
        
        response = client.post("/chat", json=request_data)
        
        # Verify the response
        assert response.status_code == 401
        assert "Authentication failed" in response.json()["detail"]


def test_export_documents_endpoint():
    """Test the export-documents endpoint"""
    # Mock the export_to_dataset method
    with patch('app.database.mongodb.export_to_dataset', return_value="training_data.jsonl"), \
         patch('builtins.open', MagicMock()), \
         patch('app.api.open', MagicMock()):
        
        response = client.get("/export-documents")
        
        # Verify the response
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["file"] == "training_data.jsonl"
        assert "Documents exported successfully" in response.json()["message"] 