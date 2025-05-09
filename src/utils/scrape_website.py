#!/usr/bin/env python
"""
Script to scrape the university website and store content in MongoDB.
"""
from app.web_scraper import web_scraper
from loguru import logger

def main():
    """Main function to run the web scraper"""
    try:
        logger.info("Starting website scraping process...")
        web_scraper.scrape_website()
        logger.info("Website scraping completed successfully!")
    except Exception as e:
        logger.error(f"Error during website scraping: {e}")

if __name__ == "__main__":
    main() 