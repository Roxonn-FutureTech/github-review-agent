from flask import Flask, request, jsonify
from typing import Dict, Any, Tuple
import hmac
import hashlib

from .exceptions import WebhookError
from .github_integration import GitHubIntegration
from ai_engine.logging_config import get_logger, setup_logging

app = Flask(__name__)
webhook_handler = None

class WebhookHandler:
    def __init__(self, webhook_secret: str, github_client: GitHubIntegration, logger):
        self.webhook_secret = webhook_secret
        self.github = github_client
        self.logger = logger if logger else get_logger(__name__)

    def verify_webhook(self, signature: str, payload: bytes) -> bool:
        """Verify GitHub webhook signature."""
        if not self.webhook_secret:
            return True

        if not signature or not signature.startswith('sha256='):
            return False

        # Create the expected signature
        expected_signature = 'sha256=' + hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def handle_event(self, event_type: str, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Handle GitHub webhook event."""
        handlers = {
            'pull_request': self.handle_pull_request,
            'issues': self.handle_issue,
            'push': self.handle_push
        }

        handler = handlers.get(event_type)
        if not handler:
            return {"message": f"Unsupported event type: {event_type}"}, 400

        return handler(payload)

    def handle_pull_request(self, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Handle pull request events."""
        try:
            action = payload.get('action')
            pr = payload.get('pull_request', {})
            repo = payload.get('repository', {}).get('full_name')

            if not all([action, pr, repo]):
                return {"error": "Invalid payload structure"}, 400

            pr_number = pr.get('number')
            if not pr_number:
                return {"error": "Missing pull request number"}, 400

            # Track the pull request based on the action
            if action == 'opened' or action == 'synchronize':
                self.github.track_pull_request(repo, pr_number)
                task = self.github.queue_analysis(repo, pr_number)
                return {"status": "success", "action": action, "task_id": task.id}, 200
            elif action == 'closed' and pr.get('merged'):
                self.github.track_merge(repo, pr_number)
                return {"status": "success", "action": "merged"}, 200

            return {"status": "success", "action": action}, 200

        except Exception as e:
            self.logger.error(f"Error handling pull request: {str(e)}")
            return {"error": f"Error handling pull request: {str(e)}"}, 500

    def handle_issue(self, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Handle issue events."""
        try:
            action = payload.get('action')
            issue = payload.get('issue', {})
            repo = payload.get('repository', {}).get('full_name')

            if not all([action, issue, repo]):
                return {"error": "Invalid payload structure"}, 400

            issue_number = issue.get('number')
            if not issue_number:
                return {"error": "Missing issue number"}, 400

            # Handle different issue actions
            if action == 'opened':
                # Assign a reviewer when an issue is opened
                self.github.assign_reviewer(repo, issue_number)
                return {"status": "success", "action": action, "assigned": True}, 200
            elif action == 'closed':
                # Track when an issue is resolved
                self.github.track_issue_resolution(repo, issue_number)
                return {"status": "success", "action": action, "resolved": True}, 200
            elif action == 'labeled':
                # Handle labeling events
                labels = issue.get('labels', [])
                label_names = [label.get('name') for label in labels if label.get('name')]
                return {"status": "success", "action": action, "labels": label_names}, 200

            return {"status": "success", "action": action}, 200

        except Exception as e:
            self.logger.error(f"Error handling issue: {str(e)}")
            return {"error": f"Error handling issue: {str(e)}"}, 500

    def handle_push(self, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Handle push events."""
        try:
            repo = payload.get('repository', {}).get('full_name')
            ref = payload.get('ref')
            commits = payload.get('commits', [])

            if not all([repo, ref]):
                return {"error": "Invalid payload structure"}, 400

            # Extract branch name from ref (refs/heads/branch-name)
            branch = ref.replace('refs/heads/', '') if ref.startswith('refs/heads/') else ref

            # Clone or update the repository if there are commits
            if commits and repo:
                try:
                    # Clone the repository with the specific branch
                    local_path = self.github.clone_repository(repo, branch)
                    self.logger.info(f"Repository cloned/updated at {local_path}")

                    # Update status for the latest commit
                    if commits:
                        latest_commit = commits[-1]
                        commit_sha = latest_commit.get('id')
                        if commit_sha:
                            self.github.update_status(
                                repo=repo,
                                commit_sha=commit_sha,
                                state="success",
                                description="Push received and processed"
                            )
                except Exception as e:
                    self.logger.error(f"Error processing repository: {str(e)}")
                    return {"error": f"Error processing repository: {str(e)}"}, 500

            return {"status": "success", "ref": ref, "branch": branch, "commits": len(commits)}, 200

        except Exception as e:
            self.logger.error(f"Error handling push: {str(e)}")
            return {"error": str(e)}, 500

def initialize_webhook_handler():
    """Initialize the webhook handler with configuration."""
    global webhook_handler
    if webhook_handler is None:
        webhook_secret = app.config.get('WEBHOOK_SECRET')
        github_client = GitHubIntegration(
            app_id=app.config.get('GITHUB_APP_ID'),
            private_key=app.config.get('GITHUB_PRIVATE_KEY')
        )
        logger = setup_logging()
        webhook_handler = WebhookHandler(webhook_secret, github_client, logger)
    return webhook_handler

@app.before_request
def before_request():
    """Initialize webhook handler before each request if not already initialized."""
    initialize_webhook_handler()

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handle incoming GitHub webhook."""
    try:
        signature = request.headers.get('X-Hub-Signature-256')
        if not signature:
            return jsonify({"error": "No signature provided"}), 400

        if not webhook_handler.verify_webhook(signature, request.data):
            return jsonify({"error": "Invalid signature"}), 400

        event = request.headers.get('X-GitHub-Event')
        if not event:
            return jsonify({"error": "No event type provided"}), 400

        payload = request.json
        if not payload:
            return jsonify({"error": "No payload provided"}), 400

        response, status_code = webhook_handler.handle_event(event, payload)
        return jsonify(response), status_code

    except WebhookError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        webhook_handler.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Expose these for testing
def get_webhook_handler():
    """Get the current webhook handler instance."""
    return webhook_handler

def set_webhook_handler(handler):
    """Set the webhook handler instance (for testing)."""
    global webhook_handler
    webhook_handler = handler
