import json
import aiomysql
import logging
from ..config.config_loader import load_configs

logger = logging.getLogger('RAG_Agent')
config, _, _ = load_configs()

async def search_documents(start_date, end_date, keywords=None):
    """Search executive documents in the database."""
    try:
        conn = await aiomysql.connect(
            host=config['database']['host'],
            user=config['database']['user'],
            password=config['database']['password'],
            db=config['database']['db_name'],
            charset=config['database']['charset'],
            port=config['database']['port']
        )
        
        async with conn.cursor(aiomysql.DictCursor) as cur:
            query = """
                SELECT title, publication_date, abstract, document_number, url 
                FROM executive_documents 
                WHERE publication_date BETWEEN %s AND %s
            """
            params = [start_date, end_date]
            
            if keywords:
                query += " AND MATCH(title, abstract) AGAINST(%s IN NATURAL LANGUAGE MODE)"
                params.append(keywords)
            
            await cur.execute(query, params)
            results = await cur.fetchall()
            
            return json.dumps({"documents": results}, default=str)
    finally:
        if 'conn' in locals():
            conn.close()

from datetime import datetime, timedelta

def get_date_range(days=7):
    """Calculate date range for queries"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

async def execute_tool_call(tool_call):
    """Execute the appropriate tool based on the LLM's request."""
    if not tool_call:
        return "No tool call received"

    try:
        if tool_call["name"] == "search_documents":
            # Get default date range if not specified
            start_date, end_date = get_date_range()
            
            args = tool_call["arguments"]
            return await search_documents(
                args.get("start_date", start_date),
                args.get("end_date", end_date),
                args.get("keywords", "healthcare")
            )
        
        return "Invalid tool request"

    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        return str(e)