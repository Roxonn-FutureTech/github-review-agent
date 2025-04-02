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