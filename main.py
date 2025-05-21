import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
from src.AI_Recruitment_RAG.data_pipeline.fetch_data import fetch_data
from src.AI_Recruitment_RAG.data_pipeline.process_data import clean_data
from src.AI_Recruitment_RAG.data_pipeline.store_data import store_data_to_mysql
from src.AI_Recruitment_RAG.config.config_loader import load_configs

# Load configurations
config, params, _ = load_configs()

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

async def fetch_and_store_data():
    """Fetches data from Federal Register API and stores in MySQL"""
    try:
        # Fetch data
        logger.info("Fetching data from Federal Register API...")
        raw_data = await fetch_data()
        if raw_data is None:
            logger.error("Failed to fetch data from API")
            return False

        # Process data
        logger.info("Processing fetched data...")
        cleaned_data = clean_data(raw_data)
        if cleaned_data.empty:
            logger.error("No valid data after cleaning")
            return False

        # Store in database
        logger.info("Storing data in MySQL...")
        await store_data_to_mysql(cleaned_data)
        logger.info("Data pipeline completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    # Run the data pipeline
    success = asyncio.run(fetch_and_store_data())
    
    if success:
        logger.info("Initial data load completed successfully")
    else:
        logger.error("Initial data load failed")