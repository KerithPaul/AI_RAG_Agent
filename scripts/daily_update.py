import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import logging

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.AI_Recruitment_RAG.data_pipeline.fetch_data import fetch_data, verify_data_coverage
from src.AI_Recruitment_RAG.data_pipeline.process_data import clean_data
from src.AI_Recruitment_RAG.data_pipeline.store_data import store_data_to_mysql
from src.AI_Recruitment_RAG.config.config_loader import load_configs

# Setup logging
config, _, _ = load_configs()
log_dir = project_root / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    filename=log_dir / 'daily_update.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def run_daily_update():
    """Daily update of Federal Register documents"""
    try:
        logging.info("Starting daily update")
        
        # Check current coverage
        coverage = await verify_data_coverage()
        if coverage:
            logging.info(f"Current coverage: {coverage['coverage_percent']:.2f}%")
        
        # Fetch and process new data
        raw_data = await fetch_data()
        if raw_data:
            cleaned_data = clean_data(raw_data)
            if not cleaned_data.empty:
                await store_data_to_mysql(cleaned_data)
                logging.info(f"Successfully processed {len(cleaned_data)} documents")
                return True
        
        logging.error("Update failed - no data processed")
        return False
        
    except Exception as e:
        logging.error(f"Update failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(run_daily_update())