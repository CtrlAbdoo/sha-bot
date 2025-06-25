"""
API routes for the chatbot application using a simulated fine-tuned model.
This version uses a lookup dictionary created from all MongoDB data to respond to
queries without needing to retrieve and process documents for each request.
"""
import asyncio
import json
import os
import re
import aiohttp
from contextlib import asynccontextmanager
from typing import Dict, List, Any, Optional, Tuple

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.models import (
    ChatRequest, ChatResponse, 
    HealthResponse, ModelsResponse
)
from app.openrouter_client import openrouter_client, OpenRouterError


# Load the simulated fine-tuned data if it exists
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SIMULATION_FILE = os.path.join(DATA_DIR, "finetuned_simulation.json")
qa_mapping = {}

if os.path.exists(SIMULATION_FILE):
    try:
        with open(SIMULATION_FILE, "r", encoding="utf-8") as f:
            qa_mapping = json.load(f)
        logger.info(f"Loaded {len(qa_mapping)} question-answer pairs from {SIMULATION_FILE}")
    except Exception as e:
        logger.error(f"Error loading {SIMULATION_FILE}: {e}")


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
    # Startup: Start keep-alive task
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
    title="Advanced Chatbot API (Simulated Fine-tuned)",
    description="AI-powered chatbot API using OpenRouter with simulated fine-tuning for all MongoDB content",
    version="3.0.0",
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


def find_best_match(query: str) -> Tuple[Optional[str], float]:
    """
    Find the best matching question in our training data using keyword matching and semantic similarity.
    Returns the best match and a confidence score (0-1).
    """
    if not qa_mapping:
        return None, 0.0
    
    query_lower = query.lower()
    
    # 1. Try exact match first (highest confidence)
    if query_lower in qa_mapping:
        return query_lower, 1.0
    
    # 2. Check for year/level mentions (for course-related queries)
    year_words = {
        "1": ["first", "one", "1", "أولى", "الأولى", "اولى", "الاولى"],
        "2": ["second", "two", "2", "ثانية", "الثانية"],
        "3": ["third", "three", "3", "ثالثة", "الثالثة"],
        "4": ["fourth", "four", "4", "رابعة", "الرابعة"]
    }
    
    # Try to determine if this is a year-related query
    for year, keywords in year_words.items():
        if any(keyword in query_lower for keyword in keywords):
            # Find questions for the detected year
            for stored_question in qa_mapping.keys():
                if any(keyword in stored_question for keyword in keywords):
                    return stored_question, 0.9
    
    # 3. Look for keyword matches (more general approach)
    # Extract meaningful keywords from the query (words with length > 3)
    query_words = set(re.findall(r'\b\w{4,}\b', query_lower))
    
    if query_words:
        best_match = None
        best_score = 0.0
        
        for stored_question in qa_mapping.keys():
            stored_words = set(re.findall(r'\b\w{4,}\b', stored_question.lower()))
            
            if not stored_words:
                continue
            
            # Calculate Jaccard similarity (intersection over union)
            intersection = len(query_words.intersection(stored_words))
            union = len(query_words.union(stored_words))
            
            if union > 0:
                score = intersection / union
                
                # Bonus for longer word matches
                for word in query_words.intersection(stored_words):
                    if len(word) > 6:  # Bonus for longer words
                        score += 0.05
                
                if score > best_score:
                    best_score = score
                    best_match = stored_question
        
        # Return if we have a reasonable match (score > 0.3)
        if best_match and best_score > 0.3:
            return best_match, best_score
    
    # 4. Content type detection
    # Check if query is asking for a summary or overview
    summary_keywords = ["summary", "overview", "about", "tell me about", "what is", "ملخص", "نظرة عامة", "ما هو"]
    if any(keyword in query_lower for keyword in summary_keywords):
        # Look for summary-type stored questions
        for stored_question in qa_mapping.keys():
            if any(keyword in stored_question.lower() for keyword in summary_keywords):
                # Extract potential subject from query
                subject_match = re.search(r'(?:about|of|is|هو) (.+?)(?:\?|$|\.)', query_lower)
                if subject_match:
                    subject = subject_match.group(1).strip()
                    if subject in stored_question.lower():
                        return stored_question, 0.8
    
    # 5. Return a low confidence match or None if nothing good was found
    # This will likely cause a fallback to OpenRouter
    return None, 0.0


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    """Health check endpoint"""
    # Check OpenRouter API status
    openrouter_status = await openrouter_client.check_status()
    
    # Check simulation data
    simulation_status = "healthy" if qa_mapping else "not loaded"
    
    return HealthResponse(
        status="healthy", 
        service=f"Chatbot API (Simulated Fine-tuned) - {len(qa_mapping)} QA pairs", 
        database=simulation_status, 
        openrouter=openrouter_status
    )


