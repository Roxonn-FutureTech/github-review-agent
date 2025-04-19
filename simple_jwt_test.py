import jwt
import time

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
    
    # Try with different algorithms
    algorithms = ["RS256", "RS384", "RS512"]
    
    for algorithm in algorithms:
        try:
            print(f"\nTrying algorithm: {algorithm}")
            encoded_jwt = jwt.encode(payload, private_key, algorithm=algorithm)
            print(f"✅ JWT created successfully with {algorithm}: {encoded_jwt[:20]}...")
        except Exception as e:
            print(f"❌ Failed with {algorithm}: {str(e)}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
