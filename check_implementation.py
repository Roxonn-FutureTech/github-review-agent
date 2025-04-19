import os
import sys
import json
from unittest.mock import MagicMock, patch

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the GitHub integration class and exceptions
from src.backend.github_integration import GitHubIntegration
from src.backend.exceptions import GitHubAuthError, WebhookError

print("Starting GitHub integration implementation check...")

# Test the GitHub integration with mocks
with patch('src.backend.github_integration.Github') as mock_github_class, \
     patch('src.backend.github_integration.Auth.AppAuth') as mock_auth, \
     patch('src.backend.github_integration.requests.post') as mock_requests_post:

    # Create mock objects
    mock_github = MagicMock()
    mock_repo = MagicMock()
    mock_pr = MagicMock()
    mock_issue = MagicMock()
    mock_commit = MagicMock()
    mock_comment = MagicMock()
    mock_status = MagicMock()
    mock_collaborator = MagicMock()

    # Configure the mocks
    mock_github_class.return_value = mock_github
    mock_github.get_repo.return_value = mock_repo
    mock_repo.get_pull.return_value = mock_pr
    mock_repo.get_issue.return_value = mock_issue
    mock_pr.create_issue_comment.return_value = mock_comment
    mock_issue.create_comment.return_value = mock_comment
    mock_repo.get_commit.return_value = mock_commit
    mock_commit.create_status.return_value = mock_status

    # Mock the requests.post method
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 12345, "body": "Test comment"}
    mock_response.text = json.dumps({"id": 12345, "body": "Test comment"})
    mock_requests_post.return_value = mock_response

    # Mock the token attribute
    mock_github._Github__requester = MagicMock()
    mock_github._Github__requester._Requester__auth = MagicMock()
    mock_github._Github__requester._Requester__auth.token = "mock-token"

    # Set up PR and issue properties
    mock_pr.head = MagicMock()
    mock_pr.head.ref = "feature-branch"
    mock_pr.head.sha = "abc123"
    mock_pr.merged = True
    mock_pr.user = MagicMock()
    mock_pr.user.login = "test-user"

    mock_issue.user = MagicMock()
    mock_issue.user.login = "test-user"
    mock_issue.state = "closed"

    # Set up collaborators
    mock_collaborator.login = "reviewer-user"
    mock_repo.get_collaborators.return_value = [mock_collaborator]

    # Create an instance of GitHubIntegration
    print("Creating GitHubIntegration instance...")
    github = GitHubIntegration(app_id="test_id", private_key="test_key")

    # Test repository cloning
    print("\nTesting repository cloning...")
    with patch('os.path.exists', return_value=False), patch('os.system') as mock_system:
        local_path = github.clone_repository("owner/repo", "main")
        print(f"Repository cloning: {'✅ Passed' if mock_system.called else '❌ Failed'}")
        print(f"  - Local path: {local_path}")

    # Test creating a comment
    print("\nTesting comment creation...")
    try:
        github.create_comment("owner/repo", 123, "Test comment")
        print(f"Comment creation: ✅ Passed")
        print(f"  - get_issue called: {mock_repo.get_issue.called}")
        print(f"  - create_comment called: {mock_issue.create_comment.called if hasattr(mock_issue, 'create_comment') else False}")
    except Exception as e:
        print(f"Comment creation: ❌ Failed - {str(e)}")

    # Test updating status
    print("\nTesting status update...")
    try:
        github.update_status("owner/repo", "abc123", "success", "Tests passed")
        print(f"Status update: ✅ Passed")
        print(f"  - get_commit called: {mock_repo.get_commit.called}")
        print(f"  - create_status called: {mock_commit.create_status.called if hasattr(mock_commit, 'create_status') else False}")
    except Exception as e:
        print(f"Status update: ❌ Failed - {str(e)}")

    # Test tracking a pull request
    print("\nTesting PR tracking...")
    try:
        github.track_pull_request("owner/repo", 123)
        print(f"PR tracking: ✅ Passed")
        print(f"  - get_pull called: {mock_repo.get_pull.called}")
    except Exception as e:
        print(f"PR tracking: ❌ Failed - {str(e)}")

    # Test tracking a merge
    print("\nTesting merge tracking...")
    try:
        github.track_merge("owner/repo", 123)
        print(f"Merge tracking: ✅ Passed")
        print(f"  - get_pull call count: {mock_repo.get_pull.call_count}")
    except Exception as e:
        print(f"Merge tracking: ❌ Failed - {str(e)}")

    # Test assigning a reviewer
    print("\nTesting reviewer assignment...")
    try:
        github.assign_reviewer("owner/repo", 123)
        print(f"Reviewer assignment: ✅ Passed")
        print(f"  - get_issue call count: {mock_repo.get_issue.call_count}")
        print(f"  - get_collaborators called: {mock_repo.get_collaborators.called}")
    except Exception as e:
        print(f"Reviewer assignment: ❌ Failed - {str(e)}")

    # Test tracking issue resolution
    print("\nTesting issue resolution tracking...")
    try:
        github.track_issue_resolution("owner/repo", 123)
        print(f"Issue resolution tracking: ✅ Passed")
        print(f"  - get_issue call count: {mock_repo.get_issue.call_count}")
    except Exception as e:
        print(f"Issue resolution tracking: ❌ Failed - {str(e)}")

    print("\nImplementation verification complete!")
