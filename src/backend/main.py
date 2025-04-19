import sys
import argparse
import sys
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import warnings
import logging
import json
import requests
import traceback
from typing import Dict, Any
from src.ai_engine.code_analyzer import CodeAnalyzer
from .exceptions import GitHubAuthError

def fetch_pr_details(repo: str, pr_number: int, token: str = None) -> Dict[str, Any]:
    """Fetch pull request details from GitHub API."""
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'
    
    base_url = 'https://api.github.com'
    pr_url = f'{base_url}/repos/{repo}/pulls/{pr_number}'
    files_url = f'{pr_url}/files'
    
    try:
        pr_response = requests.get(pr_url, headers=headers)
        pr_response.raise_for_status()
        
        files_response = requests.get(files_url, headers=headers)
        files_response.raise_for_status()
        
        pr_data = pr_response.json()
        pr_data['files'] = files_response.json()
        
        return pr_data
        
    except requests.exceptions.RequestException as e:
        raise GitHubAuthError(f"Failed to fetch PR details: {str(e)}")

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='GitHub Review Agent')
    parser.add_argument('--repo', required=True, help='Repository name (owner/repo)')
    parser.add_argument('--pr', type=int, required=True, help='Pull request number')
    parser.add_argument('--token', help='GitHub token')
    parser.add_argument('--output', choices=['text', 'json'], default='text', help='Output format')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        pr_details = fetch_pr_details(args.repo, args.pr, args.token)
        analyzer = CodeAnalyzer()
        analysis_result = analyzer.analyze_pr(pr_details)
        
        # Convert analysis result to JSON-serializable format
        result = {
            'status': 'success',
            'repository': args.repo,
            'pull_request': args.pr,
            'analysis': {
                'files_analyzed': len(pr_details['files']),
                'issues': analysis_result.get('issues', []),
                'metrics': analysis_result.get('metrics', {}),
                'recommendations': analysis_result.get('recommendations', [])
            }
        }

        if args.output == 'json':
            print(json.dumps(result, indent=2))
        else:
            print(f"Analysis Results for PR #{args.pr} in {args.repo}:")
            print(f"Files analyzed: {len(pr_details['files'])}")
            print(f"Issues found: {len(result['analysis']['issues'])}")
            for issue in result['analysis']['issues']:
                print(f"- {issue}")
    
    except Exception as e:
        if args.verbose:
            traceback.print_exc()
        else:
            print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
