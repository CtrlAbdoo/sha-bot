"""
API routes for the chatbot application.
"""
import asyncio
import aiohttp
from contextlib import asynccontextmanager
from typing import Dict, List, Any

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.database import mongodb
from app.document_processor import document_processor
from app.models import (
    ChatRequest, ChatResponse, 
    HealthResponse, ModelsResponse, ExportResponse,
    ModelInfo
)
from app.openrouter_client import openrouter_client, OpenRouterError

# Keep-alive background task
async def keep_alive():
    """Background task to keep the server alive on platforms like Render by actively pinging the health endpoint"""
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(f"{settings.render_url}/health") as response:
                    if response.status == 200:
                        logger.debug("Keep-alive ping successful")
                    else:
                        logger.warning(f"Keep-alive ping failed: {response.status}")
            except Exception as e:
                logger.error(f"Keep-alive ping error: {e}")
            await asyncio.sleep(14 * 60)  # Ping every 14 minutes


# Lifespan handler for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler for the FastAPI application"""
    # Startup: Load documents and start keep-alive task
    try:
        mongodb.load_documents()
        logger.info("Documents loaded successfully")
    except Exception as e:
        logger.error(f"Error loading documents: {e}")
    
    task = asyncio.create_task(keep_alive())
    logger.info("Keep-alive task started")
    
    try:
        yield
    finally:
        # Shutdown: Cancel the keep-alive task
        task.cancel()
        logger.info("Keep-alive task stopped")


# Create the FastAPI application
app = FastAPI(
    title="Advanced Chatbot API",
    description="AI-powered chatbot API that uses OpenRouter models with custom MongoDB data",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    """Health check endpoint"""
    # Check OpenRouter API status
    openrouter_status = await openrouter_client.check_status()
    
    return HealthResponse(
        status="healthy", 
        service="Chatbot API", 
        database="connected",
        openrouter=openrouter_status
    )


@app.get("/models", response_model=ModelsResponse, tags=["Models"])
async def list_models():
    """List available models"""
    # Convert the dictionary to the expected model format
    model_info = {
        model_name: ModelInfo(
            id=model_data["id"],
            context_length=model_data["context_length"],
            description=model_data["description"]
        )
        for model_name, model_data in settings.available_models.items()
    }
    
    return ModelsResponse(models=model_info)


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Chat endpoint for sending messages to the chatbot
    """
    # Validate model selection
    if request.model not in settings.available_models:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid model: {request.model}. Available models: {list(settings.available_models.keys())}"
        )
    
    # Get selected model configuration
    model_config = settings.available_models[request.model]
    model_id = model_config["id"]
    
    # Get document content and extract relevant section
    document_content = mongodb.get_all_document_content()
    relevant_content = document_processor.extract_relevant_section(document_content, request.message)
    
    # Prepare messages for the model
    messages = [
        {
            "role": "system",
            "content": (
                "You are a college chatbot. Answer questions in Arabic using only the following document content. "
                "Extract the answer directly from the document content without rephrasing, summarizing, or using external knowledge. "
                "If the answer is not explicitly stated in the document, respond with 'المعلومات غير متوفرة في الوثيقة.'\n\n"
                f"Document content:\n{relevant_content}"
            )
        },
        {"role": "user", "content": request.message}
    ]
    
    try:
        # Call OpenRouter API
        result = await openrouter_client.generate_completion(
            messages=messages,
            model_id=model_id,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Extract the assistant's message
        if "choices" not in result or not result["choices"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Invalid response from OpenRouter API"
            )
        
        # Extract response data
        assistant_message = result["choices"][0]["message"]["content"]
        tokens_used = result.get("usage", {}).get("total_tokens")
        
        return ChatResponse(
            response=assistant_message,
            model=request.model,
            tokens_used=tokens_used,
            conversation_id=request.conversation_id
        )
    
    except OpenRouterError as e:
        # Map OpenRouter errors to appropriate HTTP status codes
        status_code = e.status_code
        if status_code == 401:
            status_code = status.HTTP_401_UNAUTHORIZED
        elif status_code == 429:
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
        elif status_code >= 500:
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        
        raise HTTPException(status_code=status_code, detail=e.message)
    
    except Exception as e:
        logger.exception(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error processing request: {str(e)}"
        )


@app.get("/export-documents", response_model=ExportResponse, tags=["Documents"])
async def export_documents():
    """Export documents from MongoDB to JSONL format for fine-tuning"""
    try:
        output_file = mongodb.export_to_dataset()
        
        # Count documents in the exported file
        count = 0
        with open(output_file, "r", encoding="utf-8") as f:
            for _ in f:
                count += 1
        
        return ExportResponse(
            status="success", 
            file=output_file, 
            message="Documents exported successfully",
            count=count
        )
    except Exception as e:
        logger.exception(f"Error exporting documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error exporting documents: {str(e)}"
        ) 