import pytest
import json
import hmac
import hashlib
from unittest.mock import patch, Mock
from src.backend.webhook_handler import WebhookHandler
from src.backend.exceptions import WebhookError

@pytest.fixture
def webhook_handler():
    # Create mock objects
    mock_github_client = Mock()
    mock_logger = Mock()

    # Create the webhook handler with the correct parameters
    handler = WebhookHandler(
        webhook_secret="test_secret",
        github_client=mock_github_client,
        logger=mock_logger
    )

    yield handler

def test_handle_event_pull_request(webhook_handler):
    # Mock the handle_pull_request method
    with patch.object(webhook_handler, 'handle_pull_request') as mock_handle:
        mock_handle.return_value = ({"status": "success"}, 200)

        # Call the method
        result, status = webhook_handler.handle_event("pull_request", {"action": "opened"})

        # Verify the result
        assert result == {"status": "success"}
        assert status == 200
        mock_handle.assert_called_once_with({"action": "opened"})

def test_handle_event_issue(webhook_handler):
    # Mock the handle_issue method
    with patch.object(webhook_handler, 'handle_issue') as mock_handle:
        mock_handle.return_value = ({"status": "success"}, 200)

        # Call the method
        result, status = webhook_handler.handle_event("issues", {"action": "opened"})

        # Verify the result
        assert result == {"status": "success"}
        assert status == 200
        mock_handle.assert_called_once_with({"action": "opened"})

def test_handle_event_push(webhook_handler):
    # Mock the handle_push method
    with patch.object(webhook_handler, 'handle_push') as mock_handle:
        mock_handle.return_value = ({"status": "success"}, 200)

        # Call the method
        result, status = webhook_handler.handle_event("push", {"ref": "refs/heads/main"})

        # Verify the result
        assert result == {"status": "success"}
        assert status == 200
        mock_handle.assert_called_once_with({"ref": "refs/heads/main"})

def test_handle_event_unsupported(webhook_handler):
    # Call the method with an unsupported event type
    result, status = webhook_handler.handle_event("unsupported_event", {})

    # Verify the result
    assert "Unsupported event type" in result["message"]
    assert status == 400

def test_handle_pull_request_opened(webhook_handler):
    # Create a test payload
    payload = {
        "action": "opened",
        "pull_request": {
            "number": 123,
            "head": {
                "ref": "feature-branch",
                "sha": "abc123"
            }
        },
        "repository": {
            "full_name": "test/repo"
        }
    }

    # Mock the track_pull_request and queue_analysis methods
    webhook_handler.github.track_pull_request.return_value = None
    webhook_handler.github.queue_analysis.return_value = Mock(id="task_123")

    # Call the method
    result, status = webhook_handler.handle_pull_request(payload)

    # Verify the result
    assert result["status"] == "success"
    assert result["action"] == "opened"
    assert result["task_id"] == "task_123"
    assert status == 200

    # Verify the method calls
    webhook_handler.github.track_pull_request.assert_called_once_with("test/repo", 123)
    webhook_handler.github.queue_analysis.assert_called_once_with("test/repo", 123)

def test_handle_pull_request_synchronize(webhook_handler):
    # Create a test payload
    payload = {
        "action": "synchronize",
        "pull_request": {
            "number": 123,
            "head": {
                "ref": "feature-branch",
                "sha": "abc123"
            }
        },
        "repository": {
            "full_name": "test/repo"
        }
    }

    # Mock the track_pull_request and queue_analysis methods
    webhook_handler.github.track_pull_request.return_value = None
    webhook_handler.github.queue_analysis.return_value = Mock(id="task_123")

    # Call the method
    result, status = webhook_handler.handle_pull_request(payload)

    # Verify the result
    assert result["status"] == "success"
    assert result["action"] == "synchronize"
    assert result["task_id"] == "task_123"
    assert status == 200

    # Verify the method calls
    webhook_handler.github.track_pull_request.assert_called_once_with("test/repo", 123)
    webhook_handler.github.queue_analysis.assert_called_once_with("test/repo", 123)

def test_handle_pull_request_closed_merged(webhook_handler):
    # Create a test payload
    payload = {
        "action": "closed",
        "pull_request": {
            "number": 123,
            "merged": True
        },
        "repository": {
            "full_name": "test/repo"
        }
    }

    # Mock the track_merge method
    webhook_handler.github.track_merge.return_value = None

    # Call the method
    result, status = webhook_handler.handle_pull_request(payload)

    # Verify the result
    assert result["status"] == "success"
    assert result["action"] == "merged"
    assert status == 200

    # Verify the method calls
    webhook_handler.github.track_merge.assert_called_once_with("test/repo", 123)

def test_handle_pull_request_closed_not_merged(webhook_handler):
    # Create a test payload
    payload = {
        "action": "closed",
        "pull_request": {
            "number": 123,
            "merged": False
        },
        "repository": {
            "full_name": "test/repo"
        }
    }

    # Call the method
    result, status = webhook_handler.handle_pull_request(payload)

    # Verify the result
    assert result["status"] == "success"
    assert result["action"] == "closed"
    assert status == 200

    # Verify no method calls
    webhook_handler.github.track_merge.assert_not_called()

def test_handle_pull_request_invalid_payload(webhook_handler):
    # Create an invalid payload
    payload = {
        "action": "opened"
        # Missing required fields
    }

    # Call the method
    result, status = webhook_handler.handle_pull_request(payload)

    # Verify the result
    assert "Invalid payload structure" in result["error"]
    assert status == 400

