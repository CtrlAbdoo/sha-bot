#!/usr/bin/env python
"""
Script to scrape computer science department information.
"""
from app.web_scraper import web_scraper
from loguru import logger

def main():
    """Main function to scrape CS department info"""
    try:
        logger.info("Starting CS department scraping process...")
        web_scraper.scrape_website()
        logger.info("CS department scraping completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during CS department scraping: {e}")

if __name__ == "__main__":
    main() 