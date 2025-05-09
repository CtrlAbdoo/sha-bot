"""
Main FastAPI application module.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.response_generator import ResponseGenerator
from app.document_processor import DocumentProcessor

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-3.5"
    max_tokens: int = 500
    temperature: float = 0.7

class ChatResponse(BaseModel):
    response: str
    model: str
    tokens_used: int
    conversation_id: Optional[str] = None

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint that processes user queries and returns formatted responses.
    """
    try:
        # Sample content - in a real application, this would come from a database
        content = """
        level 1 - CS101 Introduction to Programming
        level 1 - CS102 Data Structures
        level 1 - BS101 Mathematics
        level 1 - H101 Human Rights
        
        level 2 - CS201 OOP
        level 2 - CS202 Computer Networks
        level 2 - BS201 Statistics
        level 2 - H201 Work Ethics
        
        level 3 - CS301 System Analysis
        level 3 - CS302 File Processing
        level 3 - BS301 Operation Research
        level 3 - H301 Business Administration
        
        level 4 - CS401 Advanced Programming
        level 4 - CS402 Database Systems
        level 4 - BS401 Advanced Mathematics
        level 4 - H401 Professional Ethics
        """
        
        # Extract relevant content based on the query
        relevant_content = DocumentProcessor.extract_relevant_section(content, request.message)
        
        # Generate response
        response = ResponseGenerator.generate_response(
            relevant_content,
            request.message,
            request.model
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 