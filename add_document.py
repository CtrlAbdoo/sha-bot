#!/usr/bin/env python
"""
Script to add new documents to the chatbot's dataset.
This script modifies the config.py file to add new document paths.
"""
import os
import sys
import re
from typing import List, Dict, Any

def get_existing_document_paths() -> List[Dict[str, str]]:
    """Read existing document paths from config.py"""
    config_path = os.path.join("app", "config.py")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find document_paths definition in config.py
        match = re.search(r"document_paths: List\[Dict\[str, str\]\] = Field\(\s*default=\[\s*(.*?)\s*\]\s*\)", 
                         content, re.DOTALL)
        
        if not match:
            print("Could not find document_paths in config.py")
            return []
        
        # Parse document paths
        docs_text = match.group(1)
        docs = []
        
        # Extract document entries
        for entry_match in re.finditer(r'\{\s*"id":\s*"([^"]+)"\s*,\s*"path":\s*"([^"]+)"\s*\}', docs_text):
            doc_id, path = entry_match.groups()
            docs.append({"id": doc_id, "path": path})
        
        return docs
    
    except Exception as e:
        print(f"Error reading config.py: {e}")
        return []

def update_config_with_documents(docs: List[Dict[str, str]]) -> bool:
    """Update config.py with new document list"""
    config_path = os.path.join("app", "config.py")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Format document entries
        docs_formatted = ",\n            ".join([
            f'{{"id": "{doc["id"]}", "path": "{doc["path"]}"}}'
            for doc in docs
        ])
        
        new_docs_text = f"""document_paths: List[Dict[str, str]] = Field(
        default=[
            {docs_formatted}
        ]
    )"""
        
        # Replace document_paths section
        updated_content = re.sub(
            r"document_paths: List\[Dict\[str, str\]\] = Field\(\s*default=\[\s*.*?\s*\]\s*\)",
            new_docs_text,
            content,
            flags=re.DOTALL
        )
        
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        return True
    
    except Exception as e:
        print(f"Error updating config.py: {e}")
        return False

def add_document() -> None:
    """Add a new document to the configuration"""
    print("\n=== Add New Document to Chatbot Dataset ===\n")
    
    # Get the existing documents
    existing_docs = get_existing_document_paths()
    
    if existing_docs:
        print("Current documents:")
        for i, doc in enumerate(existing_docs, 1):
            print(f"{i}. ID: {doc['id']}, Path: {doc['path']}")
    else:
        print("No documents currently configured.")
    
    print("\nEnter details for the new document:")
    
    # Get document ID
    while True:
        doc_id = input("Document ID (e.g., 'doc3'): ").strip()
        if not doc_id:
            print("Document ID cannot be empty.")
            continue
            
        # Check if ID already exists
        if any(doc["id"] == doc_id for doc in existing_docs):
            print(f"Document ID '{doc_id}' already exists. Please choose a different ID.")
            continue
            
        break
    
    # Get document path
    while True:
        doc_path = input("Document path (e.g., 'courses.pdf'): ").strip()
        if not doc_path:
            print("Document path cannot be empty.")
            continue
            
        # Verify file exists
        if not os.path.exists(doc_path):
            print(f"Warning: File '{doc_path}' does not exist in the current directory.")
            confirm = input("Add anyway? (y/n): ").strip().lower()
            if confirm != 'y':
                continue
        
        # Check file type
        _, ext = os.path.splitext(doc_path)
        if ext.lower() not in ['.pdf', '.docx']:
            print(f"Warning: File type '{ext}' is not supported. Only .pdf and .docx are supported.")
            confirm = input("Add anyway? (y/n): ").strip().lower()
            if confirm != 'y':
                continue
                
        break
    
    # Add the new document
    new_docs = existing_docs + [{"id": doc_id, "path": doc_path}]
    
    # Update the configuration
    if update_config_with_documents(new_docs):
        print(f"\nDocument '{doc_id}' added successfully!")
        print("Restart the API for changes to take effect.")
    else:
        print("\nFailed to update configuration.")

if __name__ == "__main__":
    add_document() 