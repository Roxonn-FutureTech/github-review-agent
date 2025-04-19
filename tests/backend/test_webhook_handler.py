import pytest
from unittest.mock import patch, Mock
from src.backend.webhook_handler import app, WebhookHandler, set_webhook_handler
from src.backend.exceptions import WebhookError
from github import Auth

@pytest.fixture
def test_client():
    """Create a test client for the Flask app."""
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_github():
    """Mock the GitHub client."""
    with patch('src.backend.github_integration.Github') as mock:
        yield mock

@pytest.fixture
def mock_auth():
    """Mock the GitHub authentication."""
    with patch('src.backend.github_integration.Auth.AppAuth') as mock:
        yield mock

@pytest.fixture
def webhook_handler(mock_github, mock_auth):
    """Create a webhook handler instance for testing."""
    mock_auth.return_value = Mock()
    handler = WebhookHandler(webhook_secret="test_secret", github_client=mock_github, logger=Mock())
    set_webhook_handler(handler)
    return handler

def test_webhook_verification(webhook_handler):
    """Test webhook signature verification."""
    import hmac
    import hashlib

    # Test with mocked verification
    with patch.object(webhook_handler, 'verify_webhook', side_effect=lambda sig, pay: True):
        assert webhook_handler.verify_webhook('test_signature', b'test_payload')

    # Test with real verification but patched secret
    webhook_handler.webhook_secret = 'test_secret'
    payload = b'test_payload'

    # Generate the correct signature using the same algorithm as in the implementation
    expected_signature = 'sha256=' + hmac.new(
        'test_secret'.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    # Test valid signature
    assert webhook_handler.verify_webhook(expected_signature, payload)

    # Test invalid signature
    invalid_signature = 'sha256=invalid'
    assert not webhook_handler.verify_webhook(invalid_signature, payload)

def test_webhook_endpoint_no_signature(test_client):
    """Test webhook endpoint without signature."""
    response = test_client.post('/webhook', json={})
    assert response.status_code == 400
    assert b'No signature provided' in response.data

def test_webhook_endpoint_invalid_signature(test_client, webhook_handler):
    """Test webhook endpoint with invalid signature."""
    response = test_client.post(
        '/webhook',
        json={},
        headers={'X-Hub-Signature-256': 'invalid'}
    )
    assert response.status_code == 400
    assert b'Invalid signature' in response.data

def test_webhook_endpoint_no_event(test_client, webhook_handler):
    """Test webhook endpoint without event type."""
    # Mock the verify_webhook method to return True
    with patch.object(webhook_handler, 'verify_webhook', return_value=True):
        response = test_client.post(
            '/webhook',
            json={},
            headers={'X-Hub-Signature-256': 'sha256=valid'}
        )
        assert response.status_code == 400
        assert b'No event type provided' in response.data

def test_webhook_endpoint_success(test_client, webhook_handler):
    """Test successful webhook processing."""
    with patch.object(webhook_handler, 'verify_webhook', return_value=True):
        with patch.object(webhook_handler, 'handle_event', return_value=({'status': 'success'}, 200)):
            response = test_client.post(
                '/webhook',
                json={'action': 'opened'},
                headers={
                    'X-Hub-Signature-256': 'sha256=valid',
                    'X-GitHub-Event': 'pull_request'
                }
            )
            assert response.status_code == 200
            assert response.json == {'status': 'success'}
