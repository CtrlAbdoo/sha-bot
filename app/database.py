"""
Database module for MongoDB connections and operations.
"""
import json
import os
from typing import Dict, List, Any, Optional

from docx import Document
from PyPDF2 import PdfReader
from loguru import logger
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from app.config import settings


class MongoDB:
    """MongoDB database handler"""
    client: MongoClient
    db: Database
    collection: Collection
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.client = MongoClient(settings.mongo_uri)
        self.db = self.client[settings.mongo_db_name]
        self.collection = self.db[settings.mongo_collection]
        logger.info(f"Connected to MongoDB: {settings.mongo_db_name}.{settings.mongo_collection}")
    
    def load_documents(self) -> None:
        """Load documents into MongoDB"""
        for doc_info in settings.document_paths:
            try:
                doc_id = doc_info["id"]
                doc_path = doc_info["path"]
                
                logger.info(f"Loading document {doc_id} from {doc_path}")
                
                # Determine file type based on extension
                file_ext = os.path.splitext(doc_path)[1].lower()
                
                # Process based on file type
                if file_ext == '.pdf':
                    # Process PDF file
                    content = self._extract_pdf_content(doc_path)
                elif file_ext == '.docx':
                    # Process DOCX file
                    content = self._extract_docx_content(doc_path)
                elif file_ext == '.txt':
                    # Process TXT file
                    content = self._extract_txt_content(doc_path)
                else:
                    logger.warning(f"Unsupported file type: {file_ext} for document {doc_id}")
                    continue
                
                # Store in MongoDB
                self.collection.update_one(
                    {"_id": doc_id},
                    {"$set": {"content": content}},
                    upsert=True
                )
                logger.info(f"Document {doc_id} loaded successfully")
            except Exception as e:
                logger.error(f"Error loading document {doc_info['id']}: {e}")
                raise

    def _extract_pdf_content(self, file_path: str) -> str:
        """Extract text content from a PDF file"""
        try:
            reader = PdfReader(file_path)
            content = []
            
            # Extract text from each page
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    content.append(page_text)
            
            return "\n\n".join(content)
        except Exception as e:
            logger.error(f"Error extracting PDF content from {file_path}: {e}")
            raise
    
    def _extract_docx_content(self, file_path: str) -> str:
        """Extract text content from a DOCX file"""
        document = Document(file_path)
        return "\n".join([para.text for para in document.paragraphs])
    
    def _extract_txt_content(self, file_path: str) -> str:
        """Extract text content from a TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting TXT content from {file_path}: {e}")
            raise
    
    def get_all_document_content(self) -> str:
        """Fetch all document content from MongoDB"""
        docs = self.collection.find()
        content = "\n\n".join([doc["content"] for doc in docs if "content" in doc])
        return content if content else "No document content available."
    
    def export_to_dataset(self, output_file: str = "training_data.jsonl") -> str:
        """Export MongoDB documents to JSONL for fine-tuning"""
        docs = self.collection.find()
        count = 0
        
        with open(output_file, "w", encoding="utf-8") as f:
            for doc in docs:
                if "content" in doc:
                    # Format as messages for fine-tuning
                    entry = {
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": f"Tell me about this: {doc['content'][:100]}"},
                            {"role": "assistant", "content": doc["content"]}
                        ]
                    }
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                    count += 1
        
        logger.info(f"Exported {count} documents to {output_file}")
        return output_file


# Global database instance
mongodb = MongoDB() 