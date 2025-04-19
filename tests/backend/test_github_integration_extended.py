import pytest
from unittest.mock import patch, Mock
from src.backend.github_integration import GitHubIntegration
from src.backend.exceptions import GitHubAuthError, WebhookError
from github import Auth

class TestGitHubIntegrationExtended:
    @pytest.fixture
    def mock_github(self):
        with patch('src.backend.github_integration.Github') as mock:
            yield mock

    @pytest.fixture
    def mock_auth(self):
        with patch('src.backend.github_integration.Auth.AppAuth') as mock:
            yield mock

    @pytest.fixture
    def github_integration(self, mock_github, mock_auth):
        # Configure the mock to return a successful authentication
        mock_auth.return_value = Mock()
        # Create an instance of GitHubIntegration with mock authentication
        integration = GitHubIntegration(app_id="test_id", private_key="test_key")
        # Configure the Github mock for use in tests
        integration.github = mock_github
        return integration

    def test_create_comment(self, github_integration):
        # Mock the repository and issue
        mock_repo = Mock()
        mock_issue = Mock()
        mock_comment = Mock()

        # Configure the mocks
        github_integration.github.get_repo.return_value = mock_repo
        mock_repo.get_issue.return_value = mock_issue
        mock_issue.create_comment.return_value = mock_comment

        # Configure the comment object
        mock_comment.id = 12345
        mock_comment.body = "Test comment"
        mock_comment.created_at.isoformat.return_value = "2023-01-01T12:00:00Z"

        # Call the method
        result = github_integration.create_comment("test/repo", 123, "Test comment")

        # Verify the result
        assert result["id"] == 12345
        assert result["body"] == "Test comment"

        # Verify the method calls
        github_integration.github.get_repo.assert_called_once_with("test/repo")
        mock_repo.get_issue.assert_called_once_with(number=123)
        mock_issue.create_comment.assert_called_once_with("Test comment")

    def test_create_comment_error(self, github_integration):
        # Mock the repository to raise an exception
        github_integration.github.get_repo.side_effect = Exception("API Error")

        # Call the method and expect an exception
        with pytest.raises(WebhookError) as exc_info:
            github_integration.create_comment("test/repo", 123, "Test comment")

        assert "Failed to create comment" in str(exc_info.value)

    def test_add_label(self, github_integration):
        # Mock the repository and issue
        mock_repo = Mock()
        mock_issue = Mock()

        # Configure the mocks
        github_integration.github.get_repo.return_value = mock_repo
        mock_repo.get_issue.return_value = mock_issue
        mock_repo.get_label.return_value = Mock()  # Label exists

        # Call the method
        github_integration.add_label("test/repo", 123, "bug")

        # Verify the method calls
        github_integration.github.get_repo.assert_called_once_with("test/repo")
        mock_repo.get_issue.assert_called_once_with(number=123)
        mock_repo.get_label.assert_called_once_with("bug")
        mock_issue.add_to_labels.assert_called_once_with("bug")

    def test_add_label_error(self, github_integration):
        # Mock the repository to raise an exception
        github_integration.github.get_repo.side_effect = Exception("API Error")

        # Call the method and expect an exception
        with pytest.raises(WebhookError) as exc_info:
            github_integration.add_label("test/repo", 123, "bug")

        assert "Failed to add label" in str(exc_info.value)

    def test_queue_analysis(self, github_integration):
        # Mock the repository and pull request
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.head = Mock()
        mock_pr.head.ref = "feature-branch"
        mock_pr.head.sha = "abc123"

        github_integration.github.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr

        # Mock the clone_repository method
        with patch.object(github_integration, 'clone_repository') as mock_clone:
            mock_clone.return_value = "./repos/test_repo"

            # Mock the update_status method
            with patch.object(github_integration, 'update_status') as mock_update:
                # Call the method
                task = github_integration.queue_analysis("test/repo", 123)

                # Verify the result
                assert task.id == "task_test_repo_123"
                assert task.repo == "test/repo"
                assert task.pr_number == 123
                assert task.local_path == "./repos/test_repo"
                assert task.status == "queued"

                # Verify the method calls
                github_integration.github.get_repo.assert_called_once_with("test/repo")
                mock_repo.get_pull.assert_called_once_with(123)
                mock_clone.assert_called_once_with("test/repo", "feature-branch")
                mock_update.assert_called_once()

    def test_queue_analysis_error(self, github_integration):
        # Mock the repository to raise an exception
        github_integration.github.get_repo.side_effect = Exception("API Error")

        # Call the method and expect an exception
        with pytest.raises(Exception) as exc_info:
            github_integration.queue_analysis("test/repo", 123)

        assert "API Error" in str(exc_info.value)

    def test_track_merge(self, github_integration):
        # Mock the repository and pull request
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.merged = True

        github_integration.github.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr

        # Mock the create_comment method
        with patch.object(github_integration, 'create_comment') as mock_comment:
            # Call the method
            github_integration.track_merge("test/repo", 123)

            # Verify the method calls
            github_integration.github.get_repo.assert_called_once_with("test/repo")
            mock_repo.get_pull.assert_called_once_with(123)
            mock_comment.assert_called_once()

    def test_track_merge_not_merged(self, github_integration):
        # Mock the repository and pull request that is not merged
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.merged = False

        github_integration.github.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr

        # Mock the create_comment method
        with patch.object(github_integration, 'create_comment') as mock_comment:
            # Call the method
            github_integration.track_merge("test/repo", 123)

            # Verify the method calls
            github_integration.github.get_repo.assert_called_once_with("test/repo")
            mock_repo.get_pull.assert_called_once_with(123)
            mock_comment.assert_not_called()

    def test_track_merge_error(self, github_integration):
        # Mock the repository to raise an exception
        github_integration.github.get_repo.side_effect = Exception("API Error")

        # Call the method and expect an exception
        with pytest.raises(Exception) as exc_info:
            github_integration.track_merge("test/repo", 123)

        assert "API Error" in str(exc_info.value)

    def test_assign_reviewer(self, github_integration):
        # Mock the repository and issue
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.user = Mock()
        mock_issue.user.login = "user1"

        # Mock collaborators
        mock_collaborator1 = Mock()
        mock_collaborator1.login = "user1"  # Same as issue creator
        mock_collaborator2 = Mock()
        mock_collaborator2.login = "user2"  # Different user

        github_integration.github.get_repo.return_value = mock_repo
        mock_repo.get_issue.return_value = mock_issue
        mock_repo.get_collaborators.return_value = [mock_collaborator1, mock_collaborator2]

        # Mock the create_comment and add_label methods
        with patch.object(github_integration, 'create_comment') as mock_comment:
            with patch.object(github_integration, 'add_label') as mock_label:
                # Call the method
                github_integration.assign_reviewer("test/repo", 123)

                # Verify the method calls
                github_integration.github.get_repo.assert_called_once_with("test/repo")
                mock_repo.get_issue.assert_called_once_with(123)
                mock_repo.get_collaborators.assert_called_once()
                mock_comment.assert_called_once()
                mock_label.assert_called_once_with("test/repo", 123, "assigned")

    def test_assign_reviewer_no_collaborators(self, github_integration):
        # Mock the repository and issue
        mock_repo = Mock()
        mock_issue = Mock()

        github_integration.github.get_repo.return_value = mock_repo
        mock_repo.get_issue.return_value = mock_issue
        mock_repo.get_collaborators.return_value = []  # No collaborators

        # Mock the create_comment and add_label methods
        with patch.object(github_integration, 'create_comment') as mock_comment:
            with patch.object(github_integration, 'add_label') as mock_label:
                # Call the method
                github_integration.assign_reviewer("test/repo", 123)

                # Verify the method calls
                github_integration.github.get_repo.assert_called_once_with("test/repo")
                mock_repo.get_issue.assert_called_once_with(123)
                mock_repo.get_collaborators.assert_called_once()
                mock_comment.assert_not_called()
                mock_label.assert_not_called()

    def test_assign_reviewer_error(self, github_integration):
        # Mock the repository to raise an exception
        github_integration.github.get_repo.side_effect = Exception("API Error")

        # Call the method and expect an exception
        with pytest.raises(Exception) as exc_info:
            github_integration.assign_reviewer("test/repo", 123)

        assert "API Error" in str(exc_info.value)

    def test_track_issue_resolution(self, github_integration):
        # Mock the repository and issue
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.state = "closed"

        github_integration.github.get_repo.return_value = mock_repo
        mock_repo.get_issue.return_value = mock_issue

        # Mock the create_comment and add_label methods
        with patch.object(github_integration, 'create_comment') as mock_comment:
            with patch.object(github_integration, 'add_label') as mock_label:
                # Call the method
                github_integration.track_issue_resolution("test/repo", 123)

                # Verify the method calls
                github_integration.github.get_repo.assert_called_once_with("test/repo")
                mock_repo.get_issue.assert_called_once_with(123)
                mock_comment.assert_called_once()
                mock_label.assert_called_once_with("test/repo", 123, "resolved")

    def test_track_issue_resolution_not_closed(self, github_integration):
        # Mock the repository and issue that is not closed
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.state = "open"

        github_integration.github.get_repo.return_value = mock_repo
        mock_repo.get_issue.return_value = mock_issue

        # Mock the create_comment and add_label methods
        with patch.object(github_integration, 'create_comment') as mock_comment:
            with patch.object(github_integration, 'add_label') as mock_label:
                # Call the method
                github_integration.track_issue_resolution("test/repo", 123)

                # Verify the method calls
                github_integration.github.get_repo.assert_called_once_with("test/repo")
                mock_repo.get_issue.assert_called_once_with(123)
                mock_comment.assert_not_called()
                mock_label.assert_not_called()

    def test_track_issue_resolution_error(self, github_integration):
        # Mock the repository to raise an exception
        github_integration.github.get_repo.side_effect = Exception("API Error")

        # Call the method and expect an exception
        with pytest.raises(Exception) as exc_info:
            github_integration.track_issue_resolution("test/repo", 123)

        assert "API Error" in str(exc_info.value)
