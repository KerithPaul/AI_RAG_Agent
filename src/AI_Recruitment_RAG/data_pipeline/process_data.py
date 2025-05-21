import pandas as pd
import logging
from ..config.config_loader import load_configs

_, params, schema = load_configs()
logger = logging.getLogger('RAG_Agent')

def clean_data(raw_data):
    """Transforms raw JSON response into a structured pandas dataframe."""
    if "results" not in raw_data:
        logger.error("No 'results' key in API response")
        return pd.DataFrame()

    df = pd.DataFrame(raw_data["results"])
    
    # Map Federal Register API fields to our schema
    field_mapping = {
        'title': 'title',
        'abstract': 'abstract',
        'document_number': 'document_number',
        'publication_date': 'publication_date',
        'html_url': 'url'  # Federal Register API uses html_url for the URL field
    }
    
    # Rename columns according to mapping
    df = df.rename(columns=field_mapping)
    
    # Get expected columns from schema
    expected_columns = [col for col in schema['tables']['executive_documents']['columns'] 
                       if col != 'id']
    
    # Check for missing columns
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        logger.warning(f"Missing columns in API response: {missing_columns}")
        # Add missing columns with None values
        for col in missing_columns:
            df[col] = None
    
    # Select only the columns we need
    df = df[expected_columns]
    
    # Apply processing parameters
    chunk_size = params['data_pipeline']['processing']['chunk_size']
    df = df.head(chunk_size)
    
    # Remove rows with any NULL values
    df_cleaned = df.dropna()
    
    if df_cleaned.empty:
        logger.error("No valid data after cleaning")
        return pd.DataFrame()
        
    logger.info(f"Successfully cleaned {len(df_cleaned)} records")
    return df_cleaned