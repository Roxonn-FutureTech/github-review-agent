import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import ast
from src.ai_engine.code_analyzer import CodeAnalyzer

class TestCodeAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = CodeAnalyzer()
        self.test_repo_path = "test_repo"
        
    def test_collect_files(self):
        mock_files = [
            "test_repo/file1.py",
            "test_repo/subdir/file2.py",
            "test_repo/.git/config",  # Should be ignored
            "test_repo/file3.txt"     # Should be ignored
        ]
        
        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                ("test_repo", [], ["file1.py"]),
                ("test_repo/subdir", [], ["file2.py"]),
                ("test_repo/.git", [], ["config"]),
                ("test_repo", [], ["file3.txt"])
            ]
            
            files = self.analyzer._collect_files(self.test_repo_path)
            self.assertEqual(len(files), 2)
            self.assertIn("test_repo/file1.py", files)
            self.assertIn("test_repo/subdir/file2.py", files)

    def test_parse_files(self):
        test_content = """
def test_function():
    return "Hello"

class TestClass:
    def method(self):
        pass
"""
        mock_file_content = mock_open(read_data=test_content)
        
        with patch('builtins.open', mock_file_content):
            with patch.object(self.analyzer, 'files', ["test.py"]):
                ast_trees = self.analyzer._parse_files()
                
                self.assertEqual(len(ast_trees), 1)
                self.assertIsInstance(ast_trees["test.py"], ast.Module)
                
                # Verify AST structure
                function_def = False
                class_def = False
                for node in ast.walk(ast_trees["test.py"]):
                    if isinstance(node, ast.FunctionDef):
                        function_def = True
                    elif isinstance(node, ast.ClassDef):
                        class_def = True
                
                self.assertTrue(function_def)
                self.assertTrue(class_def)

    def test_parse_files_with_syntax_error(self):
        invalid_content = """
def invalid_function()
    return "Missing colon"
"""
        mock_file_content = mock_open(read_data=invalid_content)
        
        with patch('builtins.open', mock_file_content):
            with patch.object(self.analyzer, 'files', ["invalid.py"]):
                with self.assertLogs(level='ERROR'):
                    ast_trees = self.analyzer._parse_files()
                    self.assertEqual(len(ast_trees), 0)

    def test_analyze_dependencies(self):
        test_content = """
import os
from datetime import datetime
from .local_module import LocalClass
"""
        mock_file_content = mock_open(read_data=test_content)
        
        with patch('builtins.open', mock_file_content):
            with patch.object(self.analyzer, 'files', ["test.py"]):
                self.analyzer._parse_files()
                deps = self.analyzer._analyze_dependencies()
                
                self.assertIn("test.py", deps)
                self.assertEqual(len(deps["test.py"]), 3)
                self.assertIn("os", deps["test.py"])
                self.assertIn("datetime", deps["test.py"])
                self.assertIn(".local_module", deps["test.py"])

    def test_build_knowledge_representation(self):
        # Mock AST trees and dependencies
        self.analyzer.ast_trees = {
            "test.py": ast.parse("""
class TestClass:
    def method(self):
        pass
""")
        }
        
        self.analyzer.dependencies = {
            "test.py": ["os", "datetime"]
        }
        
        knowledge = self.analyzer._build_knowledge_representation()
        
        self.assertIn("classes", knowledge)
        self.assertIn("functions", knowledge)
        self.assertIn("dependencies", knowledge)
        self.assertEqual(len(knowledge["classes"]), 1)
        self.assertEqual(len(knowledge["functions"]), 1)
        self.assertEqual(len(knowledge["dependencies"]), 2)

    def test_scan_repository(self):
        with patch.object(self.analyzer, '_collect_files') as mock_collect:
            with patch.object(self.analyzer, '_parse_files') as mock_parse:
                with patch.object(self.analyzer, '_analyze_dependencies') as mock_deps:
                    with patch.object(self.analyzer, '_build_knowledge_representation') as mock_knowledge:
                        
                        mock_collect.return_value = ["test.py"]
                        mock_parse.return_value = {"test.py": ast.parse("")}
                        mock_deps.return_value = {"test.py": ["os"]}
                        mock_knowledge.return_value = {"test": "data"}
                        
                        result = self.analyzer.scan_repository(self.test_repo_path)
                        
                        mock_collect.assert_called_once_with(self.test_repo_path)
                        mock_parse.assert_called_once()
                        mock_deps.assert_called_once()
                        mock_knowledge.assert_called_once()
                        self.assertEqual(result, {"test": "data"})

    def test_scan_repository_nonexistent_path(self):
        with self.assertRaises(FileNotFoundError):
            self.analyzer.scan_repository("nonexistent/path")

    def test_extract_patterns(self):
        test_content = """
def test_function(arg1, arg2=None):
    '''Test function docstring'''
    return arg1 + arg2

class TestClass:
    def __init__(self):
        self.value = 0
        
    @property
    def prop(self):
        return self.value
"""
        ast_tree = ast.parse(test_content)
        patterns = self.analyzer._extract_patterns(ast_tree)
        
        self.assertIn("function_patterns", patterns)
        self.assertIn("class_patterns", patterns)
        self.assertTrue(any(p["name"] == "test_function" for p in patterns["function_patterns"]))
        self.assertTrue(any(p["name"] == "TestClass" for p in patterns["class_patterns"]))

    def test_analyze_complexity(self):
        test_content = """
def complex_function(x):
    if x > 0:
        if x < 10:
            return "Medium"
        else:
            return "High"
    else:
        return "Low"
"""
        ast_tree = ast.parse(test_content)
        complexity = self.analyzer._analyze_complexity(ast_tree)
        
        self.assertGreater(complexity["cyclomatic_complexity"], 1)
        self.assertIn("cognitive_complexity", complexity)

    def test_get_file_statistics(self):
        test_content = """
import os
import sys

def func1():
    pass

def func2():
    pass

class TestClass:
    def method1(self):
        pass
"""
        with patch('builtins.open', mock_open(read_data=test_content)):
            stats = self.analyzer.get_file_statistics("test.py")
            
            self.assertEqual(stats["num_functions"], 2)
            self.assertEqual(stats["num_classes"], 1)
            self.assertEqual(stats["num_imports"], 2)
            self.assertIn("loc", stats)
            self.assertIn("complexity", stats)

if __name__ == '__main__':
    unittest.main()
