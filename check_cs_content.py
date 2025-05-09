#!/usr/bin/env python
"""
Script to check the content stored in MongoDB for the CS department page.
"""
from app.database import mongodb
from loguru import logger

def main():
    """Main function to check CS department content"""
    try:
        # Get all documents from MongoDB
        docs = mongodb.collection.find()
        
        # Look for CS department content using various keywords
        cs_keywords = [
            "قسم علم الحاسب",
            "علوم الحاسب",
            "قسم الحاسبات",
            "computer science",
            "cs department",
            "hicit"
        ]
        
        found_content = []
        for doc in docs:
            if "content" in doc:
                content = doc["content"]
                # Check if any keyword is in the content
                if any(keyword in content.lower() for keyword in cs_keywords):
                    found_content.append(content)
        
        if found_content:
            logger.info(f"Found {len(found_content)} documents with CS department content:")
            for i, content in enumerate(found_content, 1):
                print(f"\nDocument {i}:")
                print("="*80)
                print(content)
                print("="*80 + "\n")
        else:
            logger.warning("No CS department content found in MongoDB")
            
    except Exception as e:
        logger.error(f"Error checking CS department content: {e}")

if __name__ == "__main__":
    main() 