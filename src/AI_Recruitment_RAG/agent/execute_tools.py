import json
import aiomysql
import asyncio
import logging
from ..config.config_loader import load_configs

logger = logging.getLogger('RAG_Agent')
config, _, _ = load_configs()

async def fetch_executive_documents(date_range):
    """Fetches executive documents from MySQL based on a date range."""
    try:
        db_config = config['database']
        conn = await aiomysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            db=db_config['db_name'],
            charset=db_config['charset'],
            port=db_config['port']
        )
        
        async with conn.cursor(aiomysql.DictCursor) as cur:
            query = """
                SELECT title, publication_date, abstract, document_number, url 
                FROM executive_documents 
                WHERE publication_date >= %s
            """
            await cur.execute(query, (date_range,))
            results = await cur.fetchall()
            
            logger.info(f"Retrieved {len(results)} documents")
            return json.dumps({"documents": results}, default=str)

    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def execute_tool_call(tool_call):
    """Parses and executes tool calls from the LLM."""
    if not tool_call:
        return "No tool call received"

    try:
        if tool_call["name"] == "fetch_executive_documents":
            date_range = tool_call["arguments"]["date_range"]
            return asyncio.run(fetch_executive_documents(date_range))
        
        return "Invalid tool request"

    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        return str(e)