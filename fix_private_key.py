import os
import sys
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join('config', '.env')
load_dotenv(env_path)

# Get GitHub App credentials
app_id = os.getenv("GITHUB_APP_ID")
private_key = os.getenv("GITHUB_PRIVATE_KEY")

print(f"App ID: {app_id}")
print(f"Original private key length: {len(private_key) if private_key else 0}")
print(f"Original private key: {private_key}")

# Fix the private key format
if private_key:
    # Check if the key is already in the correct format
    if "-----BEGIN RSA PRIVATE KEY-----" not in private_key:
        # Format the key properly
        formatted_key = "-----BEGIN RSA PRIVATE KEY-----\n"
        formatted_key += private_key
        formatted_key += "\n-----END RSA PRIVATE KEY-----"
        
        # Update the .env file
        try:
            with open(env_path, 'r') as file:
                env_content = file.read()
            
            # Replace the private key
            new_env_content = env_content.replace(
                f"GITHUB_PRIVATE_KEY={private_key}",
                f"GITHUB_PRIVATE_KEY={formatted_key}"
            )
            
            with open(env_path, 'w') as file:
                file.write(new_env_content)
            
            print(f"\nPrivate key has been formatted and saved to {env_path}")
            print(f"New private key length: {len(formatted_key)}")
        except IOError as e:
            print(f"\nError updating .env file: {str(e)}")
            sys.exit(1)
        print(f"\nPrivate key has been formatted and saved to {env_path}")
        print(f"New private key length: {len(formatted_key)}")
    else:
        print("\nPrivate key is already in the correct format")
else:
    print("\nNo private key found in .env file")
