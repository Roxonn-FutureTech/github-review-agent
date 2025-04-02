import unittest
from unittest.mock import Mock, patch
import os
import ast
import shutil
from src.ai_engine.code_analyzer import CodeAnalyzer
from src.ai_engine.exceptions import CodeParsingError

class TestCodeAnalyzer(unittest.TestCase):
    def setUp(self):
        # Mock the transformer models to avoid loading them during tests
        with patch('transformers.AutoTokenizer.from_pretrained'), \
             patch('transformers.AutoModel.from_pretrained'):
            self.analyzer = CodeAnalyzer()
        
        # Create test directory structure
        self.test_dir = "test_repo"
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create sample files
        self.sample_files = {
            'main.py': 'def main():\n    print("Hello")\n',
            'utils.py': 'import os\n\ndef helper():\n    pass\n'
        }
        
        for filename, content in self.sample_files.items():
            with open(os.path.join(self.test_dir, filename), 'w') as f:
                f.write(content)

    def tearDown(self):
        # Clean up test files and directory
        try:
            shutil.rmtree(self.test_dir)
        except OSError:
            pass

    def test_collect_files(self):
        files = self.analyzer._collect_files(self.test_dir)
        self.assertEqual(len(files), 2)
        self.assertTrue(any(f.endswith('main.py') for f in files))
        self.assertTrue(any(f.endswith('utils.py') for f in files))

    def test_parse_files(self):
        self.analyzer.files = [
            os.path.join(self.test_dir, 'main.py'),
            os.path.join(self.test_dir, 'utils.py')
        ]
        ast_trees = self.analyzer._parse_files()
        
        self.assertEqual(len(ast_trees), 2)
        for file_path, tree_data in ast_trees.items():
            self.assertIsInstance(tree_data['ast'], ast.AST)
            self.assertIsInstance(tree_data['content'], str)

    def test_analyze_dependencies(self):
        # Mock AST trees
        self.analyzer.ast_trees = {
            'utils.py': {
                'ast': ast.parse('import os\nimport sys'),
                'content': 'import os\nimport sys'
            }
        }
        
        deps = self.analyzer._analyze_dependencies()
        self.assertIn('utils.py', deps)
        self.assertTrue(len(deps['utils.py']['imports']) > 0)

    def test_build_knowledge_representation(self):
        # Setup test data
        self.analyzer.files = [
            os.path.join(self.test_dir, 'main.py'),
            os.path.join(self.test_dir, 'utils.py')
        ]
        
        # Mock the pattern recognizer to return dummy patterns
        mock_patterns = [
            {'type': 'function', 'content': 'def main(): pass'},
            {'type': 'import', 'content': 'import os'}
        ]
        self.analyzer.pattern_recognizer.analyze = Mock(return_value=mock_patterns)
        
        # Add ast_trees setup
        self.analyzer.ast_trees = {
            'main.py': {
                'ast': ast.parse('def main(): pass'),
                'content': 'def main(): pass'
            },
            'utils.py': {
                'ast': ast.parse('import os'),
                'content': 'import os'
            }
        }
        self.analyzer.dependencies = {
            'main.py': {'imports': []},
            'utils.py': {'imports': [{'module': 'os'}]}
        }
        
        knowledge = self.analyzer._build_knowledge_representation()
        
        # Verify the structure and content of the knowledge base
        self.assertIn('files', knowledge)
        self.assertIn('dependencies', knowledge)
        self.assertIn('patterns', knowledge)
        self.assertIn('graph', knowledge)
        self.assertEqual(knowledge['patterns'], mock_patterns)
        self.assertEqual(len(knowledge['files']), 2)
        self.assertEqual(len(knowledge['dependencies']), 2)

    def test_scan_repository_error_handling(self):
        """Test error handling in scan_repository method"""
        with self.assertRaises(CodeParsingError):
            self.analyzer.scan_repository("non_existent_path")

    def test_parse_files_with_invalid_syntax(self):
        """Test handling of invalid Python syntax"""
        with open(os.path.join(self.test_dir, 'invalid.py'), 'w') as f:
            f.write("def invalid_syntax(:")  # Invalid syntax
        
        self.analyzer.files = [os.path.join(self.test_dir, 'invalid.py')]
        with self.assertRaises(CodeParsingError):
            self.analyzer._parse_files()

    def test_analyze_dependencies_with_complex_imports(self):
        """Test dependency analysis with various import types"""
        self.analyzer.ast_trees = {
            'complex.py': {
                'ast': ast.parse(
                    'import os, sys\n'
                    'from datetime import datetime as dt\n'
                    'from .local_module import func\n'
                    'from ..parent_module import Class\n'
                ),
                'content': ''
            }
        }
        
        deps = self.analyzer._analyze_dependencies()
        self.assertIn('complex.py', deps)
        imports = deps['complex.py']['imports']
        self.assertTrue(any(imp['module'] == 'os' for imp in imports))
        self.assertTrue(any(imp['module'] == 'sys' for imp in imports))
        self.assertTrue(any(imp['module'] == 'datetime' for imp in imports))
        self.assertTrue(any(imp['module'] == 'local_module' for imp in imports))
        self.assertTrue(any(imp['module'] == 'parent_module' for imp in imports))

