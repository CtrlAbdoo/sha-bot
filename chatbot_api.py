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


# Estimate token count (rough approximation: 1 word ≈ 1-2 tokens in Arabic)
def estimate_tokens(text):
    words = len(text.split())
    return words * 1.5  # Approximate tokens in Arabic


# Extract relevant section from document content based on query
def extract_relevant_section(content, query):
    # Split content into lines
    lines = content.split("\n")
    relevant_lines = []
    in_relevant_section = False

    # Look for year or course-related keywords in the query
    year_keywords = {
        "الفرقة الاولى": "الفرقة الأولى",
        "الفرقة الثانيه": "الفرقة الثانية",
        "الفرقة الثالثه": "الفرقة الثالثة",
        "الفرقة الرابعه": "الفرقة الرابعة",
    }
    query_lower = query.lower()

    # Find the relevant year section
    target_year = None
    for keyword, formal_year in year_keywords.items():
        if keyword in query_lower or formal_year in query_lower:
            target_year = formal_year
            break

    # Look for specific course (e.g., "الذكاء الاصطناعي")
    course_name = None
    if "الذكاء الاصطناعي" in query:
        course_name = "الذكاء الاصطناعي"

    # Extract the relevant section
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Start of a year section
        if target_year and target_year in line:
            in_relevant_section = True
            relevant_lines.append(line)
            continue
        # Start of a course section
        elif course_name and course_name in line:
            in_relevant_section = True
            relevant_lines.append(line)
            # Include the next few lines (e.g., course details)
            for j in range(i + 1, min(i + 5, len(lines))):  # Look ahead 5 lines
                next_line = lines[j].strip()
                if not next_line or any(year in next_line for year in year_keywords.values()):
                    break
                relevant_lines.append(next_line)
            break  # Stop after finding the course
        # End of a section
        elif in_relevant_section and any(year in line for year in year_keywords.values()):
            in_relevant_section = False
            continue

        if in_relevant_section:
            relevant_lines.append(line)

    # If no relevant section found, or section is too large, trim aggressively
    extracted_content = "\n".join(relevant_lines)
    if not extracted_content or estimate_tokens(extracted_content) > 6000:  # ~4000 words
        # Trim to 2000 words (approx. 3000 tokens in Arabic)
        words = content.split()[:2000]
        extracted_content = " ".join(words)

    # Log the extracted content and token estimate
    token_estimate = estimate_tokens(extracted_content)
    print(f"Extracted content (first 100 chars): {extracted_content[:100]}...")
    print(f"Estimated tokens for extracted content: {token_estimate}")

    return extracted_content


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
    # Get full document content
    full_content = get_all_document_content()
    # Extract relevant section based on the query
    document_content = extract_relevant_section(full_content, request.message)
    messages = [
        {
            "role": "system",
            "content": (
                "Answer questions in Arabic, strictly using the following document content. "
                "Do not use any external knowledge, general information, or creative elaboration. "
                "Extract the answer directly from the document content without rephrasing or summarizing. "
                "Be flexible with Arabic spelling variations (e.g., 'الرابعه' and 'الرابعة' are the same). "
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
                    json={
                        "model": "openai/gpt-3.5-turbo",
                        "messages": messages,
                        "max_tokens": 3000
                    }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"OpenRouter API error: Status {response.status}, Response: {error_text}")
                    raise HTTPException(status_code=500, detail=f"Error communicating with the API: {error_text}")
                result = await response.json()
                print(f"OpenRouter API response: {result}")
                if "choices" not in result:
                    raise HTTPException(status_code=500, detail=f"Invalid API response: {result}")
                return {"response": result["choices"][0]["message"]["content"]}
        except Exception as e:
            print(f"Chat endpoint error: {str(e)}")
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