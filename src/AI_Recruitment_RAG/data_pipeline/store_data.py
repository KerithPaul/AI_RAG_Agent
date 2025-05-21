import aiomysql
import pandas as pd
from datetime import datetime
from ..config.config_loader import load_configs
from src.AI_Recruitment_RAG.data_pipeline.process_data import logger

config, _, schema = load_configs()

db_config = {
    'host': config['database']['host'],
    'user': config['database']['user'],
    'password': config['database']['password'],
    'db': config['database']['database'],
    'charset': config['database']['charset'],
    'port': config['database']['port']
}

async def store_data_to_mysql(cleaned_data):
    """Stores processed Federal Register data into MySQL"""
    conn = None
    try:
        conn = await aiomysql.connect(**db_config)
        
        async with conn.cursor() as cur:
            # Create pipeline_status table if not exists
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_status (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    last_run TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    documents_processed INT,
                    status VARCHAR(50),
                    error_message TEXT
                )
            """)
            
            # Insert records
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
                except Exception as e:
                    logger.error(f"Error inserting row: {str(e)}")
            
            # Update pipeline status
            await cur.execute("""
                INSERT INTO pipeline_status 
                (documents_processed, status) 
                VALUES (%s, %s)
            """, (successful_inserts, "success"))
            
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