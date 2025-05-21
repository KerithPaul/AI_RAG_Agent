import logging
from ..config.config_loader import load_configs
from .tool_calls import get_tool_schema
from .execute_tools import execute_tool_call

logger = logging.getLogger('RAG_Agent')
config, _, _ = load_configs()

def query_llm(user_query):
    """Processes user queries through LLM and executes tool calls."""
    try:
        # Get LLM configuration
        llm_config = config['llm']
        
        # Create messages for the LLM
        messages = [
            {
                "role": "system",
                "content": "You are an AI assistant with access to a database of executive documents. Use the available tools to help answer queries."
            },
            {"role": "user", "content": user_query}
        ]

        # Import Ollama here to avoid conflicts
        import ollama

        # Create Ollama client
        client = ollama.Client()
        
        # Query the LLM with correct parameters
        response = client.chat(
            model=llm_config['model'],
            messages=messages,
            options={
                "temperature": float(llm_config['temperature']),
                "num_predict": int(llm_config['max_tokens'])
            }
        )

        logger.info("LLM query successful")
        
        # Handle tool calls if present in response
        if hasattr(response, 'tool_calls') and response.tool_calls:
            return execute_tool_call(response.tool_calls[0])
        else:
            return response.message['content']

    except Exception as e:
        logger.error(f"Error in LLM query: {str(e)}")
        raise