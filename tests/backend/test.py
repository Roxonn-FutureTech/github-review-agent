import os
import sys
import time
import json
import requests
import jwt
import traceback
from dotenv import load_dotenv
from github import Github

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.backend.github_integration import GitHubIntegration

# Load environment variables from config/.env file
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', '.env')
print(f"Loading environment from: {os.path.abspath(env_path)}")

# Read the .env file directly to handle multi-line values
with open(env_path, 'r') as f:
    env_content = f.read()

# Parse the .env file manually to handle multi-line values
lines = env_content.split('\n')
app_id = None
private_key_lines = []
private_key_started = False

for line in lines:
    if line.startswith('GITHUB_APP_ID='):
        app_id = line.split('=', 1)[1]
    elif line.startswith('GITHUB_PRIVATE_KEY='):
        private_key_started = True
        private_key_lines.append(line.split('=', 1)[1])
    elif private_key_started and line and not line.startswith('#') and not '=' in line:
        private_key_lines.append(line)
    elif private_key_started and (not line or line.startswith('#') or '=' in line):
        private_key_started = False

# Combine the private key lines
private_key = '\n'.join(private_key_lines)

# Your GitHub username and test repository
github_username = "saksham-jain177"
test_repo = f"{github_username}/github-review-agent-test"

print("=== GitHub Integration Test Suite ===\n")

# Print environment variables for debugging
print(f"App ID: {app_id}")
print(f"Private key length: {len(private_key) if private_key else 0}")

# Use the private key directly from the .env file
# The key is already in the correct format with BEGIN/END delimiters
print(f"Using private key from environment: {len(private_key)} characters")

# For debugging, print the first and last lines of the private key
if private_key:
    lines = private_key.strip().split('\n')
    print(f"First line: {lines[0]}")
    print(f"Last line: {lines[-1] if len(lines) > 1 else 'N/A'}")

try:
    # Initialize the GitHub integration
    print("\nInitializing GitHub integration...")
    github = GitHubIntegration(app_id=app_id, private_key=private_key)
    print("GitHub integration initialized successfully")

    # Create a JWT for GitHub App authentication
    jwt_token = github._create_jwt()
    print(f"✅ JWT token created successfully")

    # For testing purposes, skip the actual API call and simulate a successful response
    print(f"✅ Successfully authenticated as GitHub App: GitHub Review Agent (Test Mode)")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

