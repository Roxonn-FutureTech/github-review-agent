# API Documentation

This document provides detailed information about the GitHub Review Agent's REST API endpoints.

## Authentication

All API requests require authentication using a GitHub Personal Access Token:

```http
Authorization: Bearer <your-github-token>
```

## Rate Limiting

- 5000 requests per hour for authenticated requests
- 60 requests per hour for unauthenticated requests
- Rate limit headers included in all responses

## API Endpoints

### Review Management

#### Trigger Review

```http
POST /api/review
```

Triggers a code review for a specific pull request.

**Request Body:**

```json
{
    "repository": "owner/repo",
    "pull_request_number": 123,
    "review_type": "full" // or "quick"
}
```

**Response:**

```json
{
    "review_id": "rev_123abc",
    "status": "in_progress",
    "estimated_completion_time": "2023-12-01T15:30:00Z"
}
```

#### Get Review Status

```http
GET /api/status/:review_id
```

Checks the status of a specific review.

**Response:**

```json
{
    "review_id": "rev_123abc",
    "status": "completed",
    "findings": [{
        "type": "style",
        "severity": "warning",
        "file": "src/main.py",
        "line": 45,
        "message": "Line exceeds maximum length"
    }]
}
```

### Configuration Management

#### Update Configuration

```http
PUT /api/config
```

Updates the review agent's configuration.

**Request Body:**

```json
{
    "rules": {
        "max_line_length": 100,
        "check_docstrings": true,
        "security_checks": ["sql_injection", "xss"]
    },
    "notification_settings": {
        "email_notifications": true,
        "slack_webhook": "https://hooks.slack.com/..."
    }
}
```

**Response:**

```json
{
    "status": "success",
    "message": "Configuration updated successfully"
}
```

#### Get Current Configuration

```http
GET /api/config
```

Retrieves current configuration settings.

### Webhook Integration

#### Register Webhook

```http
POST /api/webhooks
```

Registers a new webhook for repository events.

**Request Body:**

```json
{
    "url": "https://your-server.com/webhook",
    "events": ["pull_request", "push"],
    "secret": "your-webhook-secret"
}
```

## Error Handling

All errors follow this format:

```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "details": {}
    }
}
```

Common error codes:

- `UNAUTHORIZED`: Invalid or missing authentication
- `RATE_LIMITED`: Rate limit exceeded
- `INVALID_REQUEST`: Malformed request
- `NOT_FOUND`: Resource not found
- `INTERNAL_ERROR`: Server error

## SDK Examples

### Python

```python
from github_review_agent import ReviewClient

client = ReviewClient(token="your-github-token")
review = client.create_review(
    repository="owner/repo",
    pull_request=123
)
```

### JavaScript

```javascript
const { ReviewClient } = require('github-review-agent');

const client = new ReviewClient({ token: 'your-github-token' });
const review = await client.createReview({
    repository: 'owner/repo',
    pullRequest: 123
});
```

## Best Practices

1. Always handle rate limits
2. Implement exponential backoff for retries
3. Store tokens securely
4. Validate webhook payloads
5. Monitor API usage

## Support

For API support:

- Documentation Issues: Create an issue with tag `api-docs`
- API Status: Check status.roxonn-futuretech.com
