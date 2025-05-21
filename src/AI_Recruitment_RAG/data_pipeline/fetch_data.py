import aiohttp
import asyncio
from datetime import datetime, timedelta
from ..config.config_loader import load_configs

config, params, _ = load_configs()

async def fetch_data():
    """Fetches latest Federal Register documents based on configuration."""
    base_url = config['api']['federal_register']['base_url']
    batch_size = params['data_pipeline']['fetch']['batch_size']
    date_range = params['data_pipeline']['fetch']['date_range_days']
    timeout = params['api']['request']['timeout']

    # Calculate date range
    from_date = (datetime.now() - timedelta(days=date_range)).strftime('%Y-%m-%d')
    
    request_params = {
        "conditions[publication_date][gte]": from_date,
        "order": "newest",
        "per_page": batch_size,
    }

    try:
        timeout_config = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_config) as session:
            async with session.get(base_url, params=request_params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"❌ Error fetching data: {response.status}")
                    return None
    except Exception as e:
        print(f"❌ Error during fetch: {str(e)}")
        return None