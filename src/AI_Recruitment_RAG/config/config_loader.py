import yaml
from pathlib import Path

def load_configs():
    """
    Load configuration from YAML files.
    Returns:
        tuple: (config, params, schema) dictionaries
    """
    try:
        base_path = Path(__file__).parent.parent.parent.parent

        # Load config.yaml
        config_path = base_path / 'config' / 'config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Load params.yaml
        params_path = base_path / 'params.yaml'
        with open(params_path, 'r', encoding='utf-8') as f:
            params = yaml.safe_load(f)

        # Load schema.yaml
        schema_path = base_path / 'schema.yaml'
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = yaml.safe_load(f)

        return config, params, schema

    except FileNotFoundError as e:
        print(f"❌ Configuration file not found: {str(e)}")
        raise
    except yaml.YAMLError as e:
        print(f"❌ Error parsing YAML file: {str(e)}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error loading configurations: {str(e)}")
        raise