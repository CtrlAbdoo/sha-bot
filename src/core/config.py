"""
Configuration module for the chatbot API.
"""
import os
from typing import Dict, List, Optional, Any

from loguru import logger
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenRouterModel:
    """OpenRouter model configuration"""
    id: str
    context_length: int
    description: str


class Settings(BaseSettings):
    """Application settings"""
    # MongoDB settings
    mongo_uri: str = Field(
        default="mongodb+srv://chatbot:VBEZlriNjETVEfUV@cluster0.yau1zmm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    )
    mongo_db_name: str = "sha-bot"
    mongo_collection: str = "documents"
    
    # OpenRouter settings
    openrouter_api_key: str = Field(default="")
    openrouter_url: str = "https://openrouter.ai/api/v1/chat/completions"
    openrouter_status_url: str = "https://openrouter.ai/api/v1/status"
    
    # Application settings
    render_url: str = "https://sha-bot.onrender.com"
    log_level: str = "INFO"
    default_max_tokens: int = 500
    default_temperature: float = 0.7
    
    # Available models
    default_model: str = "gpt-3.5"
    
    # CORS settings
    allowed_origins: List[str] = Field(
        default=[
            "http://127.0.0.1:5500",
            "http://localhost:8000",
            "http://localhost:8081",
            "https://your-site-name.netlify.app"
        ]
    )
    
    # Document settings
    document_paths: List[Dict[str, str]] = Field(
        default=[
            {"id": "doc1", "path": "test.docx"},
            {"id": "doc2", "path": "test2.docx"},
        ]
    )
    
    # Model configs
    available_models: Dict[str, Dict[str, Any]] = Field(
        default={
            "gpt-4": {
                "id": "openai/gpt-4-turbo",
                "context_length": 128000,
                "description": "GPT-4 Turbo - Most powerful model for complex tasks"
            },
            "claude-3": {
                "id": "anthropic/claude-3-opus",
                "context_length": 100000,
                "description": "Claude 3 Opus - Advanced reasoning capabilities"
            },
            "mixtral": {
                "id": "mistralai/mixtral-8x7b-instruct",
                "context_length": 32000,
                "description": "Mixtral 8x7B - Fast and capable open model"
            },
            "qwen": {
                "id": "qwen/qwen-2-72b-instruct",
                "context_length": 32768,
                "description": "Qwen 2 72B - Advanced Chinese/English model"
            },
            "gpt-3.5": {
                "id": "openai/gpt-3.5-turbo",
                "context_length": 16000,
                "description": "GPT-3.5 Turbo - Fast and economical"
            }
        }
    )
    
    # Enable .env file loading
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    @field_validator("openrouter_api_key")
    def validate_api_key(cls, v: str) -> str:
        """Validate and clean the OpenRouter API key"""
        if not v:
            logger.warning("No OpenRouter API key provided, using development mode")
            return "sk-or-v1-development-mode"
        
        # Clean the key (remove whitespace)
        clean_key = v.strip()
        
        # Validate format
        if not clean_key.startswith("sk-or-"):
            logger.warning(
                "OpenRouter API key doesn't start with expected prefix 'sk-or-'. "
                "This may cause authentication issues."
            )
            
        return clean_key


# Create global settings instance
settings = Settings()

# Configure logging
logger.remove()
logger.add(
    "logs/chatbot.log",
    rotation="10 MB",
    retention="1 week",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}"
)
logger.add(
    lambda msg: print(msg),
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

# Log loaded configuration
logger.info(f"Loaded API key: {settings.openrouter_api_key[:4]}...{settings.openrouter_api_key[-4:]} (length: {len(settings.openrouter_api_key)})")
logger.info(f"Default model: {settings.default_model}")
logger.info(f"MongoDB URI: {settings.mongo_uri[:20]}...") 