"""
Token Refresher for Epic FHIR API

This module provides automatic token generation and refresh functionality
for the Epic FHIR API, ensuring authentication tokens are always valid.
"""

import os
import time
import uuid
import json
import logging
import requests
from typing import Dict, Optional, Any, Callable
from pathlib import Path

try:
    import jwt
except ImportError:
    raise ImportError("PyJWT package not found. Please install with: pip install PyJWT cryptography")

from fhir_pipeline.utils.config_loader import load_epic_credentials

logger = logging.getLogger("fhir_pipeline.auth.token_refresher")

# Default configuration
DEFAULT_JWKS_URL = "https://gsiegel14.github.io/ATLAS-EPIC/.well-known/jwks.json"
DEFAULT_KID = "atlas-key-001"
DEFAULT_TOKEN_URL = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"
DEFAULT_SCOPE = "system/*.read"
DEFAULT_JWT_EXPIRATION_SECONDS = 300
DEFAULT_REFRESH_BUFFER_SECONDS = 60  # Refresh token when it's within this many seconds of expiring


class TokenRefresher:
    """
    Handles automatic generation and refresh of Epic FHIR API tokens.
    
    This class implements the proven authentication approach from setup_epic_auth.py
    and provides automatic refresh functionality.
    """
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        private_key: Optional[str] = None,
        token_url: str = DEFAULT_TOKEN_URL,
        jwks_url: str = DEFAULT_JWKS_URL,
        kid: str = DEFAULT_KID,
        scope: str = DEFAULT_SCOPE,
        debug_mode: bool = False,
        token_file_path: Optional[str] = "epic_token.json",
    ):
        """
        Initialize the token refresher.
        
        Args:
            client_id: Epic client ID
            private_key: Private key content as string
            token_url: Token endpoint URL
            jwks_url: URL to JWKS (JSON Web Key Set)
            kid: Key ID in JWKS
            scope: OAuth scope
            debug_mode: Whether to enable debug output
            token_file_path: Path to save/load token (None to disable)
        """
        self.debug_mode = debug_mode
        
        # Load credentials if not provided
        if client_id is None or private_key is None:
            logger.debug("Loading credentials from config loader")
            loaded_client_id, loaded_private_key = load_epic_credentials()
            
            if client_id is None:
                client_id = loaded_client_id
                logger.debug(f"Using client ID from config: {client_id}")
            
            if private_key is None:
                private_key = loaded_private_key
                logger.debug("Using private key from config")
        
        self.client_id = client_id
        self.private_key = private_key
        self.token_url = token_url
        self.jwks_url = jwks_url
        self.kid = kid
        self.scope = scope
        self.token_file_path = token_file_path
        
        # Token cache
        self.token_data = None
        self.last_refresh_time = 0
        
        # Debug info
        if self.debug_mode:
            logger.debug(f"TokenRefresher initialized with client ID: {self.client_id}")
            logger.debug(f"Using token endpoint: {self.token_url}")
            logger.debug(f"Using JWKS URL: {self.jwks_url}")
            logger.debug(f"Token file path: {self.token_file_path}")
    
    def get_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.
        
        Returns:
            str: Access token
        """
        # Check if we have a cached token
        if self.token_data:
            # Check if token is about to expire
            current_time = int(time.time())
            expiry_time = self.token_data.get("expires_at", 0)
            
            # If token is valid and not about to expire, return it
            if expiry_time > current_time + DEFAULT_REFRESH_BUFFER_SECONDS:
                logger.debug("Using cached token")
                return self.token_data["access_token"]
            
            logger.info("Token is expired or about to expire, refreshing...")
        
        # Try to generate a new token
        try:
            token_data = self._generate_token()
            if token_data and "access_token" in token_data:
                self.token_data = token_data
                self.last_refresh_time = int(time.time())
                logger.info("Successfully generated new token")
                return token_data["access_token"]
        except Exception as e:
            logger.error(f"Failed to generate new token: {str(e)}")
            # Fall through to try loading from file
        
        # If we couldn't generate a token, try to load one from file
        if self.token_file_path:
            try:
                logger.info(f"Trying to load token from {self.token_file_path}")
                token_data = self._load_token_from_file()
                if token_data and "access_token" in token_data:
                    # Check if the loaded token is still valid
                    current_time = int(time.time())
                    expiry_time = token_data.get("expires_at", 0)
                    if expiry_time > current_time:
                        self.token_data = token_data
                        logger.info(f"Using token from {self.token_file_path}")
                        return token_data["access_token"]
                    else:
                        logger.warning(f"Token in {self.token_file_path} is expired")
            except Exception as e:
                logger.error(f"Error loading token from {self.token_file_path}: {str(e)}")
        
        # If we reach here, we failed to get a valid token
        raise ValueError("Failed to obtain a valid access token")
    
    def create_token_provider(self) -> Callable[[], str]:
        """
        Create a token provider function for the FHIR client.
        
        Returns:
            Callable: Token provider function that returns an access token
        """
        def token_provider():
            return self.get_access_token()
        
        return token_provider
    
    def _generate_token(self) -> Dict[str, Any]:
        """
        Generate a new access token using JWT authentication.
        
        Returns:
            Dict[str, Any]: Token data including access_token and expires_in
        """
        # Set the JWT headers
        headers = {
            "alg": "RS384",  # Epic requires RS384
            "kid": self.kid,
            "jku": self.jwks_url,
            "typ": "JWT"
        }
        
        # Get current time
        now = int(time.time())
        
        # Generate a unique JTI (max 32 chars)
        jti = str(uuid.uuid4())[:32]
        
        # Create JWT payload
        payload = {
            "iss": self.client_id,
            "sub": self.client_id,
            "aud": self.token_url,
            "jti": jti,
            "iat": now,
            "nbf": now,
            "exp": now + DEFAULT_JWT_EXPIRATION_SECONDS
        }
        
        if self.debug_mode:
            logger.debug(f"Creating JWT with headers: {headers}")
            logger.debug(f"Creating JWT with payload: {payload}")
        
        # Sign the JWT with the private key
        try:
            encoded_jwt = jwt.encode(
                payload=payload,
                key=self.private_key,
                algorithm="RS384",
                headers=headers
            )
        except Exception as e:
            logger.error(f"Error encoding JWT: {str(e)}")
            raise
        
        # Exchange JWT for access token
        data = {
            'grant_type': 'client_credentials',
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'client_assertion': encoded_jwt,
            'scope': self.scope
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        if self.debug_mode:
            logger.debug(f"Requesting access token from {self.token_url}")
        
        try:
            response = requests.post(
                self.token_url,
                data=data,
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Token request failed with status {response.status_code}")
                if self.debug_mode:
                    logger.debug(f"Response: {response.text}")
                
                if "invalid_client" in response.text:
                    logger.error("Invalid client error - check client_id, key, and JWKS setup")
                    logger.error("Note: JWKS can take up to 60 min (sandbox) or 12 hours (prod) to propagate")
                
                response.raise_for_status()
            
            token_data = response.json()
            
            # Add expiration timestamp
            if 'expires_in' in token_data:
                token_data['expires_at'] = int(time.time()) + token_data['expires_in']
            
            # Save token to file if a path is provided
            if self.token_file_path:
                self._save_token_to_file(token_data)
            
            return token_data
            
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            raise
    
    def _save_token_to_file(self, token_data: Dict[str, Any]) -> None:
        """
        Save token data to a file.
        
        Args:
            token_data: Token data to save
        """
        if not self.token_file_path:
            return
        
        try:
            # Create directory if it doesn't exist
            token_file = Path(self.token_file_path)
            token_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.token_file_path, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            logger.debug(f"Token saved to {self.token_file_path}")
        except Exception as e:
            logger.error(f"Error saving token to {self.token_file_path}: {str(e)}")
    
    def _load_token_from_file(self) -> Optional[Dict[str, Any]]:
        """
        Load token data from a file.
        
        Returns:
            Dict[str, Any]: Token data if successful, None otherwise
        """
        if not self.token_file_path or not os.path.exists(self.token_file_path):
            return None
        
        try:
            with open(self.token_file_path, 'r') as f:
                token_data = json.load(f)
            
            return token_data
        except Exception as e:
            logger.error(f"Error loading token from {self.token_file_path}: {str(e)}")
            return None 