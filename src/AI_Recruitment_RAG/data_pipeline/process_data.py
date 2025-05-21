import pandas as pd
import logging
from datetime import datetime
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
        'html_url': 'url'
    }
    
    # Rename columns
    df = df.rename(columns=field_mapping)
    
    # Validate required columns
    required_columns = ['title', 'publication_date', 'abstract', 'document_number', 'url']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"Missing required columns: {missing_columns}")
        return pd.DataFrame()
    
    # Data type conversions
    df['publication_date'] = pd.to_datetime(df['publication_date']).dt.date
    
    # Clean text fields
    text_columns = ['title', 'abstract']
    for col in text_columns:
        df[col] = df[col].str.strip()
    
    # Remove invalid records
    df = df.dropna(subset=required_columns)
    
    # Apply size limits from params
    chunk_size = params['data_pipeline']['processing']['chunk_size']
    df = df.head(chunk_size)
    
    logger.info(f"Processed {len(df)} records successfully")
    return df