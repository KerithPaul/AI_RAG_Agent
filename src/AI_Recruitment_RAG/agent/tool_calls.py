import json
from ..config.config_loader import load_configs

def get_tool_schema():
    """Defines available tools for the LLM."""
    tools = [
        {
            "name": "search_documents",
            "description": "Search executive documents in the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format"
                    },
                    "keywords": {
                        "type": "string",
                        "description": "Keywords to search in title and abstract"
                    }
                },
                "required": ["start_date", "end_date"]
            }
        }
    ]
    return json.dumps(tools)