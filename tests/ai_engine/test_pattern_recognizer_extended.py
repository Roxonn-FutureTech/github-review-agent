import unittest
import ast
from unittest.mock import patch, MagicMock
import numpy as np
import torch
from src.ai_engine.pattern_recognizer import PatternRecognizer
from src.ai_engine.exceptions import PatternAnalysisError

class TestPatternRecognizerExtended(unittest.TestCase):
    def setUp(self):
        # Create a recognizer with a mocked embedding model
        with patch('src.ai_engine.pattern_recognizer.AutoModel') as mock_model:
            with patch('src.ai_engine.pattern_recognizer.AutoTokenizer') as mock_tokenizer:
                self.recognizer = PatternRecognizer()
                self.recognizer.embedding_model = MagicMock()
                self.recognizer.tokenizer = MagicMock()

    def test_initialize_embedding_model(self):
        """Test the _initialize_embedding_model method."""
        with patch('src.ai_engine.pattern_recognizer.AutoModel') as mock_model:
            with patch('src.ai_engine.pattern_recognizer.AutoTokenizer') as mock_tokenizer:
                # Create a new recognizer to test initialization
                recognizer = PatternRecognizer()

                # Verify the model was initialized
                mock_model.from_pretrained.assert_called_once()
                mock_tokenizer.from_pretrained.assert_called_once()

    def test_get_embeddings(self):
        """Test the _get_embeddings method."""
        # Mock the tokenizer and model
        self.recognizer.tokenizer.return_value = {"input_ids": torch.tensor([[1, 2, 3]]), "attention_mask": torch.tensor([[1, 1, 1]])}

        # Mock the model output
        mock_output = MagicMock()
        mock_output.last_hidden_state = torch.tensor([[[0.1, 0.2, 0.3]]])
        self.recognizer.embedding_model.return_value = mock_output

        # Test with a single code block
        code_blocks = ["def test(): pass"]
        embeddings = self.recognizer._get_embeddings(code_blocks)

        # Verify the result
        self.assertIsInstance(embeddings, np.ndarray)
        self.assertEqual(embeddings.shape[0], 1)  # One embedding for one code block

    def test_get_embeddings_error(self):
        """Test error handling in _get_embeddings method."""
        # Mock the tokenizer to raise an exception
        self.recognizer.tokenizer.side_effect = Exception("Test error")

        # Test with a single code block
        code_blocks = ["def test(): pass"]

        with self.assertRaises(PatternAnalysisError):
            self.recognizer._get_embeddings(code_blocks)

    def test_cluster_patterns(self):
        """Test the _cluster_patterns method."""
        # Create sample embeddings
        embeddings = np.array([
            [0.1, 0.2, 0.3],
            [0.11, 0.21, 0.31],  # Close to the first one
            [0.9, 0.8, 0.7]      # Far from the others
        ])

        # Cluster the embeddings
        clusters = self.recognizer._cluster_patterns(embeddings)

        # Verify the result
        self.assertEqual(len(clusters), 3)  # One cluster label per embedding

        # The first two should be in the same cluster, the third in a different one
        self.assertEqual(clusters[0], clusters[1])
        self.assertNotEqual(clusters[0], clusters[2])

    def test_cluster_patterns_error(self):
        """Test error handling in _cluster_patterns method."""
        with patch('src.ai_engine.pattern_recognizer.DBSCAN') as mock_dbscan:
            mock_dbscan.side_effect = Exception("Test error")

            with self.assertRaises(PatternAnalysisError):
                self.recognizer._cluster_patterns(np.array([[0.1, 0.2, 0.3]]))

    def test_analyze(self):
        """Test the analyze method."""
        # Create sample AST trees
        ast_trees = {
            "file1.py": {
                "ast": ast.parse("""
class TestClass:
    def method1(self):
        pass

    def method2(self):
        pass

def standalone_function():
    pass
""")
            }
        }

        # Analyze the AST trees
        patterns = self.recognizer.analyze(ast_trees)

        # Verify the result
        self.assertEqual(len(patterns), 6)  # 1 class + 2 methods + 1 function + 2 extras

        # Check for class pattern
        class_patterns = [p for p in patterns if p['type'] == 'class_definition']
        self.assertEqual(len(class_patterns), 1)
        self.assertEqual(class_patterns[0]['name'], 'TestClass')

        # Check for method patterns
        method_patterns = [p for p in patterns if p['type'] == 'method_definition']
        self.assertEqual(len(method_patterns), 2)

        # Check for function pattern
        function_patterns = [p for p in patterns if p['type'] == 'function_definition']
        self.assertEqual(len(function_patterns), 1)
        self.assertEqual(function_patterns[0]['name'], 'standalone_function')

    def test_analyze_clusters(self):
        """Test the _analyze_clusters method."""
        # Create sample clusters and code blocks
        clusters = np.array([0, 0, 1, -1])  # Two in cluster 0, one in cluster 1, one noise
        code_blocks = [
            "def func1(): pass",
            "def func2(): pass",
            "class TestClass: pass",
            "# This is a comment"
        ]

        # Analyze the clusters
        patterns = self.recognizer._analyze_clusters(clusters, code_blocks)

        # Verify the result
        self.assertEqual(len(patterns), 2)  # Two clusters (excluding noise)

        # Check cluster 0 (function definitions)
        cluster0 = next(p for p in patterns if p['cluster_id'] == 0)
        self.assertEqual(cluster0['frequency'], 2)
        self.assertEqual(len(cluster0['examples']), 2)
        self.assertEqual(cluster0['pattern_type'], 'function_definition')

        # Check cluster 1 (class definition)
        cluster1 = next(p for p in patterns if p['cluster_id'] == 1)
        self.assertEqual(cluster1['frequency'], 1)
        self.assertEqual(len(cluster1['examples']), 1)
        self.assertEqual(cluster1['pattern_type'], 'class_definition')

    def test_identify_pattern_type(self):
        """Test the _identify_pattern_type method."""
        # Test function pattern
        function_code = ["def func1(): pass", "def func2(): return 42"]
        self.assertEqual(self.recognizer._identify_pattern_type(function_code), 'function_definition')

        # Test class pattern
        class_code = ["class TestClass: pass", "class AnotherClass:\n    def method(self): pass"]
        self.assertEqual(self.recognizer._identify_pattern_type(class_code), 'class_definition')

        # Test import pattern
        import_code = ["import os", "from datetime import datetime"]
        self.assertEqual(self.recognizer._identify_pattern_type(import_code), 'import_pattern')

        # Test error handling pattern
        error_code = ["try:\n    func()\nexcept Exception as e:\n    print(e)"]
        self.assertEqual(self.recognizer._identify_pattern_type(error_code), 'error_handling')

        # Test loop pattern
        loop_code = ["for i in range(10):\n    print(i)", "while True:\n    break"]
        self.assertEqual(self.recognizer._identify_pattern_type(loop_code), 'loop_pattern')

        # Test general pattern (no specific keywords)
        general_code = ["x = 1 + 2", "result = x * y"]
        self.assertEqual(self.recognizer._identify_pattern_type(general_code), 'general_code_pattern')

    def test_analyze_class_patterns(self):
        """Test the analyze_class_patterns method."""
        # Create a sample AST tree with classes
        test_content = """
class SmallClass:
    def method(self):
        pass

class LargeClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass

class InheritedClass(BaseClass):
    def method(self):
        pass
"""
        tree = ast.parse(test_content)

        # Analyze class patterns
        patterns = self.recognizer.analyze_class_patterns(tree)

        # Verify the result
        self.assertIn('class_patterns', patterns)
        self.assertEqual(len(patterns['class_patterns']), 2)  # Large class and inheritance patterns

        # Check for large class pattern
        large_class = next(p for p in patterns['class_patterns'] if p['type'] == 'large_class')
        self.assertEqual(large_class['class_name'], 'LargeClass')
        self.assertEqual(large_class['method_count'], 11)

        # Check for inheritance pattern
        inheritance = next(p for p in patterns['class_patterns'] if p['type'] == 'inheritance')
        self.assertEqual(inheritance['class_name'], 'InheritedClass')
        self.assertEqual(inheritance['base_classes'], ['BaseClass'])

    def test_pattern_matching(self):
        """Test the pattern_matching method."""
        # Test singleton pattern
        singleton_code = """
class Singleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
"""
        self.assertTrue(self.recognizer.pattern_matching(singleton_code, 'singleton'))

        # Test factory pattern
        factory_code = """
class Factory:
    @classmethod
    def create(cls, type):
        if type == 'A':
            return ProductA()
        return ProductB()
"""
        self.assertTrue(self.recognizer.pattern_matching(factory_code, 'factory'))

        # Test non-matching pattern
        regular_code = """
class Regular:
    def method(self):
        pass
"""
        self.assertFalse(self.recognizer.pattern_matching(regular_code, 'singleton'))
        self.assertFalse(self.recognizer.pattern_matching(regular_code, 'factory'))

    def test_analyze_code_patterns_method(self):
        """Test the analyze_code_patterns method."""
        # Create sample code
        test_code = """
class TestClass:
    _instance = None

    def __init__(self, value):
        self.value = value

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls(42)
        return cls._instance

def long_parameter_function(a, b, c, d, e, f):
    return a + b + c + d + e + f
"""

        # Analyze code patterns
        patterns = self.recognizer.analyze_code_patterns(test_code)

        # Verify the result
        self.assertIn('code_smells', patterns)
        self.assertIn('design_patterns', patterns)
        self.assertIn('complexity_metrics', patterns)

        # Check for singleton pattern
        self.assertIn('singleton', patterns['design_patterns'])

        # Check for long parameter list smell
        self.assertIn('long_parameter_list:long_parameter_function', patterns['code_smells'])

        # Check complexity metrics
        self.assertGreater(patterns['complexity_metrics']['cyclomatic_complexity'], 0)

    def test_analyze_code_patterns_syntax_error(self):
        """Test error handling in analyze_code_patterns method."""
        # Create code with syntax error
        test_code = """
def function(
    return 42
"""

        # Analyze code patterns
        patterns = self.recognizer.analyze_code_patterns(test_code)

        # Verify the result
        self.assertIn('error', patterns)

    def test_calculate_complexity_metrics(self):
        """Test the calculate_complexity_metrics method."""
        # Create sample code with nested structures
        test_code = """
def complex_function(x):
    result = 0
    for i in range(10):
        if i % 2 == 0:
            for j in range(5):
                if j > 2:
                    result += i * j
                    try:
                        result /= (j - 2)
                    except ZeroDivisionError:
                        result += 1
    return result
"""
        tree = ast.parse(test_code)

        # Calculate complexity metrics
        metrics = self.recognizer.calculate_complexity_metrics(tree)

        # Verify the result
        self.assertIn('cyclomatic_complexity', metrics)
        self.assertIn('cognitive_complexity', metrics)
        self.assertIn('max_nesting_depth', metrics)

        # Check values
        self.assertGreater(metrics['cyclomatic_complexity'], 3)  # At least 4 decision points
        self.assertGreater(metrics['max_nesting_depth'], 3)  # At least 4 levels of nesting

if __name__ == '__main__':
    unittest.main()
