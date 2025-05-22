import aiohttp
import aiomysql
import asyncio
from datetime import datetime, timedelta
from src.AI_Recruitment_RAG.data_pipeline.process_data import logger
from ..config.config_loader import load_configs
from src.AI_Recruitment_RAG.data_pipeline.store_data import db_config

config, params, _ = load_configs()


async def fetch_page(session, url, params, retry=0):

    try:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            elif retry < config['data_pipeline']['fetch']['max_retries']:
                await asyncio.sleep(config['data_pipeline']['fetch']['retry_delay'])
                return await fetch_page(session, url, params, retry + 1)
            else:
                logger.error(f"Failed to fetch page after {retry} retries")
                return None
    except Exception as e:
        logger.error(f"Error fetching page: {str(e)}")
        return None
    

async def fetch_data():
    """Fetches Federal Register documents for date range with pagination"""
    try:
        # Get configuration
        fetch_config = config['data_pipeline']['fetch']
        base_url = fetch_config['api_url']
        per_page = config['data_pipeline']['pagination']['per_page']
        
        # Set up date range
        start_date = datetime.strptime(fetch_config['start_date'], '%Y-%m-%d')
        end_date = datetime.now()
        
        all_results = []
        current_page = 1
        
        async with aiohttp.ClientSession() as session:
            while True:
                params = {
                    "conditions[publication_date][gte]": start_date.strftime('%Y-%m-%d'),
                    "conditions[publication_date][lte]": end_date.strftime('%Y-%m-%d'),
                    "per_page": per_page,
                    "page": current_page,
                    "order": "oldest"
                }
                
                async with session.get(base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get('results', [])
                        
                        if not results:
                            break
                            
                        all_results.extend(results)
                        total_count = data.get('count', 0)
                        
                        logger.info(f"Fetched page {current_page} with {len(results)} documents")
                        logger.info(f"Total documents fetched so far: {len(all_results)}/{total_count}")
                        
                        if len(all_results) >= total_count:
                            break
                            
                        current_page += 1
                    else:
                        logger.error(f"API request failed with status {response.status}")
                        return None
                        
                # Add a small delay to avoid rate limiting
                await asyncio.sleep(1)
        
        logger.info(f"Successfully fetched total of {len(all_results)} documents")
        return {"results": all_results, "count": len(all_results)}
                    
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        return None
    


async def verify_data_coverage():
    """Verifies data coverage from 2025-01-01"""
    try:
        fetch_config = config['data_pipeline']['fetch']
        base_url = fetch_config['api_url']
        
        params = {
            "conditions[publication_date][gte]": fetch_config['start_date'],
            "conditions[publication_date][lte]": datetime.now().strftime('%Y-%m-%d'),
            "per_page": 1
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    total_expected = data.get('count', 0)

                    conn = await aiomysql.connect(**db_config)
                    async with conn.cursor() as cur:
                        await cur.execute("""
                            SELECT COUNT(*) as doc_count
                            FROM executive_documents
                            WHERE publication_date >= %s
                            AND publication_date <= %s
                        """, (fetch_config['start_date'], datetime.now().strftime('%Y-%m-%d')))
                        
                        result = await cur.fetchone()
                        current_count = result[0] if result else 0  
                    
                    coverage_info = {
                        "expected_count": total_expected,
                        "current_count": current_count,
                        "coverage_percent": (current_count / total_expected * 100) if total_expected > 0 else 0,
                        "missing_docs": total_expected - current_count,
                        "start_date": fetch_config['start_date'],
                        "end_date": datetime.now().strftime('%Y-%m-%d')
                    }
                    
                    logger.info(f"Expected documents from API: {coverage_info['expected_count']}")
                    return coverage_info
                    
    except Exception as e:
        logger.error(f"Error verifying data coverage: {str(e)}")
        return None