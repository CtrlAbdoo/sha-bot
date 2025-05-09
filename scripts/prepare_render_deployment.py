#!/usr/bin/env python
"""
Utility script to prepare the application for deployment on Render.com
This script ensures the data directory exists and creates an empty simulation file if needed
"""
import os
import json
import sys

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import app modules
from loguru import logger

def prepare_for_render():
    """Prepare the application for deployment on Render.com"""
    
    # Set up logging
    logger.add("logs/render_deployment.log", rotation="1 day", retention="7 days", level="INFO")
    logger.info("Preparing application for Render.com deployment")
    
    # Get the data directory path
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    
    # Create the data directory if it doesn't exist
    if not os.path.exists(data_dir):
        logger.info(f"Creating data directory: {data_dir}")
        os.makedirs(data_dir, exist_ok=True)
    
    # Create the logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    if not os.path.exists(logs_dir):
        logger.info(f"Creating logs directory: {logs_dir}")
        os.makedirs(logs_dir, exist_ok=True)
    
    # Check if the simulation file exists
    simulation_file = os.path.join(data_dir, "finetuned_simulation.json")
    if not os.path.exists(simulation_file):
        logger.warning(f"Simulation file not found: {simulation_file}")
        logger.info("Creating empty simulation file")
        
        # Create an empty simulation file
        with open(simulation_file, "w", encoding="utf-8") as f:
            json.dump({}, f)
        
        # Add a message about uploading the real file
        logger.warning(
            "Empty simulation file created. You will need to upload the real "
            "simulation file to Render.com disk or configure cloud storage."
        )
    else:
        logger.info(f"Simulation file found: {simulation_file}")
    
    logger.info("Preparation completed successfully")
    return True

if __name__ == "__main__":
    success = prepare_for_render()
    sys.exit(0 if success else 1) 