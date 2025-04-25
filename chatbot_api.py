from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import aiohttp
import asyncio
from docx import Document
from pymongo import MongoClient
from contextlib import asynccontextmanager

# Lifespan handler for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the keep-alive task
    task = asyncio.create_task(keep_alive())
    print("Keep-alive task started")
    try:
        yield
    finally:
        # Shutdown: Cancel the keep-alive task
        task.cancel()
        print("Keep-alive task stopped")

# Initialize FastAPI app with lifespan handler
app = FastAPI(lifespan=lifespan)

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://chatbot:VBEZlriNjETVEfUV@cluster0.yau1zmm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client["sha-bot"]
collection = db["documents"]

# OpenRouter API Setup
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
RENDER_URL = os.getenv("RENDER_URL", "https://sha-bot.onrender.com")

# Load documents into MongoDB on startup
def load_documents():
    documents = [
        {"id": "doc1", "path": "test.docx"},
        # Add more documents as needed, e.g., {"id": "doc2", "path": "another_doc.docx"}
    ]
    for doc in documents:
        try:
            document = Document(doc["path"])
            content = "\n".join([para.text for para in document.paragraphs])
            collection.update_one(
                {"_id": doc["id"]},
                {"$set": {"content": content}},
                upsert=True
            )
            print(f"Loaded document {doc['id']} into MongoDB")
        except Exception as e:
            print(f"Error loading document {doc['id']}: {e}")
            raise

# Fetch all document content from MongoDB
def get_all_document_content():
    docs = collection.find()
    content = "\n\n".join([doc["content"] for doc in docs if "content" in doc])
    return content if content else "No document content available."

# Load documents on startup
load_documents()

# Health Check
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Chat Request Model
class ChatRequest(BaseModel):
    message: str

# Chat Endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    document_content = get_all_document_content()
    messages = [
        {
            "role": "system",
            "content": (
                "You are a college chatbot. Answer questions in Arabic, strictly using the following document content. "
                "Do not use any external knowledge, general information, or creative elaboration. "
                "Extract the answer directly from the document content without rephrasing or summarizing. "
                "If the answer is not explicitly stated in the document, respond with 'المعلومات غير متوفرة في الوثيقة.'\n\n"
                f"Document content:\n{document_content}"
            )
        },
        {"role": "user", "content": request.message}
    ]

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
                json={"model": "openai/gpt-3.5-turbo", "messages": messages}
            ) as response:
                if response.status != 200:
                    raise HTTPException(status_code=500, detail="Error communicating with the API")
                result = await response.json()
                return {"response": result["choices"][0]["message"]["content"]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Keep-Alive Function
async def keep_alive():
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(f"{RENDER_URL}/health") as response:
                    if response.status == 200:
                        print("Keep-alive ping successful")
                    else:
                        print(f"Keep-alive ping failed: {response.status}")
            except Exception as e:
                print(f"Keep-alive ping error: {e}")
            await asyncio.sleep(14 * 60)  # Ping every 14 minutes