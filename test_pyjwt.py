import time
import jwt

# GitHub App credentials
import os

app_id = os.environ.get("GITHUB_APP_ID")
private_key = os.environ.get("GITHUB_PRIVATE_KEY")

if not app_id or not private_key:
    raise ValueError("GITHUB_APP_ID and GITHUB_PRIVATE_KEY environment variables must be set")

print(f"App ID: {app_id}")
print(f"Private key length: {len(private_key)}")

try:
    # Create a JWT for GitHub App authentication
    now = int(time.time())
    payload = {
        "iat": now,
        "exp": now + 600,  # 10 minutes expiration
        "iss": app_id
    }
    
    # Use PyJWT directly
    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    print(f"JWT created successfully: {encoded_jwt[:20]}...")
    print("Test passed!")
except Exception as e:
    print(f"Error creating JWT: {str(e)}")
    import traceback
    traceback.print_exc()
