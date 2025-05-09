"""
Test script for course listing functionality.
"""
from app.response_generator import ResponseGenerator
from app.document_processor import DocumentProcessor

def test_course_queries():
    # Sample content with course listings
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
    
    # Test queries in both Arabic and English
    queries = [
        # Arabic queries
        "ما هي مواد الفرقة الأولى؟",
        "عايز اعرف مواد الفرقة الثانية",
        "مواد السنة الثالثة",
        "المقررات الدراسية للفرقة الرابعة",
        # English queries
        "What are the first year courses?",
        "Show me the second year subjects",
        "List the courses for third year",
        "What are the fourth year courses?"
    ]
    
    # Process each query
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        # Extract relevant content
        relevant_content = DocumentProcessor.extract_relevant_section(content, query)
        
        # Generate response
        response = ResponseGenerator.generate_response(relevant_content, query)
        
        print("Response:")
        print(response["response"])
        print("-" * 50)

if __name__ == "__main__":
    test_course_queries() 