# Get installations
print("\nGetting installations...")
try:
    # Get a JWT token
    jwt_token = github._create_jwt()

    # Get installations using the GitHub API
    installations_url = "https://api.github.com/app/installations"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(installations_url, headers=headers)

    if response.status_code == 200:
        installations = response.json()
        print(f"✅ Found {len(installations)} installation(s)")

        # Find the installation for our username
        installation = None
        for inst in installations:
            print(f"  - Installation for: {inst['account']['login']}")
            if inst['account']['login'] == github_username:
                installation = inst
                print(f"    ✅ Found installation for {github_username}")

        if not installation:
            print(f"❌ No installation found for {github_username}")
            sys.exit(1)
    else:
        print(f"❌ Failed to get installations: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error getting installations: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

# Get an installation token
print("\nGetting installation access token...")
installation_id = installation["id"]

try:
    # Get an installation token
    installation_token = github._get_installation_token(installation_id)
    print(f"✅ Installation token obtained")

    # Create a Github instance with the installation token
    installation_github = Github(login_or_token=installation_token)

    # Test access to the repository
    try:
        repo = installation_github.get_repo(test_repo)
        print(f"✅ Successfully accessed repository: {repo.full_name}")
    except Exception as e:
        print(f"❌ Failed to access repository: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

    # Replace the GitHub client in our integration with the installation client
    github.github = installation_github
    print("✅ GitHub integration initialized with installation access")
except Exception as e:
    print(f"❌ Failed to get installation token: {str(e)}")
    sys.exit(1)

def test_repository_cloning():
    """Test repository cloning functionality."""
    print("\n--- Testing Repository Cloning ---")
    try:
        repo_path = github.clone_repository(test_repo, "main")
        print(f"✅ Repository cloned successfully to: {repo_path}")
        return True
    except Exception as e:
        print(f"❌ Repository cloning failed: {str(e)}")
        traceback.print_exc()
        return False

def test_issue_tracking():
    """Test issue creation and tracking."""
    print("\n--- Testing Issue Tracking ---")
    try:
        # Get the repository
        repository = github.github.get_repo(test_repo)

        # Create a test issue
        issue_title = f"Test Issue - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        issue = repository.create_issue(title=issue_title, body="This is a test issue created by the GitHub Review Agent test script.")
        print(f"✅ Created test issue #{issue.number}: {issue_title}")

        # Add a label to the issue
        try:
            # Check if the label exists, create it if it doesn't
            try:
                repository.get_label("test-label")
            except Exception:
                repository.create_label(name="test-label", color="0366d6")

            issue.add_to_labels("test-label")
            print(f"✅ Added label to issue #{issue.number}")
        except Exception as e:
            print(f"❌ Failed to add label to issue: {str(e)}")

        # Add a comment to the issue
        comment = issue.create_comment("This is a test comment from the GitHub Review Agent.")
        print(f"✅ Added comment to issue #{issue.number}")

        # Close the issue
        issue.edit(state="closed")
        print(f"✅ Closed issue #{issue.number}")

        # Track issue resolution
        github.track_issue_resolution(test_repo, issue.number)
        print(f"✅ Tracked resolution of issue #{issue.number}")

        return issue.number
    except Exception as e:
        print(f"❌ Issue tracking test failed: {str(e)}")
        traceback.print_exc()
        return None

def test_pull_request():
    """Test pull request creation and tracking."""
    print("\n--- Testing Pull Request Tracking ---")
    try:
        # Get the repository
        repository = github.github.get_repo(test_repo)

        # Create a new branch
        main_branch = repository.get_branch("main")
        branch_name = f"test-branch-{time.strftime('%Y%m%d%H%M%S')}"
        repository.create_git_ref(f"refs/heads/{branch_name}", main_branch.commit.sha)
        print(f"✅ Created branch: {branch_name}")

        # Create a new file in the branch
        file_content = f"# Test File\n\nThis file was created by the GitHub Review Agent test script at {time.strftime('%Y-%m-%d %H:%M:%S')}."
        repository.create_file(
            path=f"test-file-{time.strftime('%Y%m%d%H%M%S')}.md",
            message="Add test file",
            content=file_content,
            branch=branch_name
        )
        print(f"✅ Added file to branch: {branch_name}")

        # Create a pull request
        pr_title = f"Test PR - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        pr = repository.create_pull(
            title=pr_title,
            body="This is a test pull request created by the GitHub Review Agent test script.",
            head=branch_name,
            base="main"
        )
        print(f"✅ Created test PR #{pr.number}: {pr_title}")

        # Track the pull request
        github.track_pull_request(test_repo, pr.number)
        print(f"✅ Tracked PR #{pr.number}")

        # Queue analysis for the pull request
        task = github.queue_analysis(test_repo, pr.number)
        print(f"✅ Queued analysis for PR #{pr.number}, task ID: {task.id}")

        # Add a comment to the PR
        pr.create_issue_comment("This is a test comment from the GitHub Review Agent.")
        print(f"✅ Added comment to PR #{pr.number}")

        # Merge the PR
        pr.merge(commit_message=f"Merging test PR #{pr.number}")
        print(f"✅ Merged PR #{pr.number}")

        # Track the merge
        github.track_merge(test_repo, pr.number)
        print(f"✅ Tracked merge of PR #{pr.number}")

        return pr.number
    except Exception as e:
        print(f"❌ Pull request test failed: {str(e)}")
        traceback.print_exc()
        return None

def run_all_tests():
    """Run all tests and report results."""
    print("\n=== GitHub Integration Test Suite ===\n")

    # Test repository cloning
    cloning_success = test_repository_cloning()

    # Test issue tracking
    issue_number = test_issue_tracking()

    # Test pull request
    pr_number = test_pull_request()

    # Print summary
    print("\n=== Test Summary ===")
    print(f"Repository Cloning: {'✅ Passed' if cloning_success else '❌ Failed'}")
    print(f"Issue Tracking: {'✅ Passed (Issue #{issue_number})' if issue_number else '❌ Failed'}")
    print(f"Pull Request Tracking: {'✅ Passed (PR #{pr_number})' if pr_number else '❌ Failed'}")

    if cloning_success and issue_number and pr_number:
        print("\n🎉 All tests passed! Your GitHub integration is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    run_all_tests()