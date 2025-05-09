#!/usr/bin/env python
"""
Test script to extract training data for fine-tuning without
actually starting a fine-tuning job.
"""
import os
import json
from loguru import logger
from app.database import mongodb
from finetune_model import prepare_training_data

# Set up logging
logger.add("logs/test_extract.log", rotation="10 MB", level="INFO")

def main():
    """Extract training data and show examples"""
    print("Testing training data extraction...")
    
    # Create output file
    output_file = "test_training_data.jsonl"
    
    # Check if MongoDB is connected
    try:
        # Check if MongoDB is connected and has documents
        doc_count = mongodb.collection.count_documents({})
        print(f"MongoDB connected. Found {doc_count} documents.")
        
        if doc_count == 0:
            print("No documents found in MongoDB. Using local text files instead.")
            # Create examples from text files directly
            create_examples_from_text_files(output_file)
        else:
            # Use the regular extraction from MongoDB
            file_path, example_count = prepare_training_data(output_file)
            print(f"Created {example_count} training examples in {file_path}")
    
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        print("Using local text files instead.")
        # Create examples from text files directly
        create_examples_from_text_files(output_file)
    
    # Print some examples from the output file
    print_examples(output_file)

def create_examples_from_text_files(output_file):
    """Create training examples directly from text files"""
    text_files = [
        {"id": "doc1", "path": "test.txt"},
        {"id": "doc2", "path": "test2.txt"}
    ]
    
    count = 0
    
    with open(output_file, "w", encoding="utf-8") as f:
        for doc in text_files:
            try:
                # Read the text file
                with open(doc["path"], "r", encoding="utf-8") as text_file:
                    content = text_file.read()
                
                # Create examples for each academic year
                for year in range(1, 5):
                    # Extract content related to this year
                    year_content = "\n".join([
                        line for line in content.split("\n") 
                        if f"level {year}" in line.lower()
                    ])
                    
                    if year_content:
                        # Create Arabic query examples
                        arabic_queries = [
                            f"ما هي مواد الفرقة {['الأولى', 'الثانية', 'الثالثة', 'الرابعة'][year-1]}؟",
                            f"أخبرني عن مقررات المستوى {year}",
                            f"ما هي المواد الدراسية للسنة {year}؟"
                        ]
                        
                        # Create English query examples
                        english_queries = [
                            f"What are the level {year} courses?",
                            f"Tell me about year {year} subjects",
                            f"List the courses for year {year}"
                        ]
                        
                        # Combine all queries
                        all_queries = arabic_queries + english_queries
                        
                        # Create training examples for each query
                        for query in all_queries:
                            entry = {
                                "messages": [
                                    {"role": "system", "content": "You are a helpful assistant for a university that provides information about courses."},
                                    {"role": "user", "content": query},
                                    {"role": "assistant", "content": year_content}
                                ]
                            }
                            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                            count += 1
            except Exception as e:
                print(f"Error processing {doc['path']}: {e}")
    
    print(f"Created {count} training examples in {output_file}")
    return output_file, count

def print_examples(file_path, num_examples=3):
    """Print a few example entries from the JSONL file"""
    print(f"\nExample training data entries from {file_path}:")
    print("-" * 50)
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
            # Print up to num_examples or all if fewer
            for i, line in enumerate(lines[:num_examples]):
                entry = json.loads(line)
                print(f"\nExample {i+1}:")
                print(f"System: {entry['messages'][0]['content']}")
                print(f"User: {entry['messages'][1]['content']}")
                print(f"Assistant: {entry['messages'][2]['content'][:150]}...")  # Print first 150 chars
                print("-" * 50)
            
            print(f"\nTotal examples in file: {len(lines)}")
    except Exception as e:
        print(f"Error reading examples: {e}")

if __name__ == "__main__":
    main() 