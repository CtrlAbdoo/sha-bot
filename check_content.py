#!/usr/bin/env python
"""
Script to check content stored in MongoDB.
"""
from app.database import mongodb
from loguru import logger

def main():
    """Check document content in MongoDB"""
    try:
        # Get all documents
        docs = mongodb.collection.find()
        
        print("\nDocuments in MongoDB:")
        print("-" * 50)
        
        for doc in docs:
            doc_id = doc.get("_id", "Unknown")
            content_preview = doc.get("content", "")[:200] + "..." if doc.get("content") else "No content"
            source = doc.get("source_url", "Manual upload")
            doc_type = doc.get("type", "Unknown")
            
            print(f"\nDocument ID: {doc_id}")
            print(f"Type: {doc_type}")
            print(f"Source: {source}")
            print("Content Preview:")
            print("-" * 30)
            print(content_preview)
            print("-" * 30)
            
    except Exception as e:
        logger.error(f"Error checking content: {e}")

if __name__ == "__main__":
    main() 