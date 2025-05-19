"""
Palantir Foundry Template Module
--------------------------------
This template demonstrates best practices for code that will run in Palantir Foundry.
It includes patterns for:
- Function definition matching YAML configuration
- Proper error handling and logging
- Working with Spark DataFrames
- Handling secrets

USAGE:
1. Configure the corresponding function.yml with appropriate parameters
2. Implement the business logic in the main function
3. Test locally before deploying to Foundry
"""

import logging
import os
import sys
from typing import Dict, List, Optional, Any

# Standard libraries for data processing
import pandas as pd
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_TIMEOUT = 30  # seconds

def get_secret(secret_name: str) -> str:
    """
    Get a secret from the environment or Foundry secrets.
    In Foundry, secrets are injected as environment variables.
    
    Args:
        secret_name: Name of the secret
        
    Returns:
        The secret value
        
    Raises:
        ValueError: If the secret is not found
    """
    # In Foundry, secrets are provided as environment variables
    secret_value = os.environ.get(secret_name)
    
    if not secret_value:
        raise ValueError(f"Secret {secret_name} not found. Ensure it's configured in Foundry.")
    
    return secret_value

def retry_with_backoff(func, max_retries=3, initial_backoff=1):
    """
    Retry a function with exponential backoff
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_backoff: Initial backoff time in seconds
        
    Returns:
        The result of the function
        
    Raises:
        Exception: If all retries fail
    """
    import time
    
    retries = 0
    while True:
        try:
            return func()
        except Exception as e:
            retries += 1
            if retries > max_retries:
                logger.error(f"Max retries ({max_retries}) exceeded. Last error: {str(e)}")
                raise
            
            # Exponential backoff
            wait_time = initial_backoff * (2 ** (retries - 1))
            logger.warning(f"Attempt {retries} failed. Retrying in {wait_time} seconds. Error: {str(e)}")
            time.sleep(wait_time)

def process_data(spark, input_df, param1: str, param2: Optional[int] = None) -> Any:
    """
    Main entry point for Foundry function.
    This function will be referenced in the function.yml file.
    
    Args:
        spark: Spark session provided by Foundry
        input_df: Input DataFrame provided by Foundry
        param1: First parameter from function configuration
        param2: Optional second parameter
        
    Returns:
        Processed data in the format expected by Foundry
    """
    logger.info(f"Starting data processing with param1={param1}, param2={param2}")
    
    try:
        # Validate inputs
        if input_df is None or input_df.count() == 0:
            logger.warning("Input DataFrame is empty")
            return spark.createDataFrame(pd.DataFrame())
        
        # Get secrets if needed
        try:
            api_key = get_secret("MY_API_KEY")
            logger.info("Successfully retrieved API key")
        except ValueError as e:
            logger.error(f"Failed to get secret: {str(e)}")
            raise
        
        # Process data (example)
        # Note: Use Spark operations for large datasets
        logger.info(f"Processing DataFrame with {input_df.count()} rows")
        
        # Example: Convert Spark DataFrame to pandas for processing
        # Only do this for small datasets that fit in memory
        pandas_df = input_df.toPandas()
        
        # Perform data transformations (example)
        result_df = pandas_df.copy()
        if param2:
            result_df = result_df[result_df['value'] > param2]
        
        # Add a column based on external API call (example)
        def call_external_api(row_id):
            """Make API call with retry logic"""
            def _api_call():
                response = requests.get(
                    f"https://api.example.com/data/{row_id}",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=DEFAULT_TIMEOUT
                )
                response.raise_for_status()
                return response.json()
            
            # Use retry logic for the API call
            return retry_with_backoff(_api_call)
        
        # Only process a sample of rows during testing
        sample_size = min(100, len(result_df))
        logger.info(f"Processing sample of {sample_size} rows for API enrichment")
        
        # Apply the API call to the first N rows (for testing)
        # In production, you might process all rows or use batching
        sample_df = result_df.head(sample_size)
        
        try:
            # This is just an example - in production you might use more efficient approaches
            sample_df['api_data'] = sample_df['id'].apply(call_external_api)
            result_df = pd.concat([sample_df, result_df.iloc[sample_size:]])
        except Exception as e:
            logger.error(f"API enrichment failed: {str(e)}")
            # Continue with unenriched data rather than failing
            result_df['api_data'] = None
        
        # Convert back to Spark DataFrame for return
        return spark.createDataFrame(result_df)
    
    except Exception as e:
        logger.error(f"Data processing failed: {str(e)}", exc_info=True)
        raise

def main():
    """
    Local testing entry point.
    This function is not called when running in Foundry.
    """
    # Create mock data for local testing
    import numpy as np
    from pyspark.sql import SparkSession
    
    # Create a local spark session for testing
    spark = SparkSession.builder \
        .appName("FoundryTemplateTest") \
        .master("local[1]") \
        .getOrCreate()
    
    # Create sample data
    data = {
        'id': [f"id{i}" for i in range(1, 11)],
        'value': np.random.randint(1, 100, 10),
        'category': np.random.choice(['A', 'B', 'C'], 10)
    }
    df = pd.DataFrame(data)
    spark_df = spark.createDataFrame(df)
    
    # Set environment variables for local testing
    os.environ['MY_API_KEY'] = 'dummy_api_key_for_testing'
    
    # Process the data
    result = process_data(spark, spark_df, "test_param", 50)
    
    print(f"Processed {result.count()} rows")
    result.show()
    
    # Clean up
    spark.stop()

if __name__ == "__main__":
    # This code only runs during local testing, not in Foundry
    main() 