"""
Document processor module for extracting relevant content from documents.
"""
from loguru import logger


class DocumentProcessor:
    """Handles extraction of relevant content from document text"""
    
    @staticmethod
    def extract_relevant_section(content: str, query: str) -> str:
        """
        Extract relevant section from document content based on query.
        
        Args:
            content: The full document content
            query: The user query
            
        Returns:
            Extracted relevant section
        """
        lines = content.split("\n")
        relevant_lines = []
        seen_courses = set()  # To track unique courses
        in_relevant_section = False
        
        # Keywords for year detection
        year_keywords = {
            "الفرقة الثانية": "level 2",
            "الفرقة الثانيه": "level 2",
            "السنة الثانية": "level 2",
            "المستوى الثاني": "level 2",
            "second year": "level 2",
            "level 2": "level 2",
            "الفرقة الأولى": "level 1",
            "الفرقة الاولى": "level 1",
            "السنة الأولى": "level 1",
            "المستوى الأول": "level 1",
            "first year": "level 1",
            "level 1": "level 1",
            "الفرقة الثالثة": "level 3",
            "الفرقة الثالثه": "level 3",
            "السنة الثالثة": "level 3",
            "المستوى الثالث": "level 3",
            "third year": "level 3",
            "level 3": "level 3",
            "الفرقة الرابعة": "level 4",
            "الفرقة الرابعه": "level 4",
            "السنة الرابعة": "level 4",
            "المستوى الرابع": "level 4",
            "المقررات الدراسية للفرقة الرابعة": "level 4",
            "fourth year": "level 4",
            "level 4": "level 4"
        }

        # Keywords for course-related content
        course_keywords = ["مواد", "المقررات", "المواد الدراسية", "courses", "subjects"]
        
        # Detect target year from query
        target_year = None
        for keyword, level in year_keywords.items():
            if keyword in query.lower():
                target_year = level
                break
                
        # First try to find course listings
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for course section headers
            if target_year and line.lower().startswith(target_year.lower()):
                in_relevant_section = True
                relevant_lines.append(line)
                continue
            elif in_relevant_section and any(line.lower().startswith(level.lower()) for level in year_keywords.values()):
                in_relevant_section = False
                continue
                
            # Add course lines if we're in a course section
            if in_relevant_section:
                relevant_lines.append(line)

        # If no course listings found, try to find general content
        if not relevant_lines:
            logger.info("No course listings found, looking for general content")
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check if this line marks the start of a relevant section
                if target_year and target_year.lower() in line.lower():
                    in_relevant_section = True
                    relevant_lines.append(line)
                    continue
                    
                # Check if this line marks the end of the current section
                if in_relevant_section and any(year.lower() in line.lower() for year in year_keywords.values()):
                    in_relevant_section = False
                    continue

                # Add line if we're in a relevant section
                if in_relevant_section:
                    relevant_lines.append(line)

        # If still no relevant content found, try one more time with more flexible matching
        if not relevant_lines and target_year:
            logger.info("Trying more flexible matching")
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if target_year.lower() in line.lower():
                    relevant_lines.append(line)

        extracted_content = "\n".join(relevant_lines) if relevant_lines else content
        logger.debug(f"Extracted {len(relevant_lines)} relevant lines")
        return extracted_content


# Global document processor instance
document_processor = DocumentProcessor() 