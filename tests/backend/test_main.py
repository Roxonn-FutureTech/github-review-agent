import pytest
from unittest.mock import patch, MagicMock
import sys
import requests
from src.backend.main import main, fetch_pr_details
from src.backend.exceptions import GitHubAuthError

class TestMain:
    @pytest.fixture
    def mock_code_analyzer(self):
        with patch('src.backend.main.CodeAnalyzer') as mock:
            yield mock

    @pytest.fixture
    def mock_response(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            'title': 'Test PR',
            'body': 'Test description',
            'changed_files': 1,
            'additions': 10,
            'deletions': 5,
        }
        return mock_resp

    @pytest.fixture
    def mock_files_response(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [{'filename': 'test.py'}]
        return mock_resp

    def test_fetch_pr_details_with_token(self, mock_response, mock_files_response):
        with patch('requests.get') as mock_get:
            mock_get.side_effect = [mock_response, mock_files_response]
            result = fetch_pr_details("owner/repo", 123, "test-token")

            mock_get.assert_any_call(
                'https://api.github.com/repos/owner/repo/pulls/123',
                headers={'Authorization': 'token test-token'}
            )
            assert result['title'] == 'Test PR'
            assert result['changed_files'] == 1

    def test_fetch_pr_details_api_error(self):
        with patch('requests.get') as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 404
            mock_resp.json.return_value = {'message': 'Not Found'}
            mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error: Not Found")
            mock_get.return_value = mock_resp

            with pytest.raises(GitHubAuthError) as exc_info:
                fetch_pr_details("owner/repo", 123)
            assert "Failed to fetch PR details" in str(exc_info.value)

    def test_main_with_json_output(self, mock_code_analyzer, mock_response, mock_files_response):
        # Configure the mock_code_analyzer to return a valid result
        analyzer_instance = mock_code_analyzer.return_value
        analyzer_instance.analyze_pr.return_value = {
            'issues': [],
            'metrics': {'complexity': 5},
            'recommendations': ['Improve test coverage']
        }

        with patch('requests.get') as mock_get:
            mock_get.side_effect = [mock_response, mock_files_response]

            test_args = ['program', '--repo', 'owner/test_repo', '--pr', '123', '--output', 'json']
            with patch.object(sys, 'argv', test_args):
                with patch('builtins.print') as mock_print:
                    with patch('sys.exit') as mock_exit:
                        main()
                        mock_print.assert_called()
                        mock_exit.assert_not_called()

    def test_main_with_verbose_error(self, mock_code_analyzer):
        mock_code_analyzer.side_effect = Exception("Test error")

        test_args = ['program', '--repo', 'owner/test_repo', '--pr', '123', '--verbose']
        with patch.object(sys, 'argv', test_args):
            with patch('traceback.print_exc') as mock_traceback:
                with pytest.raises(SystemExit):
                    main()
                mock_traceback.assert_called_once()

    def test_main_with_invalid_output_format(self):
        test_args = ['program', '--repo', 'owner/test_repo', '--pr', '123', '--output', 'invalid']
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit):
                main()

