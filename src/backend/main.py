import argparse
import sys
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import warnings
import logging
import json
import requests
from pprint import pprint
warnings.filterwarnings("ignore", category=UserWarning, module="torch._utils")

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.ai_engine.code_analyzer import CodeAnalyzer
from src.ai_engine.logging_config import get_logger

logger = get_logger(__name__)

def fetch_pr_details(repo: str, pr_number: int, github_token: str = None):
    """Fetch PR details from GitHub API"""
    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    base_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    response = requests.get(base_url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch PR details: {response.json().get('message', 'Unknown error')}")
    
    pr_data = response.json()
    return {
        'title': pr_data['title'],
        'description': pr_data['body'],
        'changed_files': pr_data['changed_files'],
        'additions': pr_data['additions'],
        'deletions': pr_data['deletions'],
        'files': [f['filename'] for f in requests.get(f"{base_url}/files", headers=headers).json()]
    }

def format_pr_results(pr_details):
    """Format PR analysis results"""
    return {
        "Pull Request Summary": {
            "Title": pr_details['title'],
            "Description": pr_details['description'],
            "Statistics": {
                "Changed Files": pr_details['changed_files'],
                "Additions": pr_details['additions'],
                "Deletions": pr_details['deletions']
            },
            "Modified Files": pr_details['files']
        }
    }

def main():
    parser = argparse.ArgumentParser(description='GitHub Review Agent')
    parser.add_argument('--repo', type=str, required=True, help='Repository in format owner/repo')
    parser.add_argument('--pr', type=int, required=True, help='Pull Request number')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--output', choices=['text', 'json'], default='text', help='Output format')
    parser.add_argument('--token', type=str, help='GitHub token for authentication')
    
    args = parser.parse_args()
    print(f"\n🔍 Analyzing PR #{args.pr} in repository {args.repo}...")
    
    try:
        # Fetch PR details from GitHub
        pr_details = fetch_pr_details(args.repo, args.pr, args.token)
        summary = format_pr_results(pr_details)
        
        if args.output == 'json':
            print(json.dumps(summary, indent=2))
        else:
            print("\n📊 Pull Request Analysis:")
            print(f"Title: {summary['Pull Request Summary']['Title']}")
            print(f"Description: {summary['Pull Request Summary']['Description'][:200]}...")
            
            print("\n📝 Statistics:")
            stats = summary['Pull Request Summary']['Statistics']
            for key, value in stats.items():
                print(f"  • {key}: {value}")
            
            print("\n📂 Modified Files:")
            for file in summary['Pull Request Summary']['Modified Files']:
                print(f"  - {file}")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
