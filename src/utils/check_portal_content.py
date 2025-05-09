#!/usr/bin/env python
"""
Script to check content from portal and learning system.
"""
from app.database import mongodb
from loguru import logger

def main():
    """Check portal and learning system content"""
    try:
        # Get documents from portal and learning system
        portal_docs = mongodb.collection.find({
            "source_url": {"$regex": "portal.sha.edu.eg|learn.sha.edu.eg"}
        })
        
        print("\nPortal and Learning System Content:")
        print("-" * 50)
        
        for doc in portal_docs:
            doc_id = doc.get("_id", "Unknown")
            source = doc.get("source_url", "")
            content_preview = doc.get("content", "")[:500] + "..." if doc.get("content") else "No content"
            keywords = doc.get("keywords", [])
            
            print(f"\nDocument ID: {doc_id}")
            print(f"Source: {source}")
            print(f"Keywords found: {', '.join(keywords)}")
            print("Content Preview:")
            print("-" * 30)
            print(content_preview)
            print("-" * 30)
            
    except Exception as e:
        logger.error(f"Error checking content: {e}")

if __name__ == "__main__":
    main() 