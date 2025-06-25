"""
Response generator module for the chatbot.
"""
from loguru import logger
from typing import Dict, Any, List, Optional
import re

class ResponseGenerator:
    """Generates responses based on extracted content"""
    
    @staticmethod
    def _is_arabic_query(query: str) -> bool:
        """Check if the query is in Arabic"""
        # Arabic Unicode range
        arabic_pattern = re.compile(r'[\u0600-\u06FF]')
        return bool(arabic_pattern.search(query))

    @staticmethod
    def _extract_courses(content: str, level: str) -> List[str]:
        """Extract course listings for a specific level"""
        courses = []
        lines = content.split("\n")
        in_level = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.lower().startswith(level.lower()):
                in_level = True
                courses.append(line)
            elif in_level and any(line.lower().startswith(f"level {i}") for i in range(1, 5)):
                in_level = False
            elif in_level:
                courses.append(line)
                
        return courses

    @staticmethod
    def _format_course_list(courses: List[str], is_arabic: bool) -> str:
        """Format a list of courses into a readable response"""
        if not courses:
            return "المعلومات غير متوفرة في الوثيقة." if is_arabic else "Information not available in the document."
            
        # Headers based on language
        if is_arabic:
            response = "مواد الفرقة المطلوبة هي:\n\n"
            prefix_translations = {
                "BS": "علوم أساسية",
                "CS": "علوم حاسب",
                "H": "علوم إنسانية"
            }
        else:
            response = "The courses for the requested year are:\n\n"
            prefix_translations = {
                "BS": "Basic Sciences",
                "CS": "Computer Science",
                "H": "Humanities"
            }
        
        # Dictionary to translate course names
        course_translations = {
            "data structures": "هياكل البيانات",
            "oop": "البرمجة كائنية التوجه",
            "system analysis": "تحليل النظم",
            "file processing": "معالجة الملفات",
            "computer networks": "شبكات الحاسب",
            "operation research": "بحوث العمليات",
            "stat prob": "الإحصاء والاحتمالات",
            "co": "تنظيم الحاسبات",
            "human rights": "حقوق الإنسان",
            "work ethics": "أخلاقيات العمل",
            "business administration": "إدارة الأعمال",
            "professional ethics": "أخلاقيات المهنة",
            "advanced programming": "البرمجة المتقدمة",
            "database systems": "نظم قواعد البيانات",
            "advanced mathematics": "الرياضيات المتقدمة"
        }
        
        # Group courses by prefix
        grouped_courses = {}
        for course in courses:
            # Clean up the course name
            course = course.replace("_2F", "").replace("updated", "").strip()
            course = re.sub(r'\s+', ' ', course)  # Remove multiple spaces
            
            # Extract course code and name
            match = re.match(r'level \d+ - ([A-Z]+)[\s_]?(\d+)\s+(.+)', course)
            if match:
                prefix, number, name = match.groups()
                if prefix not in grouped_courses:
                    grouped_courses[prefix] = []
                    
                # Clean up the name
                name = name.replace("_", " ").strip()
                name = re.sub(r'\s+', ' ', name)  # Remove multiple spaces
                
                # Get course name in appropriate language
                if is_arabic:
                    name_final = course_translations.get(name.lower(), name)
                else:
                    # If English requested but we have Arabic translation, use English original
                    name_final = next((k for k, v in course_translations.items() if v == name), name)
                    name_final = name_final.title()  # Capitalize English names
                
                grouped_courses[prefix].append((number, name_final))
            else:
                if "Other" not in grouped_courses:
                    grouped_courses["Other"] = []
                grouped_courses["Other"].append(("", course))
        
        # Add courses by group
        for prefix in ["CS", "BS", "H", "Other"]:
            if prefix not in grouped_courses:
                continue
                
            prefix_display = prefix_translations.get(prefix, prefix)
            response += f"\n{prefix_display}:\n"
            
            # Sort courses by number within each group
            courses_in_group = sorted(grouped_courses[prefix], key=lambda x: x[0] if x[0].isdigit() else "0")
            
            for number, name in courses_in_group:
                if number:
                    response += f"- {prefix}{number}: {name}\n"
                else:
                    response += f"- {name}\n"
            
        return response

    @staticmethod
    def generate_response(content: str, query: str, model: str = "gpt-4.1-mini") -> Dict[str, Any]:
        """
        Generate a response based on the content and query.
        
        Args:
            content: The relevant content extracted from documents
            query: The user's query
            model: The model being used
            
        Returns:
            Dict containing response and metadata
        """
        is_arabic = ResponseGenerator._is_arabic_query(query)
        query_lower = query.lower()
        
        # Handle course listings
        if any(keyword in query for keyword in ["مواد", "المقررات", "courses", "subjects"]):
            if any(year in query for year in ["الفرقة الثانية", "الفرقة الثانيه", "السنة الثانية", "المستوى الثاني", "second year", "level 2"]):
                courses = ResponseGenerator._extract_courses(content, "level 2")
                response = ResponseGenerator._format_course_list(courses, is_arabic)
            elif any(year in query for year in ["الفرقة الأولى", "الفرقة الاولى", "السنة الأولى", "المستوى الأول", "first year", "level 1"]):
                courses = ResponseGenerator._extract_courses(content, "level 1")
                response = ResponseGenerator._format_course_list(courses, is_arabic)
            elif any(year in query for year in ["الفرقة الثالثة", "الفرقة الثالثه", "السنة الثالثة", "المستوى الثالث", "third year", "level 3"]):
                courses = ResponseGenerator._extract_courses(content, "level 3")
                response = ResponseGenerator._format_course_list(courses, is_arabic)
            elif any(year in query for year in ["الفرقة الرابعة", "الفرقة الرابعه", "السنة الرابعة", "المستوى الرابع", "fourth year", "level 4"]):
                courses = ResponseGenerator._extract_courses(content, "level 4")
                response = ResponseGenerator._format_course_list(courses, is_arabic)
            else:
                response = "من فضلك حدد السنة الدراسية التي تريد معرفة موادها." if is_arabic else "Please specify which year's courses you want to know about."
        else:
            # For other types of queries, return the content as is or a default message
            response = content if content else "المعلومات غير متوفرة في الوثيقة." if is_arabic else "Information not available in the document."

        return {
            "response": response,
            "model": model,
            "tokens_used": len(content.split()) + len(query.split()),
            "conversation_id": None
        }

# Global response generator instance
response_generator = ResponseGenerator()