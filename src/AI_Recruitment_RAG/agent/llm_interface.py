import logging
import ollama
from ..config.config_loader import load_configs
from .tool_calls import get_tool_schema
from .execute_tools import execute_tool_call

logger = logging.getLogger('RAG_Agent')
config, _, _ = load_configs()

async def query_llm(user_query):
    """Process user queries through LLM and execute tool calls."""
    try:
        # Get LLM configuration
        llm_config = config['llm']
        
        # Create messages for the LLM
        messages = [
            {
                "role": "system",
                "content": """You are an AI assistant with access to a database of executive documents.
                To search for documents, you MUST use the search_documents tool.
                DO NOT suggest or write code. Instead, use the provided tool to search the database.
                
                The search_documents tool requires:
                - start_date: Date in YYYY-MM-DD format
                - end_date: Date in YYYY-MM-DD format
                - keywords: Optional search terms
                
                After getting results, summarize them in a clear, organized way."""
            },
            {"role": "user", "content": user_query}
        ]

        try:
            # Create Ollama client
            client = ollama.Client(host='http://localhost:11434')
            
            # Query the LLM
            response = client.chat(
                model=llm_config['model'],
                messages=messages,
                options={
                    "temperature": float(llm_config['temperature']),
                    "num_predict": int(llm_config['max_tokens'])
                }
            )
            
            logger.info("LLM query successful")
            
            # Handle tool calls if present
            if hasattr(response, 'tool_calls') and response.tool_calls:
                tool_result = await execute_tool_call(response.tool_calls[0])
                
                # Send tool result back to LLM for final response
                final_response = client.chat(
                    model=llm_config['model'],
                    messages=[*messages, {
                        "role": "function",
                        "content": tool_result
                    }]
                )
                return final_response.message['content']
            
            return response.message['content']
                
        except ConnectionError:
            logger.error("Cannot connect to Ollama. Please ensure Ollama is running")
            raise
            
    except Exception as e:
        logger.error(f"Error in LLM query: {str(e)}")
        raise