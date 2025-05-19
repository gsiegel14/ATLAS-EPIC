from palantir.datasets.core import Dataset
import subprocess
import json
import os
import tempfile

def refresh_epic_token():
    """
    Refreshes the Epic API access token using the existing setup_epic_auth.py script.
    
    Returns:
        str: A fresh access token for Epic API
    """
    # Create a temporary script that will call our existing setup_epic_auth.py
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as temp_script:
        script_path = temp_script.name
        temp_script.write('''#!/bin/bash
cat << 'EOF' | python setup_epic_auth.py
-----BEGIN RSA PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC2AKimbjNPeeRU
G137XJU7q90RVIfAkO9EHz5HGrYG3etXGIF/C9fJfYKJ2wfhs/SjQQL97rr5l+nE
xrndtnIqOKgltQoBIDkk2dJcKzfSNhJzqjH4MBj07DpLwqLhWQWlhsK7b4cM61o7
Jka4PY/FCofIklU+dPGC29tG1P83HxHkDitwsznMfmJbWywfeCWc9cCO9eoQVAUs
+LkdJvIH99SSIbDh6J8QecI41hVtTkGEaXHIRerTZHPMisiQz2NMpP82tutzHTVM
KoPKVkiJ7KKzXG9ecNmU8aIiaJIhWZ2Sb1/syKyqnCpMIrNdqqG5gFqhbzsbz0tT
yZPbLiE1AgMBAAECggEAIcyiBVRqUXxiv47ch3l0WmJKmfUPh96ynH1L4MMQYlqU
obZSmDAwGQJmu2iygEMd77J7VoKe9Qq19l3sdwTyky415djG3JoqGpKcGxNImNCD
YTkOchemjteO5PJmssBISOrrn4jw9OCBP4JWeFEwcaiIumIYlBJ+Jm3jfTZBli/t
y6xBK4vTXVSNN//tbZupNOSDGPEb7+d65f6xfJbZ8x9I6mvwXF0mpPt6gacS8tte
uPUtxGfSxT9ireXBZQOW+sJxzPqp570X6Af160UXfbwv2T289XGPbioAEcvN6m25
b5oQ41zaDi/haf/Ots8e+GtW2dnn0HG3apmPK/JmyQKBgQDoZs+aFNX/fT0VQb9h
BJz1n5GQ2jqtNrJKAHztXVQv//3B4+x/FMz5mwhY5xOXLBm0HZ0qoOjSJpSQHI7g
zFbCJ3MjUoWm2uFkeFUJjNFEGgtDHU4TY9vfIB9nKP2HKxUd8dOYiNEJKlo0I/aY
vdTrfNrRzg12zGlpw5X4Y9hQeQKBgQDIhmAe+SlGu6QFT5HpL2tCXOKP4GQYwx2/
2xEv5M7eN1BTHWlCFDl+DSbQpkTfZUtYJ2/rbSnGPOmkP2PWO8hYwF6+Ee/qTCoB
GblzN9/S+lx1xEKYxu/ZNe9FeCyMw3XeOBtNQCzn+N9lw7qGFAJQT3z7BgZQwcL3
CKqU1+1h3QKBgQCSGvwImB7VBDRElyzCgLYlBxX7U1t5QOW5ZTBKW8BGhHp1k+Cs
NQrauFebZI8z16TvfX6RFxnXNYUaRpMIXdlYh3UhTnSnL2jIwHmLtN+ujXbBPNx6
aVg6X5a0xFrTdOVCQxXd40pRSlZjLfAHGqJNXxXrDcx9t28FrY9UDVYm0QKBgCpL
/3lCKYzMiHgYdHoXn9dGEfAn5MxJu+TmhpQhOPXEAymJSW5Zv3HGtYpjMlnvG3hd
n/n1g5jlg3mLI1SN49dMvgS5MvJmxkqC6QJlxG+G3UGbuyUUoCDiZkdJnNv9vIK1
p7E8JOCYvyIGYAjuIbhsC3kcwQrbuIeN6y2F5XCRAoGBAJomFkBvkk53Qp99m6tk
cAhsDE9iZpVMEr0lLzEYAodYu8/IRFX5T8J+ZVu21mXCYdVG4VCigbXvfvaQZeVi
RdZT5i2QpI8VEAaRPJUVWS+FJiW/qmtb08UQTDgJSGojFnvkUxLbkwg+wHmuys9w
iGlwPXB2QzKpyM0k0SN9Qg+m
-----END RSA PRIVATE KEY-----
EOF
''')
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    
    try:
        # Run the script and capture the output
        result = subprocess.run([script_path], capture_output=True, text=True)
        
        # Check for errors
        if result.returncode != 0:
            raise Exception(f"Error refreshing token: {result.stderr}")
        
        # Read the token file
        with open('epic_token.json', 'r') as token_file:
            token_data = json.load(token_file)
            access_token = token_data.get('access_token')
            
            if not access_token:
                raise Exception("Failed to get access token")
                
            return access_token
    
    finally:
        # Clean up the temporary script
        if os.path.exists(script_path):
            os.remove(script_path)

# Make this compatible with Foundry Functions
@function
def refresh_epic_token() -> str:
    """
    Refreshes the Epic API access token using the existing setup_epic_auth.py script.
    
    Returns:
        str: A fresh access token for Epic API
    """
    return refresh_epic_token() 