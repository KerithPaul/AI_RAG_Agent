import yaml
from pathlib import Path
import logging

logger = logging.getLogger('RAG_Agent')

def load_configs():
    
    try:
        base_path = Path(__file__).parent.parent.parent.parent

    
        config_path = base_path / 'config' / 'config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded config.yaml from {config_path}")


        params_path = base_path / 'params.yaml'
        with open(params_path, 'r', encoding='utf-8') as f:
            params = yaml.safe_load(f)
        logger.info(f"Loaded params.yaml from {params_path}")

    
        schema_path = base_path / 'schema.yaml'
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = yaml.safe_load(f)
        logger.info(f"Loaded schema.yaml from {schema_path}")

        return config, params, schema
    

    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {str(e)}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading configurations: {str(e)}")
        raise