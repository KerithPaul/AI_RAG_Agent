import asyncio
import logging
import os
from pathlib import Path
from src.AI_Recruitment_RAG.data_pipeline.fetch_data import fetch_data
from src.AI_Recruitment_RAG.data_pipeline.process_data import clean_data
from src.AI_Recruitment_RAG.data_pipeline.store_data import store_data_to_mysql
from src.AI_Recruitment_RAG.config.config_loader import load_configs

def setup_logging():
    """Configure logging with both file and console handlers"""
    # Create logs directory
    log_dir = Path(__file__).parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    log_file = log_dir / 'system.log'
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Get logger
    logger = logging.getLogger('RAG_Agent')
    logger.setLevel(logging.INFO)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Initialize logging
logger = setup_logging()

async def run_pipeline():
    """Executes the full data pipeline: fetch, clean, and store."""
    try:
        logger.info("Starting data pipeline...")
        raw_data = await fetch_data()
        if raw_data is None:
            logger.error("Failed to fetch data")
            return
        
        logger.info("Cleaning data...")
        cleaned_data = clean_data(raw_data)
        if cleaned_data.empty:
            logger.error("No valid data available after cleaning")
            return
        
        logger.info("Storing data to MySQL...")
        await store_data_to_mysql(cleaned_data)
        logger.info("Data pipeline executed successfully!")
        
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(run_pipeline())