def test_handle_pull_request_error(webhook_handler):
    # Create a test payload
    payload = {
        "action": "opened",
        "pull_request": {
            "number": 123
        },
        "repository": {
            "full_name": "test/repo"
        }
    }

    # Mock the track_pull_request method to raise an exception
    webhook_handler.github.track_pull_request.side_effect = Exception("API Error")

    # Call the method
    result, status = webhook_handler.handle_pull_request(payload)

    # Verify the result
    assert "Error handling pull request" in result["error"]
    assert status == 500

def test_handle_issue_opened(webhook_handler):
    # Create a test payload
    payload = {
        "action": "opened",
        "issue": {
            "number": 123
        },
        "repository": {
            "full_name": "test/repo"
        }
    }

    # Mock the assign_reviewer method
    webhook_handler.github.assign_reviewer.return_value = None

    # Call the method
    result, status = webhook_handler.handle_issue(payload)

    # Verify the result
    assert result["status"] == "success"
    assert result["action"] == "opened"
    assert result["assigned"] == True
    assert status == 200

    # Verify the method calls
    webhook_handler.github.assign_reviewer.assert_called_once_with("test/repo", 123)

def test_handle_issue_closed(webhook_handler):
    # Create a test payload
    payload = {
        "action": "closed",
        "issue": {
            "number": 123
        },
        "repository": {
            "full_name": "test/repo"
        }
    }

    # Mock the track_issue_resolution method
    webhook_handler.github.track_issue_resolution.return_value = None

    # Call the method
    result, status = webhook_handler.handle_issue(payload)

    # Verify the result
    assert result["status"] == "success"
    assert result["action"] == "closed"
    assert result["resolved"] == True
    assert status == 200

    # Verify the method calls
    webhook_handler.github.track_issue_resolution.assert_called_once_with("test/repo", 123)

def test_handle_issue_labeled(webhook_handler):
    # Create a test payload
    payload = {
        "action": "labeled",
        "issue": {
            "number": 123,
            "labels": [
                {"name": "bug"},
                {"name": "enhancement"}
            ]
        },
        "repository": {
            "full_name": "test/repo"
        }
    }

    # Call the method
    result, status = webhook_handler.handle_issue(payload)

    # Verify the result
    assert result["status"] == "success"
    assert result["action"] == "labeled"
    assert "bug" in result["labels"]
    assert "enhancement" in result["labels"]
    assert status == 200

def test_handle_issue_invalid_payload(webhook_handler):
    # Create an invalid payload
    payload = {
        "action": "opened"
        # Missing required fields
    }

    # Call the method
    result, status = webhook_handler.handle_issue(payload)

    # Verify the result
    assert "Invalid payload structure" in result["error"]
    assert status == 400

def test_handle_issue_error(webhook_handler):
    # Create a test payload
    payload = {
        "action": "opened",
        "issue": {
            "number": 123
        },
        "repository": {
            "full_name": "test/repo"
        }
    }

    # Mock the assign_reviewer method to raise an exception
    webhook_handler.github.assign_reviewer.side_effect = Exception("API Error")

    # Call the method
    result, status = webhook_handler.handle_issue(payload)

    # Verify the result
    assert "Error handling issue" in result["error"]
    assert status == 500

def test_handle_push(webhook_handler):
    # Create a test payload
    payload = {
        "ref": "refs/heads/main",
        "repository": {
            "full_name": "test/repo"
        },
        "commits": [
            {"id": "abc123", "message": "Test commit"}
        ]
    }

    # Mock the clone_repository and update_status methods
    webhook_handler.github.clone_repository.return_value = "./repos/test_repo"
    webhook_handler.github.update_status.return_value = None

    # Call the method
    result, status = webhook_handler.handle_push(payload)

    # Verify the result
    assert result["status"] == "success"
    assert result["ref"] == "refs/heads/main"
    assert result["branch"] == "main"
    assert result["commits"] == 1
    assert status == 200

    # Verify the method calls
    webhook_handler.github.clone_repository.assert_called_once_with("test/repo", "main")
    webhook_handler.github.update_status.assert_called_once()

def test_handle_push_no_commits(webhook_handler):
    # Create a test payload with no commits
    payload = {
        "ref": "refs/heads/main",
        "repository": {
            "full_name": "test/repo"
        },
        "commits": []
    }

    # Call the method
    result, status = webhook_handler.handle_push(payload)

    # Verify the result
    assert result["status"] == "success"
    assert result["ref"] == "refs/heads/main"
    assert result["branch"] == "main"
    assert result["commits"] == 0
    assert status == 200

    # Verify no method calls
    webhook_handler.github.clone_repository.assert_not_called()
    webhook_handler.github.update_status.assert_not_called()

def test_handle_push_invalid_payload(webhook_handler):
    # Create an invalid payload
    payload = {
        # Missing required fields
    }

    # Call the method
    result, status = webhook_handler.handle_push(payload)

    # Verify the result
    assert "Invalid payload structure" in result["error"]
    assert status == 400

def test_handle_push_error(webhook_handler):
    # Create a test payload
    payload = {
        "ref": "refs/heads/main",
        "repository": {
            "full_name": "test/repo"
        },
        "commits": [
            {"id": "abc123", "message": "Test commit"}
        ]
    }

    # Mock the clone_repository method to raise an exception
    webhook_handler.github.clone_repository.side_effect = Exception("API Error")

    # Call the method
    result, status = webhook_handler.handle_push(payload)

    # Verify the result
    assert "Error processing repository" in result["error"]
    assert status == 500
