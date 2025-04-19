import unittest
import ast
import os
import sys
from unittest.mock import patch, mock_open, MagicMock
from src.ai_engine.code_analyzer import CodeAnalyzer
from src.ai_engine.exceptions import PatternAnalysisError

class TestCodeAnalyzerExtended(unittest.TestCase):
    def setUp(self):
        self.analyzer = CodeAnalyzer()
        self.test_repo_path = "test_repo"
        
    def test_analyze_pr(self):
        """Test the analyze_pr method with a mock PR."""
        pr_details = {
            'changed_files': 3,
            'additions': 100,
            'deletions': 50,
            'files': [
                {'filename': 'test.py', 'status': 'modified'},
                {'filename': 'core/auth.py', 'status': 'modified'},
                {'filename': 'tests/test_file.py', 'status': 'added'}
            ]
        }
        
        # Mock the internal methods
        with patch.object(self.analyzer, '_analyze_pr_summary') as mock_summary:
            with patch.object(self.analyzer, '_analyze_code_quality') as mock_quality:
                with patch.object(self.analyzer, '_analyze_impact') as mock_impact:
                    
                    mock_summary.return_value = {'files_changed': 3}
                    mock_quality.return_value = {'code_smells': ['large_class']}
                    mock_impact.return_value = {'high_risk_changes': [{'file': 'core/auth.py'}]}
                    
                    result = self.analyzer.analyze_pr(pr_details)
                    
                    # Verify the result structure
                    self.assertIn('summary', result)
                    self.assertIn('code_quality', result)
                    self.assertIn('impact_analysis', result)
                    self.assertIn('recommendations', result)
                    
                    # Verify recommendations were generated
                    self.assertEqual(len(result['recommendations']), 2)
                    self.assertEqual(result['recommendations'][0]['type'], 'code_quality')
                    self.assertEqual(result['recommendations'][1]['type'], 'risk')
    
    def test_analyze_pr_error(self):
        """Test error handling in analyze_pr method."""
        pr_details = {'changed_files': 3, 'additions': 100, 'deletions': 50, 'files': []}
        
        with patch.object(self.analyzer, '_analyze_pr_summary') as mock_summary:
            mock_summary.side_effect = Exception("Test error")
            
            with self.assertRaises(Exception):
                self.analyzer.analyze_pr(pr_details)
    
    def test_analyze_pr_summary(self):
        """Test the _analyze_pr_summary method."""
        pr_details = {
            'changed_files': 3,
            'additions': 100,
            'deletions': 50
        }
        
        summary = self.analyzer._analyze_pr_summary(pr_details)
        
        self.assertEqual(summary['files_changed'], 3)
        self.assertEqual(summary['additions'], 100)
        self.assertEqual(summary['deletions'], 50)
        self.assertEqual(summary['net_changes'], 50)  # 100 - 50
    
    def test_analyze_code_quality(self):
        """Test the _analyze_code_quality method."""
        files = [
            {'filename': 'test.py', 'status': 'modified'}
        ]
        
        test_content = """
class LargeClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
"""
        
        with patch('builtins.open', mock_open(read_data=test_content)):
            quality = self.analyzer._analyze_code_quality(files)
            
            self.assertIn('code_smells', quality)
            self.assertIn('complexity_scores', quality)
            self.assertIn('pattern_violations', quality)
            self.assertIn('test.py', quality['complexity_scores'])
    
    def test_analyze_impact(self):
        """Test the _analyze_impact method."""
        pr_details = {
            'files': [
                {'filename': 'core/auth.py', 'status': 'modified'},
                {'filename': 'tests/test_auth.py', 'status': 'added'}
            ]
        }
        
        impact = self.analyzer._analyze_impact(pr_details)
        
        self.assertIn('high_risk_changes', impact)
        self.assertIn('affected_components', impact)
        self.assertIn('test_coverage', impact)
        
        # Verify high risk changes detection
        self.assertEqual(len(impact['high_risk_changes']), 1)
        self.assertEqual(impact['high_risk_changes'][0]['file'], 'core/auth.py')
        
        # Verify affected components
        self.assertIn('core', impact['affected_components'])
        self.assertIn('tests', impact['affected_components'])
        
        # Verify test coverage
        self.assertEqual(impact['test_coverage']['files_with_tests'], 1)
        self.assertEqual(impact['test_coverage']['total_files'], 2)
    
    def test_identify_high_risk_changes(self):
        """Test the _identify_high_risk_changes method."""
        files = [
            {'filename': 'core/auth.py', 'status': 'modified'},
            {'filename': 'utils/helper.py', 'status': 'modified'},
            {'filename': 'security/encryption.py', 'status': 'added'}
        ]
        
        high_risk = self.analyzer._identify_high_risk_changes(files)
        
        self.assertEqual(len(high_risk), 2)
        self.assertEqual(high_risk[0]['file'], 'core/auth.py')
        self.assertEqual(high_risk[1]['file'], 'security/encryption.py')
    
    def test_identify_affected_components(self):
        """Test the _identify_affected_components method."""
        files = [
            {'filename': 'core/auth.py', 'status': 'modified'},
            {'filename': 'core/user.py', 'status': 'modified'},
            {'filename': 'utils/helper.py', 'status': 'added'}
        ]
        
        components = self.analyzer._identify_affected_components(files)
        
        self.assertEqual(len(components), 2)
        self.assertIn('core', components)
        self.assertIn('utils', components)
    
    def test_analyze_test_coverage(self):
        """Test the _analyze_test_coverage method."""
        files = [
            {'filename': 'core/auth.py', 'status': 'modified'},
            {'filename': 'tests/test_auth.py', 'status': 'added'},
            {'filename': 'tests/test_user.py', 'status': 'modified'}
        ]
        
        coverage = self.analyzer._analyze_test_coverage(files)
        
        self.assertEqual(coverage['files_with_tests'], 2)
        self.assertEqual(coverage['total_files'], 3)
    
    def test_calculate_overall_metrics(self):
        """Test the _calculate_overall_metrics method."""
        # Setup test files and AST trees
        self.analyzer.files = ['file1.py', 'file2.py']
        
        # Mock open to return file content
        test_content = """
def function():
    if True:
        pass
    else:
        pass
"""
        with patch('builtins.open', mock_open(read_data=test_content)):
            # Parse the test content into AST trees
            self.analyzer.ast_trees = {
                'file1.py': ast.parse(test_content),
                'file2.py': ast.parse(test_content)
            }
            
            metrics = self.analyzer._calculate_overall_metrics()
            
            self.assertEqual(metrics['total_files'], 2)
            self.assertIn('total_lines', metrics)
            self.assertIn('average_complexity', metrics)
    
    def test_extract_patterns(self):
        """Test the _extract_patterns method."""
        test_content = """
class TestClass:
    def method1(self, arg1, arg2):
        pass
    
    def method2(self):
        pass

def standalone_function(arg1, arg2, arg3):
    pass
"""
        tree = ast.parse(test_content)
        
        patterns = self.analyzer._extract_patterns(tree)
        
        self.assertIn('class_patterns', patterns)
        self.assertIn('function_patterns', patterns)
        
        # Verify class pattern
        self.assertEqual(len(patterns['class_patterns']), 1)
        self.assertEqual(patterns['class_patterns'][0]['name'], 'TestClass')
        self.assertEqual(patterns['class_patterns'][0]['methods'], 2)
        
        # Verify function patterns
        self.assertEqual(len(patterns['function_patterns']), 3)  # 2 methods + 1 standalone function
        
        # Find the standalone function
        standalone = next(f for f in patterns['function_patterns'] if f['name'] == 'standalone_function')
        self.assertEqual(standalone['args'], 3)
    
    def test_scan_repository_with_test_repo(self):
        """Test scan_repository with a test repository."""
        # Create a temporary test repo
        if not os.path.exists(self.test_repo_path):
            os.makedirs(self.test_repo_path, exist_ok=True)
        
        test_file_path = os.path.join(self.test_repo_path, "file1.py")
        with open(test_file_path, "w") as f:
            f.write("# Test file")
        
        try:
            # Run the scan
            result = self.analyzer.scan_repository(self.test_repo_path)
            
            # Verify the result
            self.assertIn('files', result)
            self.assertIn('dependencies', result)
            self.assertIn('patterns', result)
            self.assertIn('metrics', result)
            self.assertIn('classes', result)
            self.assertIn('functions', result)
        finally:
            # Clean up
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
            if os.path.exists(self.test_repo_path):
                os.rmdir(self.test_repo_path)
    
    def test_get_file_statistics_extended(self):
        """Test get_file_statistics with more complex code."""
        test_content = """
import os
import sys
from datetime import datetime

class TestClass:
    \"\"\"Test class docstring.\"\"\"
    
    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2
    
    def method1(self):
        \"\"\"Method docstring.\"\"\"
        if self.arg1 > 0:
            return self.arg1
        else:
            return 0

def standalone_function(arg1, arg2, arg3):
    \"\"\"Function docstring.\"\"\"
    result = 0
    for i in range(arg1):
        if i % 2 == 0:
            result += i
    return result
"""
        with patch('builtins.open', mock_open(read_data=test_content)):
            stats = self.analyzer.get_file_statistics("test.py")
            
            self.assertEqual(stats["num_classes"], 1)
            self.assertEqual(stats["num_functions"], 3)  # __init__, method1, standalone_function
            self.assertEqual(stats["num_imports"], 3)
            self.assertGreater(stats["complexity"]["cyclomatic"], 2)
            self.assertGreater(stats["complexity"]["cognitive_complexity"], 0)
            self.assertEqual(stats["complexity"]["maintainability"], 100)  # No functions with > 5 args

if __name__ == '__main__':
    unittest.main()
