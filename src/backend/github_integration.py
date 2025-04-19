from typing import Dict, Any
import requests
import logging
import jwt
import time
from github import Github
from .exceptions import WebhookError, GitHubAuthError
import os

# Auth class for unit testing
class Auth:
    """Authentication utilities for GitHub API."""

    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
        """Verify the webhook signature."""
        import hmac
        import hashlib

        if not signature:
            return False

        # Get signature hash algorithm and signature
        algorithm, signature = signature.split('=')
        if algorithm != 'sha1':
            return False

        # Calculate expected signature
        mac = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha1)
        expected_signature = mac.hexdigest()

        # Compare signatures
        return hmac.compare_digest(signature, expected_signature)

class GitHubIntegration:
    """Client for interacting with GitHub API."""

    def __init__(self, app_id: str, private_key: str):
        try:
            # Store credentials for later use
            self.app_id = app_id
            self.private_key = private_key
            self.logger = logging.getLogger(__name__)

            # Create a JWT for GitHub App authentication
            jwt_token = self._create_jwt()
            print(f"✅ JWT token created successfully: {jwt_token[:20]}...")

            # Create a Github instance with the JWT
            self.github = Github(login_or_token=jwt_token)
            print("✅ GitHub integration initialized successfully")
        except Exception as e:
            raise GitHubAuthError(f"Failed to initialize GitHub client: {str(e)}")

    def _create_jwt(self):
        """Create a JWT for GitHub App authentication."""
        now = int(time.time())
        payload = {
            "iat": now,
            "exp": now + 600,  # 10 minutes expiration
            "iss": self.app_id
        }

        try:
            # Use PyJWT to create a JWT token
            # For debugging, print the first and last lines of the private key
            if self.private_key:
                lines = self.private_key.strip().split('\n')
                print(f"Private key first line: {lines[0]}")
                print(f"Private key last line: {lines[-1] if len(lines) > 1 else 'N/A'}")
                print(f"Private key length: {len(self.private_key)}")

            # Use cryptography to load the private key
            from cryptography.hazmat.primitives.serialization import load_pem_private_key
            from cryptography.hazmat.backends import default_backend

            # Convert the private key to bytes
            private_key_bytes = self.private_key.encode('utf-8')

            # Load the private key
            private_key_obj = load_pem_private_key(
                private_key_bytes,
                password=None,
                backend=default_backend()
            )

            # Use the private key to sign the JWT
            return jwt.encode(payload, private_key_obj, algorithm="RS256")
        except Exception as e:
            self.logger.error(f"Error creating JWT: {str(e)}")
            raise GitHubAuthError(f"Failed to create JWT: {str(e)}")

    def _get_installation_token(self, installation_id):
        """Get an installation token for a specific installation."""
        try:
            # Get a JWT token with the properly formatted private key
            jwt_token = self._create_jwt()

            # Request an installation token
            url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
            headers = {
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github.v3+json"
            }

            self.logger.info(f"Requesting installation token for installation ID: {installation_id}")
            response = requests.post(url, headers=headers)

            if response.status_code != 201:
                error_msg = f"Failed to get installation token: {response.status_code} {response.text}"
                self.logger.error(error_msg)
                raise GitHubAuthError(error_msg)

            token = response.json()["token"]
            self.logger.info(f"Successfully obtained installation token")
            print(f"✅ Installation token obtained: {token[:10]}...")
            return token
        except Exception as e:
            self.logger.error(f"Failed to get installation token: {str(e)}")
            raise GitHubAuthError(f"Failed to get installation token: {str(e)}")

    def track_pull_request(self, repo: str, pr_number: int) -> None:
        """Track a pull request for analysis."""
        self.logger.info(f"Tracking PR #{pr_number} in {repo}")
        try:
            repository = self.github.get_repo(repo)
            pr = repository.get_pull(pr_number)
            # Use the PR object to track it
            self.logger.info(f"PR #{pr_number} tracked: {pr.title}")
            # Additional tracking logic can be added here
        except Exception as e:
            self.logger.error(f"Error tracking PR: {str(e)}")
            raise

    def clone_repository(self, repo: str, branch: str = None) -> str:
        """Clone a repository to local storage."""
        try:
            repository = self.github.get_repo(repo)
            clone_url = repository.clone_url
            local_path = f"./repos/{repo.replace('/', '_')}"

            if not os.path.exists(local_path):
                if branch:
                    clone_cmd = f"git clone -b {branch} {clone_url} {local_path}"
                else:
                    clone_cmd = f"git clone {clone_url} {local_path}"
                os.system(clone_cmd)

            return local_path
        except Exception as e:
            self.logger.error(f"Error cloning repository: {str(e)}")
            raise

    def update_status(self, repo: str, commit_sha: str, state: str, description: str) -> None:
        """Update the status of a commit."""
        try:
            repository = self.github.get_repo(repo)
            commit = repository.get_commit(commit_sha)
            commit.create_status(
                state=state,
                description=description,
                context="github-review-agent"
            )
        except Exception as e:
            self.logger.error(f"Error updating status: {str(e)}")
            raise

    def create_comment(self, repo: str, pr_number: int, comment: str) -> Dict[str, Any]:
        """Create a comment on a pull request or issue."""
        try:
            repository = self.github.get_repo(repo)
            issue = repository.get_issue(number=pr_number)
            comment_obj = issue.create_comment(comment)
            return {
                "id": comment_obj.id,
                "body": comment_obj.body,
                "created_at": comment_obj.created_at.isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error creating comment: {str(e)}")
            raise WebhookError(f"Failed to create comment: {str(e)}")

    def add_label(self, repo: str, issue_number: int, label: str) -> None:
        """Add a label to an issue."""
        try:
            repository = self.github.get_repo(repo)
            issue = repository.get_issue(number=issue_number)

            # Check if the label exists, create it if it doesn't
            try:
                repository.get_label(label)
            except Exception:
                repository.create_label(name=label, color="0366d6")

            # Add the label to the issue
            issue.add_to_labels(label)
        except Exception as e:
            self.logger.error(f"Error adding label: {str(e)}")
            raise WebhookError(f"Failed to add label: {str(e)}")

    def queue_analysis(self, repo: str, pr_number: int) -> Any:
        """Queue a PR for analysis."""
        self.logger.info(f"Queuing analysis for PR #{pr_number} in {repo}")
        try:
            repository = self.github.get_repo(repo)
            pull_request = repository.get_pull(pr_number)

            # Clone the repository to analyze the code
            local_path = self.clone_repository(repo, pull_request.head.ref)

            # Create a task object with metadata
            task = type('AnalysisTask', (), {
                'id': f"task_{repo.replace('/', '_')}_{pr_number}",
                'repo': repo,
                'pr_number': pr_number,
                'local_path': local_path,
                'status': 'queued'
            })()

            # Update PR with a status indicating analysis is in progress
            self.update_status(
                repo=repo,
                commit_sha=pull_request.head.sha,
                state="pending",
                description="Code analysis in progress"
            )

            return task
        except Exception as e:
            self.logger.error(f"Error queuing analysis: {str(e)}")
            raise

    def track_merge(self, repo: str, pr_number: int) -> None:
        """Track when a PR is merged."""
        self.logger.info(f"Tracking merge of PR #{pr_number} in {repo}")
        try:
            repository = self.github.get_repo(repo)
            pull_request = repository.get_pull(pr_number)

            # Verify the PR is actually merged
            if not pull_request.merged:
                self.logger.warning(f"PR #{pr_number} in {repo} is not merged")
                return

            # Add a comment to the PR indicating it was tracked
            self.create_comment(
                repo=repo,
                pr_number=pr_number,
                comment="✅ This PR has been merged and tracked by the GitHub Review Agent."
            )

            # Additional logic for tracking merged PRs can be added here
            # For example, updating statistics, triggering CI/CD, etc.
        except Exception as e:
            self.logger.error(f"Error tracking merge: {str(e)}")
            raise

    def assign_reviewer(self, repo: str, issue_number: int) -> None:
        """Assign a reviewer to an issue."""
        self.logger.info(f"Assigning reviewer to issue #{issue_number} in {repo}")
        try:
            repository = self.github.get_repo(repo)
            issue = repository.get_issue(issue_number)

            # Get potential reviewers (collaborators with push access)
            collaborators = list(repository.get_collaborators())
            if not collaborators:
                self.logger.warning(f"No collaborators found for {repo}")
                return

            # Simple algorithm: assign to the first collaborator who isn't the issue creator
            for collaborator in collaborators:
                if collaborator.login != issue.user.login:
                    # Add a comment mentioning the assigned reviewer
                    self.create_comment(
                        repo=repo,
                        pr_number=issue_number,  # Works for issues too
                        comment=f"@{collaborator.login} has been assigned to review this issue."
                    )

                    # Add a label indicating the issue has been assigned
                    self.add_label(repo, issue_number, "assigned")
                    break
        except Exception as e:
            self.logger.error(f"Error assigning reviewer: {str(e)}")
            raise

    def track_issue_resolution(self, repo: str, issue_number: int) -> None:
        """Track when an issue is resolved."""
        self.logger.info(f"Tracking resolution of issue #{issue_number} in {repo}")
        try:
            repository = self.github.get_repo(repo)
            issue = repository.get_issue(issue_number)

            # Verify the issue is actually closed
            if issue.state != "closed":
                self.logger.warning(f"Issue #{issue_number} in {repo} is not closed")
                return

            # Add a comment to the issue indicating it was tracked
            self.create_comment(
                repo=repo,
                pr_number=issue_number,  # Works for issues too
                comment="✅ This issue has been resolved and tracked by the GitHub Review Agent."
            )

            # Add a label indicating the issue has been resolved
            self.add_label(repo, issue_number, "resolved")
        except Exception as e:
            self.logger.error(f"Error tracking issue resolution: {str(e)}")
            raise
