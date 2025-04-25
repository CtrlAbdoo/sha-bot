from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

# Add CORS middleware to allow requests from specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "https://your-site-name.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI",
                      "mongodb+srv://chatbot:VBEZlriNjETVEfUV@cluster0.yau1zmm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
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

# Extract relevant section from document content based on query
def extract_relevant_section(content, query):
    # Split content into lines
    lines = content.split("\n")
    relevant_lines = []
    in_relevant_section = False

    # Look for year or department-related keywords in the query
    year_keywords = {
        "الفرقة الاولى": "الفرقة الأولى",
        "الفرقة الثانيه": "الفرقة الثانية",
        "الفرقة الثالثه": "الفرقة الثالثة",
        "الفرقة الرابعه": "الفرقة الرابعة",
    }
    department_keywords = ["قسم علم الحاسب", "علوم الحاسب", "قسم الحاسبات"]
    query_lower = query.lower()

    # Find the relevant year and department
    target_year = None
    target_department = None
    for keyword, formal_year in year_keywords.items():
        if keyword in query_lower or formal_year.lower() in query_lower:
            target_year = formal_year
            break
    for dept in department_keywords:
        if dept in query_lower:
            target_department = dept
            break

    # Extract the relevant section
    for line in lines:
        line = line.strip()
        line_lower = line.lower()
        if not line:
            continue

        # Start of a year or department section
        if (target_year and target_year.lower() in line_lower) or (target_department and target_department.lower() in line_lower):
            in_relevant_section = True
            relevant_lines.append(line)
            continue
        # End of a section (next year section)
        if in_relevant_section and any(year.lower() in line_lower for year in year_keywords.values()):
            in_relevant_section = False
            continue

        if in_relevant_section:
            relevant_lines.append(line)

    # Log the extracted content for debugging
    extracted_content = "\n".join(relevant_lines) if relevant_lines else "No relevant section found"
    print(f"Extracted content for query '{query}':\n{extracted_content}")

    # If no relevant section found, fall back to trimming the content
    if not relevant_lines:
        # Limit to first 3000 words (approx. 4500 tokens in Arabic)
        words = content.split()[:3000]
        return " ".join(words)

    return "\n".join(relevant_lines)

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
    relevant_content = extract_relevant_section(document_content, request.message)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a college chatbot. Answer questions in Arabic using only the following document content. "
                "Extract the answer directly from the document content without using external knowledge. "
                "If the answer is not explicitly stated, try to infer it from the available content if possible, "
                "otherwise respond with 'المعلومات غير متوفرة في الوثيقة.'\n\n"
                f"Document content:\n{relevant_content}"
            )
        },
        {"role": "user", "content": request.message}
    ]

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
                json={"model": "meta-llama/llama-3.1-8b-instruct:free", "messages": messages}
            ) as response:
                print(f"OpenRouter API response status: {response.status}")
                response_text = await response.text()
                print(f"OpenRouter API response body: {response_text}")
                if response.status != 200:
                    raise HTTPException(status_code=500, detail=f"Error communicating with OpenRouter API: {response_text}")
                result = await response.json()
                if "choices" not in result:
                    raise HTTPException(status_code=500, detail=f"Unexpected OpenRouter response format: {response_text}")
                return {"response": result["choices"][0]["message"]["content"]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in chat endpoint: {str(e)}")

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