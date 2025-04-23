import os
import json
import requests
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from docx import Document
from pydantic import BaseModel
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Chatbot API")

# Enable CORS for frontend and Flutter app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Retrieve OpenRouter API key from environment variable
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    logger.error("OPENROUTER_API_KEY environment variable not set")
    raise ValueError("OPENROUTER_API_KEY environment variable not set")


# Pydantic model for chat request
class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


# Pydantic model for chat response
class ChatResponse(BaseModel):
    response: str
    conversation_id: str


# In-memory storage for conversation history (use a database in production)
conversations = {}


# Utility functions for extracting text from documents
def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract text from PDF")


def extract_text_from_docx(docx_file):
    try:
        doc = Document(docx_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract text from DOCX")


# Function to summarize text using OpenRouter API
def summarize_text(text, max_input_length=5000):
    truncated_text = text[:max_input_length]
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "user",
                     "content": f"Summarize the following text in 200 words or less:\n\n{truncated_text}"}
                ],
            }),
            timeout=30
        )
        response.raise_for_status()
        api_response = response.json()
        if "choices" in api_response and len(api_response["choices"]) > 0:
            return api_response["choices"][0]["message"]["content"]
        else:
            logger.warning(f"Unexpected API response format during summarization: {api_response}")
            return "Summary not available."
    except requests.exceptions.RequestException as e:
        logger.error(f"Error summarizing text: {e}")
        return "Summary not available."


# Function to send messages to OpenRouter API
def send_message_to_model(messages):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "openai/gpt-3.5-turbo",
                "messages": messages,
            }),
            timeout=30
        )
        response.raise_for_status()
        api_response = response.json()
        if "choices" in api_response and len(api_response["choices"]) > 0:
            return api_response["choices"][0]["message"]["content"]
        else:
            logger.warning(f"Unexpected API response format: {api_response}")
            return "I'm sorry, I encountered an issue. Please try again later."
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with the API: {e}")
        return "I'm sorry, I encountered an issue. Please try again later."


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Endpoint to upload and summarize a document
@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".pdf", ".docx")):
        logger.warning(f"Unsupported file format: {file.filename}")
        raise HTTPException(status_code=400, detail="Unsupported file format. Only PDF and DOCX are supported.")

    try:
        # Save file temporarily
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(await file.read())

        # Extract text based on file type
        if file.filename.lower().endswith(".pdf"):
            text = extract_text_from_pdf(temp_file_path)
        else:
            text = extract_text_from_docx(temp_file_path)

        # Summarize the document
        summarized_content = summarize_text(text)

        # Clean up temporary file
        os.remove(temp_file_path)

        # Store summarized content as system message in a new conversation
        conversation_id = str(uuid.uuid4())
        conversations[conversation_id] = [
            {"role": "system", "content": f"Here is some context: {summarized_content}"}
        ]

        logger.info(f"Document uploaded and summarized, conversation_id: {conversation_id}")
        return {"conversation_id": conversation_id, "summary": summarized_content}
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


# Endpoint to handle chat messages
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    conversation_id = request.conversation_id or str(uuid.uuid4())

    if conversation_id not in conversations:
        conversations[conversation_id] = []

    # Add user message to conversation history
    conversations[conversation_id].append({"role": "user", "content": request.message})

    # Limit conversation history to last 10 messages
    conversations[conversation_id] = conversations[conversation_id][-10:]

    # Get assistant response
    assistant_response = send_message_to_model(conversations[conversation_id])

    # Add assistant response to conversation history
    conversations[conversation_id].append({"role": "assistant", "content": assistant_response})

    logger.info(f"Chat message processed, conversation_id: {conversation_id}")
    return ChatResponse(response=assistant_response, conversation_id=conversation_id)