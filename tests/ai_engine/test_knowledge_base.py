import unittest
import os
import json
import sqlite3
from unittest.mock import patch, MagicMock
from src.ai_engine.knowledge_base import KnowledgeBase
from src.ai_engine.exceptions import KnowledgeBaseError

class TestKnowledgeBase(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_knowledge.db"
        self.kb = KnowledgeBase(self.test_db)

    def tearDown(self):
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except PermissionError:
                pass  # Handle Windows file lock issues

    def test_initialize_db(self):
        self.assertTrue(os.path.exists(self.test_db))
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='patterns'")
            self.assertIsNotNone(cursor.fetchone())

    def test_store_pattern(self):
        pattern_type = "function_definition"
        pattern_data = {'name': 'test_func', 'params': []}

        # Clear any existing patterns
        self.kb.clear()

        result = self.kb.store_pattern(pattern_type, pattern_data)
        self.assertTrue(result)

        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT pattern_type, pattern_data FROM patterns")
            row = cursor.fetchone()
            self.assertEqual(row[0], pattern_type)
            self.assertEqual(json.loads(row[1]), pattern_data)

    def test_store_pattern_error(self):
        with self.assertRaises(KnowledgeBaseError):
            self.kb.store_pattern(None, None)

    def test_store_and_retrieve_patterns(self):
        # Clear any existing patterns
        self.kb.clear()

        patterns = [
            {'type': 'class', 'data': {'name': 'TestClass', 'file': 'test.py'}},
            {'type': 'function', 'data': {'name': 'test_func', 'file': 'test.py'}}
        ]

        self.kb.store_patterns(patterns)
        retrieved = self.kb.get_patterns('test.py')
        self.assertEqual(len(retrieved), 2)

    def test_knowledge_graph_operations(self):
        # Clear the graph
        self.kb.graph.clear()

        nodes = [
            ('file1.py', {'type': 'file'}),
            ('file2.py', {'type': 'file'}),
            ('ClassA', {'type': 'class'})
        ]
        edges = [
            ('file1.py', 'ClassA', {'type': 'contains'}),
            ('file2.py', 'file1.py', {'type': 'imports'})
        ]

        self.kb.build_graph(nodes, edges)
        self.assertTrue(self.kb.has_dependency('file2.py', 'file1.py'))

        # file1.py is related to both ClassA and file2.py
        related = self.kb.get_related_components('file1.py')
        self.assertEqual(len(related), 2)
        self.assertIn('ClassA', related)
        self.assertIn('file2.py', related)

    def test_graph_operations_error(self):
        with patch('src.ai_engine.knowledge_base.nx.DiGraph.add_nodes_from') as mock_add_nodes:
            mock_add_nodes.side_effect = Exception("Test error")
            with self.assertRaises(KnowledgeBaseError):
                self.kb.build_graph([('test', {})], [])

    def test_update_pattern_frequency(self):
        # Clear any existing patterns
        self.kb.clear()

        # Store initial pattern
        pattern_type = 'test_pattern'
        pattern_data = {'test': 'data'}
        self.kb.store_pattern(pattern_type, pattern_data)

        # Update frequency
        self.kb.update_pattern_frequency(pattern_type, 5)

        # Verify update
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT frequency FROM patterns WHERE pattern_type = ?",
                          (pattern_type,))
            frequency = cursor.fetchone()[0]
            self.assertEqual(frequency, 5)

    def test_delete_pattern(self):
        # Clear any existing patterns
        self.kb.clear()

        # Store pattern
        pattern_type = 'test_pattern'
        pattern_data = {'test': 'data'}
        self.kb.store_pattern(pattern_type, pattern_data)

        # Delete pattern
        self.kb.delete_pattern(pattern_type)

        # Verify deletion
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patterns WHERE pattern_type = ?",
                          (pattern_type,))
            self.assertIsNone(cursor.fetchone())

    def test_clear_knowledge_base(self):
        # Store some patterns
        self.kb.store_pattern('pattern1', {'test': 'data1'})
        self.kb.store_pattern('pattern2', {'test': 'data2'})

        # Clear knowledge base
        self.kb.clear()

        # Verify all patterns are removed
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM patterns")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 0)
