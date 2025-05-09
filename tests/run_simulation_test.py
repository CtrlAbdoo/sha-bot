#!/usr/bin/env python
"""
Non-interactive test script for the simulated fine-tuned model.
This script will create the training data and then test it with predefined queries.
"""
import os
import sys
import json
import subprocess
import time

# Set paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
TEST_TRAINING_DATA_PATH = os.path.join(DATA_DIR, "test_training_data.jsonl")
FINETUNED_SIMULATION_PATH = os.path.join(DATA_DIR, "finetuned_simulation.json")

def print_header(text):
    """Print a header with a border"""
    border = "=" * (len(text) + 4)
    print(f"\n{border}")
    print(f"  {text}")
    print(f"{border}\n")

def create_training_data():
    """Create training data for fine-tuning"""
    print_header("Creating Training Data")
    
    # Check if training data already exists
    if os.path.exists(TEST_TRAINING_DATA_PATH):
        print("Training data file already exists. Using existing file.")
        
        # Count examples
        with open(TEST_TRAINING_DATA_PATH, "r", encoding="utf-8") as f:
            example_count = len(f.readlines())
        print(f"Found {example_count} examples in training data.")
        
        return example_count

    # Try to run the extraction script
    print("Running data extraction script...")
    try:
        extraction_script = os.path.join(os.path.dirname(__file__), "test_extract_training_data.py")
        subprocess.run([sys.executable, extraction_script], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Check if file was created
        if os.path.exists(TEST_TRAINING_DATA_PATH):
            with open(TEST_TRAINING_DATA_PATH, "r", encoding="utf-8") as f:
                example_count = len(f.readlines())
            print(f"Successfully created training data with {example_count} examples.")
            return example_count
        else:
            print("Failed to create training data file.")
            return 0
            
    except Exception as e:
        print(f"Error running extraction script: {e}")
        
        # Create manual data if script fails
        print("Creating manual training data...")
        return create_manual_training_data()

def create_manual_training_data():
    """Create manual training data if script fails"""
    # Define test courses data
    courses_by_year = {
        1: [
            "level 1 - CS101 Introduction to Programming",
            "level 1 - CS102 Data Structures",
            "level 1 - BS101 Mathematics",
            "level 1 - H101 Human Rights"
        ],
        2: [
            "level 2 - CS201 OOP",
            "level 2 - CS202 Computer Networks",
            "level 2 - BS201 Statistics",
            "level 2 - H201 Work Ethics"
        ],
        3: [
            "level 3 - CS301 System Analysis",
            "level 3 - CS302 File Processing",
            "level 3 - BS301 Operation Research",
            "level 3 - H301 Business Administration"
        ],
        4: [
            "level 4 - CS401 Advanced Programming",
            "level 4 - CS402 Database Systems",
            "level 4 - BS401 Advanced Mathematics",
            "level 4 - H401 Professional Ethics"
        ]
    }
    
    # Create training examples
    examples = []
    
    # Arabic year names
    arabic_year_names = ["الأولى", "الثانية", "الثالثة", "الرابعة"]
    
    for year, courses in courses_by_year.items():
        year_content = "\n".join(courses)
        
        # Arabic queries
        examples.append({
            "messages": [
                {"role": "system", "content": "You are a helpful assistant for a university that provides information about courses."},
                {"role": "user", "content": f"ما هي مواد الفرقة {arabic_year_names[year-1]}؟"},
                {"role": "assistant", "content": year_content}
            ]
        })
        
        # English queries
        examples.append({
            "messages": [
                {"role": "system", "content": "You are a helpful assistant for a university that provides information about courses."},
                {"role": "user", "content": f"What are the level {year} courses?"},
                {"role": "assistant", "content": year_content}
            ]
        })
    
    # Write examples to file
    with open(TEST_TRAINING_DATA_PATH, "w", encoding="utf-8") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
    
    print(f"Created {len(examples)} manual training examples.")
    return len(examples)

def create_simulation_data():
    """Create simulation data from training examples"""
    print_header("Creating Simulation Data")
    
    # Check if simulation data already exists
    if os.path.exists(FINETUNED_SIMULATION_PATH):
        print("Simulation data file already exists. Using existing file.")
        
        # Load data to count entries
        with open(FINETUNED_SIMULATION_PATH, "r", encoding="utf-8") as f:
            qa_mapping = json.load(f)
        print(f"Found {len(qa_mapping)} question-answer pairs in simulation data.")
        
        return qa_mapping
    
    # Create simulation data from training data
    print("Creating simulation data from training examples...")
    qa_mapping = {}
    
    try:
        with open(TEST_TRAINING_DATA_PATH, "r", encoding="utf-8") as f:
            for line in f:
                example = json.loads(line)
                user_message = example["messages"][1]["content"].lower()
                assistant_message = example["messages"][2]["content"]
                qa_mapping[user_message] = assistant_message
        
        # Save simulation data
        with open(FINETUNED_SIMULATION_PATH, "w", encoding="utf-8") as f:
            json.dump(qa_mapping, f, ensure_ascii=False, indent=2)
        
        print(f"Created simulation data with {len(qa_mapping)} question-answer pairs.")
        return qa_mapping
    
    except Exception as e:
        print(f"Error creating simulation data: {e}")
        return {}

def test_simulation(qa_mapping):
    """Test the simulation with some queries"""
    print_header("Testing Simulation")
    
    if not qa_mapping:
        print("No simulation data available. Skipping test.")
        return
    
    # Test queries
    test_queries = [
        "ما هي مواد الفرقة الأولى؟",
        "What are the level 2 courses?",
        "Tell me about third year",
        "المقررات الدراسية للفرقة الرابعة"
    ]
    
    # Function to find closest match (similar to the one in finetuned_api.py)
    def find_closest_match(query):
        query_lower = query.lower()
        
        # Try exact match first
        if query_lower in qa_mapping:
            return qa_mapping[query_lower], "Exact match"
        
        # Check for year mentions
        year_words = {
            "1": ["first", "one", "1", "أولى", "الأولى", "اولى", "الاولى"],
            "2": ["second", "two", "2", "ثانية", "الثانية"],
            "3": ["third", "three", "3", "ثالثة", "الثالثة"],
            "4": ["fourth", "four", "4", "رابعة", "الرابعة"]
        }
        
        # Find year in query
        detected_year = None
        for year, keywords in year_words.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_year = year
                break
        
        if not detected_year:
            return "No year detected in query", "No match"
        
        # Find a question for the detected year
        for stored_query, answer in qa_mapping.items():
            for keyword in year_words[detected_year]:
                if keyword in stored_query:
                    return answer, f"Year match: {detected_year}"
        
        return "No matching question found", "No match"
    
    # Run tests
    for i, query in enumerate(test_queries):
        print(f"\nTest {i+1}: {query}")
        start_time = time.time()
        response, match_type = find_closest_match(query)
        end_time = time.time()
        
        print(f"Match type: {match_type}")
        print(f"Response: {response[:100]}..." if len(response) > 100 else f"Response: {response}")
        print(f"Time: {(end_time - start_time)*1000:.2f} ms")
    
    print("\nAll tests completed successfully!")

def main():
    """Main function"""
    print_header("SHA-Bot Simulated Fine-tuning Test")
    
    # Step 1: Create training data
    example_count = create_training_data()
    if example_count == 0:
        print("Failed to create training data. Exiting.")
        return
    
    # Step 2: Create simulation data
    qa_mapping = create_simulation_data()
    
    # Step 3: Test simulation
    test_simulation(qa_mapping)
    
    print_header("Summary")
    print(f"Created {example_count} training examples")
    print(f"Created {len(qa_mapping)} question-answer pairs for simulation")
    print("\nThe simulation is now ready to use.")
    print("To use the simulated fine-tuned API:")
    print("1. Update app/config.py to set use_finetuned_model=True")
    print("2. Run: python -m uvicorn app.finetuned_api:app --host 0.0.0.0 --port 8000")
    
if __name__ == "__main__":
    main() 