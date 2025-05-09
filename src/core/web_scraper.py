"""
Web scraper module for extracting content from the university website.
"""
import os
import re
from typing import List, Dict, Any
from urllib.parse import urljoin, urlencode

import requests
from bs4 import BeautifulSoup
from loguru import logger
from PyPDF2 import PdfReader
import io
import urllib3

from app.config import settings
from app.database import mongodb

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WebScraper:
    """Web scraper for university website"""
    
    def __init__(self, base_url: str = "https://sha.edu.eg/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        # Disable SSL verification
        self.session.verify = False
        
        # Keywords to look for in links and content
        self.keywords = [
            "computer", "cs", "حاسب", "كمبيوتر",
            "curriculum", "courses", "subjects", "study",
            "المناهج", "المقررات", "المواد", "الدراسة",
            "portal", "student", "elearning", "moodle",
            "بوابة", "طالب", "تعليم"
        ]
        
        # CS Department URLs
        self.cs_urls = [
            "https://hicit.sha.edu.eg/department.php?id=1",  # Main CS department page
            "https://hicit.sha.edu.eg/",  # Institute homepage
            "https://hicit.sha.edu.eg/FAQ.php"  # FAQ page
        ]
    
    def get_page_content(self, url: str) -> str:
        """Get content from a webpage"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return ""
    
    def extract_links(self, html_content: str) -> List[str]:
        """Extract all links from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        # Add CS department URLs
        links.extend(self.cs_urls)
        
        # Look for links containing our keywords
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            text = a_tag.text.lower()
            
            # Convert relative URLs to absolute
            full_url = urljoin(self.base_url, href)
            
            # Check if the link or its text contains any of our keywords
            if any(keyword in href.lower() or keyword in text for keyword in self.keywords):
                links.append(full_url)
            elif full_url.startswith(self.base_url) or full_url.startswith("https://hicit.sha.edu.eg/"):
                links.append(full_url)
        
        return list(set(links))  # Remove duplicates
    
    def extract_text_content(self, html_content: str) -> str:
        """Extract text content from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_course_info(self, html_content: str) -> Dict[str, Any]:
        """Extract structured course information"""
        soup = BeautifulSoup(html_content, 'html.parser')
        course_info = {
            "title": "",
            "description": "",
            "year": "",
            "semester": "",
            "credits": "",
            "prerequisites": []
        }
        
        # Look for course information in tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['th', 'td'])
                if len(cells) >= 2:
                    key = cells[0].text.strip().lower()
                    value = cells[1].text.strip()
                    
                    # Match both English and Arabic keywords
                    if any(year_key in key for year_key in ["year", "السنة", "الفرقة"]):
                        course_info["year"] = value
                    elif any(sem_key in key for sem_key in ["semester", "الفصل"]):
                        course_info["semester"] = value
                    elif any(credit_key in key for credit_key in ["credit", "ساعات"]):
                        course_info["credits"] = value
                    elif any(prereq_key in key for prereq_key in ["prerequisite", "المتطلبات"]):
                        course_info["prerequisites"] = [p.strip() for p in value.split(",")]
        
        # Look for course titles in headings
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            text = heading.text.strip()
            if any(keyword in text.lower() for keyword in self.keywords):
                course_info["title"] = text
                break
        
        return course_info
    
    def download_pdf(self, url: str) -> str:
        """Download and extract text from PDF"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Read PDF from response content
            pdf_file = io.BytesIO(response.content)
            reader = PdfReader(pdf_file)
            
            # Extract text from each page
            content = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    content.append(text)
            
            return "\n\n".join(content)
        except Exception as e:
            logger.error(f"Error processing PDF from {url}: {e}")
            return ""
    
    def scrape_website(self) -> None:
        """Main method to scrape the website"""
        logger.info(f"Starting to scrape {self.base_url}")
        
        # Get main page content
        main_content = self.get_page_content(self.base_url)
        if not main_content:
            logger.error("Failed to fetch main page")
            return
        
        # Extract and process all links
        links = self.extract_links(main_content)
        logger.info(f"Found {len(links)} links to process")
        
        # Process each link
        for i, link in enumerate(links, 1):
            try:
                logger.info(f"Processing link {i}/{len(links)}: {link}")
                
                if link.lower().endswith('.pdf'):
                    # Handle PDF files
                    content = self.download_pdf(link)
                    doc_id = f"pdf_{i}"
                    doc_type = "pdf"
                    metadata = {}
                else:
                    # Handle web pages
                    html_content = self.get_page_content(link)
                    content = self.extract_text_content(html_content)
                    doc_id = f"web_{i}"
                    doc_type = "webpage"
                    
                    # Try to extract course information if the URL or content seems relevant
                    if any(keyword in link.lower() or keyword in content.lower() for keyword in self.keywords):
                        metadata = self.extract_course_info(html_content)
                    else:
                        metadata = {}
                
                if content:
                    # Store in MongoDB
                    mongodb.collection.update_one(
                        {"_id": doc_id},
                        {
                            "$set": {
                                "content": content,
                                "source_url": link,
                                "type": doc_type,
                                "metadata": metadata,
                                "keywords": [k for k in self.keywords if k in content.lower()]
                            }
                        },
                        upsert=True
                    )
                    logger.info(f"Successfully stored content from {link}")
                
            except Exception as e:
                logger.error(f"Error processing {link}: {e}")
                continue
        
        logger.info("Website scraping completed")

# Create global scraper instance
web_scraper = WebScraper() 