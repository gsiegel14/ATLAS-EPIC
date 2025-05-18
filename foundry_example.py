"""
ATLAS Engine - Epic FHIR API Integration for Foundry
----------------------------------------------------
This example shows how to integrate with Epic's FHIR API in Foundry.
It demonstrates obtaining and refreshing OAuth tokens automatically.

SETUP INSTRUCTIONS:
1. Run setup_epic_auth.py once to save your private key
2. Import foundry_epic_auth.py in your Foundry transformation
3. Use the get_epic_auth_header function to get authorization headers
4. Include the header in your requests to Epic FHIR API
"""

import requests
from foundry_epic_auth import get_epic_auth_header, PRIVATE_KEY_FILE

# Configuration
EPIC_FHIR_BASE_URL = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"
USE_PRODUCTION = False  # Set to True for production environment

def get_patient(patient_id, private_key=None):
    """
    Get patient data from Epic FHIR API
    
    Args:
        patient_id (str): The Epic patient ID
        private_key (str, optional): The RSA private key. Defaults to reading from file.
        
    Returns:
        dict: Patient data as JSON
    """
    # Read private key from file if not provided
    if not private_key:
        with open(PRIVATE_KEY_FILE, "r") as f:
            private_key = f.read()
    
    # Get authorization header with valid token
    auth_header = get_epic_auth_header(
        private_key_content=private_key,
        use_prod=USE_PRODUCTION
    )
    
    # Prepare request
    url = f"{EPIC_FHIR_BASE_URL}/Patient/{patient_id}"
    headers = {
        "Authorization": auth_header,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Make request
    response = requests.get(url, headers=headers)
    
    # Handle response
    if response.ok:
        return response.json()
    else:
        raise Exception(f"Error fetching patient data: {response.status_code} - {response.text}")

def foundry_transformation_example(spark, input_df):
    """
    Example transformation function for Foundry
    
    Args:
        spark: Spark session
        input_df: Input DataFrame with patient IDs
        
    Returns:
        DataFrame: Output with patient data from Epic
    """
    import pandas as pd
    from pyspark.sql.functions import udf
    from pyspark.sql.types import StringType
    
    # Read private key (in production, use Foundry secrets)
    with open(PRIVATE_KEY_FILE, "r") as f:
        private_key = f.read()
    
    # Convert to pandas for processing (for small datasets)
    patients_df = input_df.toPandas()
    
    # Function to fetch patient data
    def fetch_patient_data(patient_id):
        try:
            patient_data = get_patient(patient_id, private_key)
            # Extract relevant fields
            return str(patient_data)  # Simplified - extract specific fields as needed
        except Exception as e:
            return f"Error: {str(e)}"
    
    # Apply function to each row
    patients_df['patient_data'] = patients_df['patient_id'].apply(fetch_patient_data)
    
    # Convert back to Spark DataFrame
    result_df = spark.createDataFrame(patients_df)
    return result_df

# Example usage in a regular Python script
if __name__ == "__main__":
    # Example patient ID (replace with a valid ID)
    patient_id = "eRp.HuKDlKB8MhAkzHFthQQ3"
    
    try:
        patient_data = get_patient(patient_id)
        print(f"Successfully retrieved data for patient {patient_id}")
        print(f"Patient name: {patient_data.get('name', [{}])[0].get('given', ['Unknown'])[0]} {patient_data.get('name', [{}])[0].get('family', 'Unknown')}")
    except Exception as e:
        print(f"Error: {e}") 