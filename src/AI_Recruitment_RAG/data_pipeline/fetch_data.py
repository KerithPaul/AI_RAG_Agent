import aiohttp
import asyncio
from datetime import datetime, timedelta
from src.AI_Recruitment_RAG.data_pipeline.process_data import logger
from ..config.config_loader import load_configs

config, params, _ = load_configs()

async def fetch_data():
    """Fetches latest Federal Register documents based on configuration."""
    base_url = config['api']['federal_register']['base_url']
    batch_size = params['data_pipeline']['fetch']['batch_size']
    date_range = params['data_pipeline']['fetch']['date_range_days']
    max_retries = config['api']['federal_register']['max_retries']
    
    # Calculate date range
    from_date = (datetime.now() - timedelta(days=date_range)).strftime('%Y-%m-%d')
    
    request_params = {
        "conditions[publication_date][gte]": from_date,
        "order": "newest",
        "per_page": batch_size,
    }

    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(base_url, params=request_params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"API error: {response.status}")
                        
        except aiohttp.ClientError as e:
            logger.error(f"Request error (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
    return None