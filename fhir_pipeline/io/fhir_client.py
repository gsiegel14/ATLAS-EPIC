import requests
import json
import time

class FHIRClient:
    def _make_request(self, method, endpoint, params=None, data=None, force_token_refresh=False):
        """
        Make an HTTP request to the FHIR API with error handling and retries.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: FHIR API endpoint
            params: Query parameters
            data: Request data (for POST, PUT)
            force_token_refresh: Whether to force refresh the token before request
            
        Returns:
            Response object
        """
        try:
            # Prepare URL and headers
            url = f"{self.base_url}/{endpoint}"
            token = self._get_token(force_refresh=force_token_refresh)
            
            if token:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json"
                }
            else:
                # Try with no authentication as a last resort (for public endpoints)
                headers = {
                    "Accept": "application/json"
                }
                self.logger.warning("Making request without authentication (token unavailable)")
            
            # Log request details in debug mode
            self.logger.debug(f"Making {method} request to {url}")
            if params:
                self.logger.debug(f"Request params: {json.dumps(params)}")
            if data:
                self.logger.debug(f"Request data: {json.dumps(data)}")
            
            # Time the request
            start_time = time.time()
            
            # Make the request
            response = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                json=data if data else None,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            
            elapsed = time.time() - start_time
            self.logger.debug(f"Request completed in {elapsed:.3f}s: {response.status_code}")
            
            # Check for errors
            if response.status_code == 401:
                # Auth error - might need a fresh token
                self.logger.warning("Authentication failed. Token might be expired.")
                
                # Check if we already tried refreshing
                if not force_token_refresh:
                    self.logger.info("Refreshing token and retrying request")
                    
                    # Try to load a fresh token directly from file (in case it was refreshed externally)
                    self.token_data = None  # Clear cache
                    self.logger.info(f"Loaded fresh token from {self.token_path}")
                    
                    # Retry with forced refresh
                    return self._make_request(
                        method, endpoint, params, data, force_token_refresh=True
                    )
            
            # Check for other errors
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                self.logger.error(f"Request failed after {elapsed:.3f}s: {str(e)}")
                
                # Log response for debugging
                self.logger.debug(f"Response headers: {dict(response.headers)}")
                if len(response.text) < 1000:
                    self.logger.debug(f"Response body: {response.text}")
                else:
                    self.logger.debug(f"Response body (truncated): {response.text[:500]}...")
                
                raise
            
            # Return response for success status codes
            return response
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {str(e)}")
            raise 