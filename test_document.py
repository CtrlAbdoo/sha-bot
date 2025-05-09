#!/usr/bin/env python
"""
Test script for document loading and processing.
This script helps test whether a PDF or DOCX file can be processed correctly.
"""
import os
import sys
import argparse
from docx import Document
from PyPDF2 import PdfReader
from loguru import logger

def extract_pdf_content(file_path: str) -> str:
    """Extract text content from a PDF file"""
    try:
        reader = PdfReader(file_path)
        content = []
        
        print(f"PDF document has {len(reader.pages)} pages")
        
        # Extract text from each page
        for i, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                content.append(page_text)
                char_count = len(page_text)
                print(f"  Page {i}: {char_count} characters extracted")
            else:
                print(f"  Page {i}: No text content extracted")
        
        full_content = "\n\n".join(content)
        return full_content
    except Exception as e:
        print(f"Error extracting PDF content: {e}")
        return None

def extract_docx_content(file_path: str) -> str:
    """Extract text content from a DOCX file"""
    try:
        document = Document(file_path)
        paragraphs = [para.text for para in document.paragraphs]
        
        print(f"DOCX document has {len(paragraphs)} paragraphs")
        
        # Print statistics about paragraphs
        non_empty_paragraphs = [p for p in paragraphs if p.strip()]
        print(f"  Non-empty paragraphs: {len(non_empty_paragraphs)}")
        
        if non_empty_paragraphs:
            avg_length = sum(len(p) for p in non_empty_paragraphs) / len(non_empty_paragraphs)
            print(f"  Average paragraph length: {avg_length:.1f} characters")
        
        full_content = "\n".join(paragraphs)
        return full_content
    except Exception as e:
        print(f"Error extracting DOCX content: {e}")
        return None

def test_document(file_path: str, preview_chars: int = 500) -> None:
    """Test if a document can be processed correctly"""
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist")
        return
    
    print(f"\n=== Testing Document: {file_path} ===\n")
    
    # Determine file type
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext == '.pdf':
        content = extract_pdf_content(file_path)
    elif ext == '.docx':
        content = extract_docx_content(file_path)
    else:
        print(f"Error: Unsupported file format '{ext}'. Only .pdf and .docx are supported.")
        return
    
    if content:
        total_chars = len(content)
        total_words = len(content.split())
        
        print(f"\nDocument Statistics:")
        print(f"  Total characters: {total_chars}")
        print(f"  Total words: {total_words}")
        
        print(f"\nContent Preview (first {min(preview_chars, total_chars)} characters):")
        print("-" * 40)
        print(content[:preview_chars] + "..." if total_chars > preview_chars else content)
        print("-" * 40)
        
        print("\nDocument processed successfully!")
    else:
        print("\nFailed to extract content from the document.")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test document loading and processing")
    parser.add_argument("file_path", help="Path to the document file (.pdf or .docx)")
    parser.add_argument("-p", "--preview", type=int, default=500, 
                        help="Number of characters to preview (default: 500)")
    
    args = parser.parse_args()
    test_document(args.file_path, args.preview)

if __name__ == "__main__":
    main() 