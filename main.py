import asyncio
import aiomysql
import logging
from pathlib import Path
from datetime import datetime, timedelta
from src.AI_Recruitment_RAG.data_pipeline.fetch_data import fetch_data
from src.AI_Recruitment_RAG.data_pipeline.process_data import clean_data
from src.AI_Recruitment_RAG.data_pipeline.store_data import store_data_to_mysql, db_config
from src.AI_Recruitment_RAG.config.config_loader import load_configs
from src.AI_Recruitment_RAG.agent.llm_interface import query_llm
from src.AI_Recruitment_RAG.data_pipeline.fetch_data import fetch_data, verify_data_coverage

# Load configurations
config, _, _ = load_configs()

def setup_logging():
    """Configure logging with both file and console handlers"""
    # Create logs directory
    log_dir = Path(__file__).parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    log_file = log_dir / 'system.log'
    
    # Create formatter
    formatter = logging.Formatter(
        config['logging']['format']
    )
    
    # Setup file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Get logger
    logger = logging.getLogger('RAG_Agent')
    logger.setLevel(config['logging']['level'])
    
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


async def verify_data_range():
    """Verify the data range in the database"""
    try:
        conn = await aiomysql.connect(**db_config)
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT 
                    MIN(publication_date) as oldest_record,
                    MAX(publication_date) as newest_record,
                    COUNT(*) as total_records
                FROM executive_documents
            """)
            result = await cur.fetchone()
            if result:
                logger.info(f"Data range: {result[0]} to {result[1]}")
                logger.info(f"Total records: {result[2]}")
    except Exception as e:
        logger.error(f"Data verification error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()



if __name__ == "__main__":
    import uvicorn
    from src.AI_Recruitment_RAG.api import app

    # Check data coverage
    coverage_info = asyncio.run(verify_data_coverage())
    
    if coverage_info:
        if coverage_info['coverage_percent'] < 100:
            logger.warning("Incomplete data coverage detected")
            logger.warning(f"Current coverage: {coverage_info['coverage_percent']:.2f}%")
            logger.warning(f"Missing {coverage_info['missing_docs']} documents")
            logger.warning(f"Date range: {coverage_info['start_date']} to {coverage_info['end_date']}")
    
    # Run initial data pipeline
    asyncio.run(fetch_and_store_data())
    
    # Verify data range
    asyncio.run(verify_data_range())
    
    # Start the FastAPI server
    uvicorn.run(
        app,
        host=config['api']['server']['host'],
        port=config['api']['server']['port'],
        log_level="info",
        ws="websockets"
    )