@app.get("/models", response_model=ModelsResponse, tags=["Models"])
async def list_models():
    """List available models"""
    # Add the simulated fine-tuned model to the list
    model_info = {
        "fine-tuned-assistant": {
            "id": "openai/gpt-4",  # Using gpt-4 from OpenRouter
            "context_length": 16000,
            "description": "Simulated fine-tuned model for all MongoDB content"
        }
    }
    
    return ModelsResponse(models=model_info)


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Chat endpoint for sending messages to the chatbot using a simulated fine-tuned model
    with intelligent responses from OpenRouter
    """
    user_message = request.message
    
    # Detect language (simple check for Arabic)
    is_arabic = any('\u0600' <= c <= '\u06FF' for c in user_message)
    
    # Try to find the best match in our simulation data
    best_match, confidence = find_best_match(user_message)
    
    # System message with different instructions based on whether we found a match
    system_message = {
        "role": "system",
        "content": (
            "You are a helpful assistant for El-Shorouk Academy that provides accurate information on "
            "university courses, academic subjects, and general knowledge. "
            "Always respond in the same language as the user's query."
        )
    }
    
    # User message template
    messages = [system_message]
    
    # If we found a good match, use the stored answer as context
    if best_match and confidence > 0.3:
        retrieved_data = qa_mapping[best_match]
        logger.info(f"Found match for query with confidence {confidence:.2f}: {user_message[:50]}...")
        
        # Add context to the system message
        system_message["content"] += (
            f"\n\nThe following information is relevant to the user's query: \n{retrieved_data}\n\n"
            f"Use this information to provide a comprehensive answer. Don't mention that this information "
            f"was retrieved from a database. Structure your response in a natural, conversational way. "
            f"If the query is in Arabic, respond in Arabic, otherwise respond in English."
        )
        
        # Add the user's message
        messages.append({"role": "user", "content": user_message})
        
    else:
        # No good match found, just pass the user's query
        logger.info(f"No good match found for query: {user_message[:50]}... Using general knowledge")
        messages.append({"role": "user", "content": user_message})
    
    try:
        # Call OpenRouter API
        # Determine which model to use, with proper fallback handling
        try:
            # First try to use the requested model
            if request.model in settings.available_models:
                model_config = settings.available_models[request.model]
            # If that fails, try to use the default model
            elif settings.default_model in settings.available_models:
                model_config = settings.available_models[settings.default_model]
            # If both fail, use gpt-3.5 as a last resort
            else:
                model_config = settings.available_models["gpt-3.5"]
                
            model_id = model_config["id"]
            logger.info(f"Using model: {request.model} -> {model_id}")
            
            result = await openrouter_client.generate_completion(
                messages=messages,
                model_id=model_id,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
        except Exception as e:
            logger.error(f"Error selecting model: {e}")
            # Fallback to a reliable model
            model_id = settings.available_models["gpt-3.5"]["id"]
            logger.info(f"Falling back to model: gpt-3.5 -> {model_id}")
            
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
        
        # Determine model description
        if best_match and confidence > 0.3:
            model_description = f"fine-tuned-assistant (confidence: {confidence:.2f})"
        else:
            model_description = result.get("model", "openai/gpt-3.5-turbo")
        
        return ChatResponse(
            response=assistant_message,
            model=model_description,
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