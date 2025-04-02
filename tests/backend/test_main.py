import pytest
from unittest.mock import patch, MagicMock
import os
import sys
import json
from src.backend.main import main, fetch_pr_details
from src.ai_engine.code_analyzer import CodeAnalyzer

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

    def test_main_with_valid_repo(self, mock_code_analyzer, mock_response, mock_files_response):
        mock_instance = MagicMock()
        mock_code_analyzer.return_value = mock_instance
        mock_instance.scan_repository.return_value = {
            'files': ['test.py'],
            'dependencies': {},
            'patterns': [],
            'graph': {}
        }

        # Mock both GitHub API calls
        with patch('requests.get') as mock_get:
            mock_get.side_effect = [mock_response, mock_files_response]
            
            test_args = ['program', '--repo', 'owner/test_repo', '--pr', '123']
            with patch.object(sys, 'argv', test_args):
                main()
                
                # Verify the API calls
                mock_get.assert_any_call(
                    'https://api.github.com/repos/owner/test_repo/pulls/123',
                    headers={}
                )
                mock_get.assert_any_call(
                    'https://api.github.com/repos/owner/test_repo/pulls/123/files',
                    headers={}
                )

    def test_main_with_invalid_repo(self, mock_code_analyzer):
        mock_instance = MagicMock()
        mock_code_analyzer.return_value = mock_instance
        mock_instance.scan_repository.side_effect = FileNotFoundError("Repository not found")

        test_args = ['program', '--repo', 'owner/nonexistent', '--pr', '123']
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit):
                main()

    def test_main_with_model_error(self, mock_code_analyzer):
        mock_instance = MagicMock()
        mock_code_analyzer.return_value = mock_instance
        mock_instance.scan_repository.side_effect = Exception("Model loading failed")

        test_args = ['program', '--repo', 'owner/test_repo', '--pr', '123']
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit):
                main()

    def test_main_with_no_args(self):
        test_args = ['program']
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit):
                main()

