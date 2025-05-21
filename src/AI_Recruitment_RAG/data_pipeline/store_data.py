import aiomysql
import asyncio
import pandas as pd
from ..config.config_loader import load_configs

config, _, schema = load_configs()

async def store_data_to_mysql(cleaned_data):
    """Stores processed Federal Register data into MySQL."""
    db_config = config['database']
    table_schema = schema['tables']['executive_documents']
    
    try:
        conn = await aiomysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            db=db_config['db_name'],
            charset=db_config['charset'],
            port=db_config['port']
        )
        
        async with conn.cursor() as cur:
            for _, row in cleaned_data.iterrows():
                await cur.execute(
                    f"""
                    INSERT INTO {table_schema['name']} 
                    (title, publication_date, abstract, document_number, url) 
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (row["title"], row["publication_date"], row["abstract"], 
                     row["document_number"], row["url"])
                )
            await conn.commit()
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()