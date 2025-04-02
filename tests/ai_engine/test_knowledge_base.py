import unittest
import os
import json
from src.ai_engine.knowledge_base import KnowledgeBase

class TestKnowledgeBase(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_knowledge.db"
        self.kb = KnowledgeBase(self.test_db)

    def tearDown(self):
        self.kb.conn.close()
        os.remove(self.test_db)

    def test_initialize_db(self):
        # Verify tables exist
        cursor = self.kb.conn.cursor()
        
        # Check code_patterns table
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='code_patterns'
        """)
        self.assertIsNotNone(cursor.fetchone())
        
        # Check dependencies table
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='dependencies'
        """)
        self.assertIsNotNone(cursor.fetchone())

    def test_store_pattern(self):
        test_pattern = {
            'pattern_type': 'function_definition',
            'data': {'name': 'test_func', 'params': []},
            'frequency': 1
        }
        
        self.kb.store_pattern(test_pattern)
        
        # Verify pattern was stored
        cursor = self.kb.conn.cursor()
        cursor.execute("SELECT * FROM code_patterns")
        row = cursor.fetchone()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[1], 'function_definition')
        self.assertEqual(
            json.loads(row[2]), 
            {'name': 'test_func', 'params': []}
        )

    def test_query_knowledge(self):
        # Store test patterns
        patterns = [
            {
                'pattern_type': 'class_definition',
                'data': {'name': 'TestClass'},
                'frequency': 2
            },
            {
                'pattern_type': 'function_definition',
                'data': {'name': 'test_func'},
                'frequency': 3
            }
        ]
        
        for pattern in patterns:
            self.kb.store_pattern(pattern)

        # Test querying specific pattern type
        results = self.kb.query_knowledge({'pattern_type': 'class_definition'})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['pattern_type'], 'class_definition')

        # Test querying all patterns
        results = self.kb.query_knowledge({})
        self.assertEqual(len(results), 2)

        # Test limit
        results = self.kb.query_knowledge({'limit': 1})
        self.assertEqual(len(results), 1)

    def test_store_and_retrieve_patterns(self):
        """Test storing and retrieving code patterns"""
        patterns = [
            {'type': 'class', 'name': 'TestClass', 'file': 'test.py'},
            {'type': 'function', 'name': 'test_func', 'file': 'test.py'}
        ]
        self.kb.store_patterns(patterns)
        
        retrieved = self.kb.get_patterns('test.py')
        self.assertEqual(len(retrieved), 2)
        self.assertEqual(retrieved[0]['type'], 'class')
        self.assertEqual(retrieved[1]['type'], 'function')

    def test_knowledge_graph_operations(self):
        """Test knowledge graph building and querying"""
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
        
        # Test graph queries
        self.assertTrue(self.kb.has_dependency('file2.py', 'file1.py'))
        self.assertEqual(len(self.kb.get_related_components('file1.py')), 2)
