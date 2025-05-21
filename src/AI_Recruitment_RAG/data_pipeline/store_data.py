import aiomysql
import pandas as pd
from datetime import datetime
from ..config.config_loader import load_configs
from src.AI_Recruitment_RAG.data_pipeline.process_data import logger

config, _, schema = load_configs()

async def store_data_to_mysql(cleaned_data):
    """Stores processed Federal Register data into MySQL."""
    conn = None
    cur = None
    db_config = config['database']
    
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
            # Insert records one by one to handle errors better
            successful_inserts = 0
            
            for _, row in cleaned_data.iterrows():
                try:
                    await cur.execute("""
                        INSERT INTO executive_documents 
                        (title, publication_date, abstract, document_number, url)
                        VALUES (%s, %s, %s, %s, %s)
                        AS new_data
                        ON DUPLICATE KEY UPDATE
                        title = new_data.title,
                        abstract = new_data.abstract,
                        url = new_data.url
                    """, (
                        row["title"],
                        row["publication_date"],
                        row["abstract"],
                        row["document_number"],
                        row["url"]
                    ))
                    successful_inserts += 1
                except Exception as row_error:
                    logger.error(f"Error inserting row: {str(row_error)}")
                    continue
            
            # Update pipeline metadata in a separate transaction
            await cur.execute("""
                INSERT INTO pipeline_metadata 
                (last_run, records_processed, status)
                VALUES (%s, %s, %s)
            """, (
                datetime.now(),
                successful_inserts,
                'success' if successful_inserts > 0 else 'partial_success'
            ))
            
            await conn.commit()
            return successful_inserts
            
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        if conn:
            await conn.rollback()
        raise
    finally:
        if conn:
            conn.close()