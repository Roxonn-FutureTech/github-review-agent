import os
import sys
import json
import hmac
import hashlib
from unittest.mock import MagicMock, patch

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.backend.webhook_handler import WebhookHandler, app

def test_webhook_handler_init():
    """Test WebhookHandler initialization."""
    # Create mock objects
    mock_github = MagicMock()
    mock_logger = MagicMock()
    
    # Initialize the webhook handler
    handler = WebhookHandler("test_secret", mock_github, mock_logger)
    
    # Verify initialization
    assert handler.webhook_secret == "test_secret"
    assert handler.github == mock_github
    assert handler.logger == mock_logger

def test_verify_webhook_valid():
    """Test webhook verification with valid signature."""
    # Create mock objects
    mock_github = MagicMock()
    mock_logger = MagicMock()
    
    # Initialize the webhook handler
    handler = WebhookHandler("test_secret", mock_github, mock_logger)
    
    # Create a test payload and signature
    payload = b'{"action":"opened","repository":{"full_name":"test/repo"}}'
    
    # Create the expected signature
    expected_signature = 'sha256=' + hmac.new(
        "test_secret".encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Verify the webhook
    assert handler.verify_webhook(expected_signature, payload) == True

def test_verify_webhook_invalid():
    """Test webhook verification with invalid signature."""
    # Create mock objects
    mock_github = MagicMock()
    mock_logger = MagicMock()
    
    # Initialize the webhook handler
    handler = WebhookHandler("test_secret", mock_github, mock_logger)
    
    # Create a test payload and signature
    payload = b'{"action":"opened","repository":{"full_name":"test/repo"}}'
    invalid_signature = 'sha256=invalid'
    
    # Verify the webhook
    assert handler.verify_webhook(invalid_signature, payload) == False

def test_handle_event_unsupported():
    """Test handling an unsupported event type."""
    # Create mock objects
    mock_github = MagicMock()
    mock_logger = MagicMock()
    
    # Initialize the webhook handler
    handler = WebhookHandler("test_secret", mock_github, mock_logger)
    
    # Handle an unsupported event
    response, status_code = handler.handle_event("unsupported_event", {})
    
    # Verify the response
    assert status_code == 400
    assert "Unsupported event type" in response["message"]

def test_handle_pull_request_opened():
    """Test handling a pull request opened event."""
    # Create mock objects
    mock_github = MagicMock()
    mock_logger = MagicMock()
    
    # Set up the mock to return a task with an ID
    mock_task = MagicMock()
    mock_task.id = "test_task_id"
    mock_github.queue_analysis.return_value = mock_task
    
    # Initialize the webhook handler
    handler = WebhookHandler("test_secret", mock_github, mock_logger)
    
    # Create a test payload
    payload = {
        "action": "opened",
        "pull_request": {"number": 123},
        "repository": {"full_name": "test/repo"}
    }
    
    # Handle the event
    response, status_code = handler.handle_pull_request(payload)
    
    # Verify the response
    assert status_code == 200
    assert response["status"] == "success"
    assert response["action"] == "opened"
    assert response["task_id"] == "test_task_id"
    
    # Verify the GitHub client was called
    mock_github.track_pull_request.assert_called_once_with("test/repo", 123)
    mock_github.queue_analysis.assert_called_once_with("test/repo", 123)

def test_handle_issue_opened():
    """Test handling an issue opened event."""
    # Create mock objects
    mock_github = MagicMock()
    mock_logger = MagicMock()
    
    # Initialize the webhook handler
    handler = WebhookHandler("test_secret", mock_github, mock_logger)
    
    # Create a test payload
    payload = {
        "action": "opened",
        "issue": {"number": 456},
        "repository": {"full_name": "test/repo"}
    }
    
    # Handle the event
    response, status_code = handler.handle_issue(payload)
    
    # Verify the response
    assert status_code == 200
    assert response["status"] == "success"
    assert response["action"] == "opened"
    assert response["assigned"] == True
    
    # Verify the GitHub client was called
    mock_github.assign_reviewer.assert_called_once_with("test/repo", 456)

def test_handle_push():
    """Test handling a push event."""
    # Create mock objects
    mock_github = MagicMock()
    mock_logger = MagicMock()
    
    # Set up the mock to return a local path
    mock_github.clone_repository.return_value = "./repos/test_repo"
    
    # Initialize the webhook handler
    handler = WebhookHandler("test_secret", mock_github, mock_logger)
    
    # Create a test payload
    payload = {
        "repository": {"full_name": "test/repo"},
        "ref": "refs/heads/main",
        "commits": [
            {"id": "abc123", "message": "Test commit"}
        ]
    }
    
    # Handle the event
    response, status_code = handler.handle_push(payload)
    
    # Verify the response
    assert status_code == 200
    assert response["status"] == "success"
    assert response["branch"] == "main"
    assert response["commits"] == 1
    
    # Verify the GitHub client was called
    mock_github.clone_repository.assert_called_once_with("test/repo", "main")
    mock_github.update_status.assert_called_once()

if __name__ == "__main__":
    # Run the tests
    test_webhook_handler_init()
    test_verify_webhook_valid()
    test_verify_webhook_invalid()
    test_handle_event_unsupported()
    test_handle_pull_request_opened()
    test_handle_issue_opened()
    test_handle_push()
    print("All tests passed!")
