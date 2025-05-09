#!/usr/bin/env python
"""
Script to export MongoDB data for model training.
"""
from app.database import mongodb
from loguru import logger

def main():
    """Export data for training"""
    try:
        logger.info("Starting data export process...")
        
        # Export data to JSONL file
        output_file = mongodb.export_to_dataset()
        
        logger.info(f"Data exported successfully to {output_file}")
        logger.info("You can now use this file for model training")
        
    except Exception as e:
        logger.error(f"Error during data export: {e}")

if __name__ == "__main__":
    main() 