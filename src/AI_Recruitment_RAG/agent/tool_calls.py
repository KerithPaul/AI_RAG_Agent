import json
from ..config.config_loader import load_configs

def get_tool_schema():
    """Defines available tools for the LLM."""
    tools = [
        {
            "name": "fetch_executive_documents",
            "description": "Fetches executive documents from MySQL based on a date range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_range": {
                        "type": "string",
                        "description": "Date range in format 'YYYY-MM-DD'"
                    }
                },
                "required": ["date_range"]
            }
        }
    ]
    return json.dumps(tools)