class GitHubAuthError(Exception):
    """Raised when GitHub authentication fails"""
    pass

class WebhookError(Exception):
    """Raised when webhook processing fails"""
    pass

class RepositoryError(Exception):
    """Raised when repository operations fail"""
    pass

class PRError(Exception):
    """Raised when pull request operations fail"""
    pass
