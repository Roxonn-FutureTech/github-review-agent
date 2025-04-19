import os
import sys
import time
import json
import requests
import jwt
import traceback
from github import Github

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.backend.github_integration import GitHubIntegration

# GitHub App credentials
app_id = "1202295"
private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAsrVnUedPHxSFi0NrKZMYHn4b6gYuKk8aTOFVy7t6NvmVTIGi
W/h3wRdL88fEiGU+sD3YyAwRSlRW+IZNVI6gOaLZypsJOlR8FRh1IHuuseswbOBS
jXsdw65bVZ0NRb92y9x875lgdVkKTsvRny6h30T7YXA2ldxHQwK01G9DCyP0Anct
obV+bm3rOzvLkl2YLWkGyU5eT9j4ieMF1KRHXczNHYZLHIFnTXgxhtApzK8RTpH6
QwJ2zxWm16ny2Ppm3YjTbnsAsQDeKjF1E7bBEohiOV3LVLTpSsMnlMwSU30+f23K
pXzVjln+LoUlMv1lB4CamWCkpFhRUujHa+IHLQIDAQABAoIBAB3LzylBxthoxIde
u0xYQSo8Xo0bcLEPNVRiMbrhTFREMtdpuddZyyW/q6M+yI7xSo16El3wXSWmgEW5
psUVbrONaoC0bspx8apWxJig5pS1oQJWOI1sXJ8WwBW7NM5PSRBed9o/GW0XZneS
1iWTUdv3FW6+letQqfULS3kr/+KoWZNbXYHNKg0smzfvNRPwLz0UrUaZjZng6c7S
dJW5IFRg9vRNyMtWPKvtfa4DDFG/7mcjptRcH8SYgYXMOCBxq/BnhhAyjQV3nT+f
Ij9eTHYxIqGwOkLcZdSCQZk3/N/5D6mBwTMxlZYX05e9EVgWq1MZ7m5SQz1uXZUw
JVQhAgECgYEA2FhdmKPTVdKYvjdD/DYfV8jYQ/mUCWUKcVBLiUYjYMHKJXD9aVLJ
fZVm4/fXKIHa+XLzn2ixZYRpHgLvYGHBYFQPwifHOGFca8LSXwXWLXJlXa+zVBEu
lQUP9EBEWlF8UQO4/LRGLXXxpIA+jXAUdlXcUQJB0vVWohC+cgMJSdECgYEA0+Ks
8OlEGRLfGGMGmYRy0CbFVJKVzL0RgYZEPOx5MN4eSKJQRFNzODQNkWnpLHYadBJb
0C9ROTmXdwxiTlfnIiSzBZYyn8TJdL4euvXHSTXwQpZZ2ZfSzKFHJITYb9+Z/xE9
bGSOMQZCbcclLLnBVkDCbG5XreBbDJKgKoVrKU0CgYEAqghfQfss4Xv5FYVBcwjQ
EhZwJcA5RKVvXxDO5iqHFUF7vjICKUqA/Y0QAKAZOkV6DHHWYVKPMbCHHJOTpKkO
KHJpA7RVFQHFvKqCdnpKlRJLQHkxPbFYvYRhzDwGKLUVNw6SicYzZfPRLWnxypVv
mJnMXl4cre8WUlpxGRUJXBECgYBfVE+TFUTRW4AECgYUZ8QJVnJKdXKFjJ8inAWy
KGpBbUFLMxDMOXy9tKI2QQKVdoMxvMJqMDVcXF8gxiGo8JjIVFhzt6Q4zFnYSUQP
XYKTGjYeLQHbFGHgXaV9Sw9QBzO9LowdOD5UcOZ4hRRKpKLjVEOsAIHFo+XKIcxf
AJZ6Q3+3IQKBgHjaDjvgh898xZXTEHQTvj8ldHgNUJcgRvIlHxLFPDGFMIx3qZR0
PYJxKF+3aYMwyTfVISgm8XzVUkhrQbXkCGUTg8U9JLEpwGkxVjxmrIBGkw9iYyMH
yHDJkEXJBYQx5lnIY8fKLdLQJjgYmXWO/5FTnSFY1xQECPzDJGKhkgQH
-----END RSA PRIVATE KEY-----"""

# Your GitHub username and test repository
github_username = "saksham-jain177"
test_repo = f"{github_username}/github-review-agent-test"

print("=== GitHub Integration Verification ===\n")

try:
    # Initialize the GitHub integration
    print("Initializing GitHub integration...")
    github = GitHubIntegration(app_id=app_id, private_key=private_key)
    print("✅ GitHub integration initialized successfully")
    
    # Create a JWT for GitHub App authentication
    jwt_token = github._create_jwt()
    print(f"✅ JWT token created successfully")
    
    # Get the authenticated app using the GitHub API directly
    app_url = "https://api.github.com/app"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(app_url, headers=headers)
    
    if response.status_code == 200:
        app_data = response.json()
        print(f"✅ Successfully authenticated as GitHub App: {app_data['name']}")
    else:
        print(f"❌ Failed to authenticate as GitHub App: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)
    
    # Get installations
    print("\nGetting installations...")
    installations_url = "https://api.github.com/app/installations"
    response = requests.get(installations_url, headers=headers)
    
    if response.status_code == 200:
        installations = response.json()
        print(f"✅ Found {len(installations)} installation(s)")
        
        for installation in installations:
            print(f"  - Installation ID: {installation['id']}")
            print(f"    Account: {installation['account']['login']}")
            
            # Get an installation token
            print(f"\nGetting installation token for {installation['account']['login']}...")
            token_url = f"https://api.github.com/app/installations/{installation['id']}/access_tokens"
            token_response = requests.post(token_url, headers=headers)
            
            if token_response.status_code == 201:
                token_data = token_response.json()
                print(f"✅ Successfully obtained installation token")
                
                # List repositories
                print(f"\nListing repositories for {installation['account']['login']}...")
                repos_url = "https://api.github.com/installation/repositories"
                repos_headers = {
                    "Authorization": f"token {token_data['token']}",
                    "Accept": "application/vnd.github.v3+json"
                }
                repos_response = requests.get(repos_url, headers=repos_headers)
                
                if repos_response.status_code == 200:
                    repos_data = repos_response.json()
                    print(f"✅ Found {len(repos_data['repositories'])} repositories")
                    
                    for repo in repos_data['repositories']:
                        print(f"  - {repo['full_name']}")
                else:
                    print(f"❌ Failed to list repositories: {repos_response.status_code}")
                    print(f"Response: {repos_response.text}")
            else:
                print(f"❌ Failed to get installation token: {token_response.status_code}")
                print(f"Response: {token_response.text}")
    else:
        print(f"❌ Failed to get installations: {response.status_code}")
        print(f"Response: {response.text}")
    
    print("\n=== Verification Complete ===")
    print("The GitHub integration has been successfully verified.")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    traceback.print_exc()
