import jwt
import time
import uuid
import requests
import json
import os
from datetime import datetime
from foundry import get_secret

# Configuration
JWKS_URL = "https://gsiegel14.github.io/ATLAS-EPIC/.well-known/jwks.json"
EPIC_TOKEN_URL = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"
TOKEN_FILE = "epic_token.json"

class EpicAuth:
    def __init__(self, use_prod=False):
        self.use_prod = use_prod
        # Get client ID from Foundry secrets
        self.client_id = get_secret('additionalSecretEpicClientId')
        # Get private key from Foundry secrets
        self.private_key = get_secret('additionalSecretEpicPrivateKey')
        
    def generate_jwt(self):
        """Generate a JWT token for Epic's OAuth 2.0 backend service authentication"""
        # Set the JWT headers
        headers = {
            "alg": "RS384",
            "kid": "atlas-key-001",
            "jku": JWKS_URL,
            "typ": "JWT"
        }

        # Get current time
        now = int(time.time())
        
        # Generate a unique JTI (max 151 chars)
        jti = str(uuid.uuid4())[:32]

        # Set the JWT claims exactly as Epic requires
        claims = {
            "iss": self.client_id,
            "sub": self.client_id,
            "aud": EPIC_TOKEN_URL,
            "jti": jti,
            "iat": now,
            "nbf": now,
            "exp": now + 300  # 5 minutes (Epic's maximum)
        }

        # Generate the JWT
        token = jwt.encode(
            payload=claims,
            key=self.private_key,
            algorithm="RS384",
            headers=headers
        )
        
        return token

    def get_access_token(self):
        """Exchange JWT for an access token from Epic"""
        jwt_token = self.generate_jwt()
        
        data = {
            'grant_type': 'client_credentials',
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'client_assertion': jwt_token,
            'scope': 'system/*.read'
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        response = requests.post(
            EPIC_TOKEN_URL,
            data=data,
            headers=headers
        )
        
        if response.ok:
            token_data = response.json()
            
            # Add issued_at timestamp
            token_data['issued_at'] = int(time.time())
            
            # Save token data to file
            with open(TOKEN_FILE, "w") as f:
                json.dump(token_data, f, indent=2)
            
            return token_data
        else:
            raise Exception(f"Failed to obtain access token: {response.text}")

    def get_valid_token(self):
        """Get a valid access token, refreshing if necessary"""
        # Check if we have a saved token
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                try:
                    token_data = json.load(f)
                    
                    # Check if token is expired or will expire in the next minute
                    issued_at = token_data.get('issued_at', 0)
                    expires_in = token_data.get('expires_in', 0)
                    now = int(time.time())
                    
                    # Add a 60-second buffer to ensure token doesn't expire during use
                    if now < (issued_at + expires_in - 60):
                        return token_data.get('access_token')
                except:
                    pass
        
        # If we don't have a valid token, get a new one
        token_data = self.get_access_token()
        return token_data.get('access_token')

def get_epic_auth_header(use_prod=False):
    """Function to get a valid Epic authorization header"""
    # Initialize Epic auth
    auth = EpicAuth(use_prod=use_prod)
    
    # Get valid token
    access_token = auth.get_valid_token()
    
    # Return the header for use in requests
    return f"Bearer {access_token}"

# Example usage in Foundry webhooks
if __name__ == "__main__":
    # Get the authorization header
    try:
        auth_header = get_epic_auth_header(use_prod=False)
        print("Successfully generated authorization header.")
        print(f"Authorization: {auth_header[:30]}...")
        print("\nUse this header in your webhook requests to Epic FHIR API.")
    except Exception as e:
        print(f"Error: {e}") 