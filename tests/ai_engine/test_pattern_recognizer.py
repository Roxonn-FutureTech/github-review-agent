import unittest
from unittest.mock import Mock, patch
import numpy as np
import torch
from src.ai_engine.pattern_recognizer import PatternRecognizer

class TestPatternRecognizer(unittest.TestCase):
    def setUp(self):
        # Create mock embedding model
        self.mock_model = Mock()
        self.mock_model.tokenizer = Mock()
        self.recognizer = PatternRecognizer(self.mock_model)

    def test_get_embeddings(self):
        # Mock tokenizer and model outputs
        self.mock_model.tokenizer.return_value = {
            'input_ids': torch.ones(1, 10),
            'attention_mask': torch.ones(1, 10)
        }
        
        mock_output = Mock()
        mock_output.last_hidden_state = torch.ones(1, 1, 768)
        self.mock_model.return_value = mock_output

        code_blocks = [
            "def test():\n    pass",
            "class Sample:\n    pass"
        ]
        
        embeddings = self.recognizer._get_embeddings(code_blocks)
        self.assertEqual(embeddings.shape[0], 2)  # Two code blocks
        self.assertEqual(embeddings.shape[1], 768)  # Embedding dimension

    def test_identify_pattern_type(self):
        test_cases = [
            {
                'code': ['class TestClass:\n    pass'],
                'expected': 'class_definition'
            },
            {
                'code': ['def test_func():\n    pass'],
                'expected': 'function_definition'
            },
            {
                'code': ['import os\nimport sys'],
                'expected': 'import_pattern'
            },
            {
                'code': ['try:\n    pass\nexcept:\n    pass'],
                'expected': 'error_handling'
            },
            {
                'code': ['for i in range(10):\n    pass'],
                'expected': 'loop_pattern'
            }
        ]

        for case in test_cases:
            pattern_type = self.recognizer._identify_pattern_type(case['code'])
            self.assertEqual(pattern_type, case['expected'])

    def test_analyze_clusters(self):
        code_blocks = [
            "def test1(): pass",
            "def test2(): pass",
            "class Sample: pass"
        ]
        clusters = np.array([0, 0, 1])  # Two clusters

        patterns = self.recognizer._analyze_clusters(clusters, code_blocks)
        
        self.assertEqual(len(patterns), 2)  # Two clusters
        self.assertTrue(any(p['cluster_id'] == 0 for p in patterns))
        self.assertTrue(any(p['cluster_id'] == 1 for p in patterns))