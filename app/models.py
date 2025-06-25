"""
Pydantic models for API requests and responses.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.config import settings


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message to the chatbot")
    model: str = Field(
        default=settings.default_model, 
        description="Model to use for generating response"
    )
    max_tokens: int = Field(
        default=settings.default_max_tokens, 
        description="Maximum tokens to generate in response"
    )
    temperature: float = Field(
        default=settings.default_temperature, 
        description="Temperature for response generation (0.0-1.0)"
    )
    conversation_id: Optional[str] = Field(
        default=None, 
        description="Optional conversation ID for tracking conversations"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "ما هي مواد الفرقة الثانية في قسم علم الحاسب؟",
                "model": "gpt-4.1-mini",
                "max_tokens": 500,
                "temperature": 0.7
            }
        }


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="Assistant's response")
    model: str = Field(..., description="Model used for generating response")
    tokens_used: Optional[int] = Field(
        default=None, 
        description="Total tokens used in the request and response"
    )
    conversation_id: Optional[str] = Field(
        default=None, 
        description="Conversation ID for tracking conversations"
    )


class ModelInfo(BaseModel):
    """Model information"""
    id: str = Field(..., description="OpenRouter model ID")
    context_length: int = Field(..., description="Maximum context length in tokens")
    description: str = Field(..., description="Model description")


class ModelsResponse(BaseModel):
    """Models list response"""
    models: Dict[str, ModelInfo] = Field(..., description="Available models")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    database: str = Field(..., description="Database connection status")
    openrouter: bool = Field(..., description="OpenRouter API availability")


class ExportResponse(BaseModel):
    """Export documents response"""
    status: str = Field(..., description="Operation status")
    file: str = Field(..., description="Path to the exported file")
    message: str = Field(..., description="Operation message")
    count: int = Field(..., description="Number of documents exported")