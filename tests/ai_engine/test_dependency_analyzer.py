import unittest
import ast
import networkx as nx
from src.ai_engine.dependency_analyzer import DependencyAnalyzer

class TestDependencyAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = DependencyAnalyzer()

    def test_process_import(self):
        # Test regular import
        import_node = ast.parse('import os').body[0]
        result = self.analyzer._process_import(import_node)
        self.assertEqual(result['type'], 'import')
        self.assertEqual(result['module'], 'os')
        self.assertIsNone(result['alias'])

        # Test import with alias
        import_node = ast.parse('import os as operating_system').body[0]
        result = self.analyzer._process_import(import_node)
        self.assertEqual(result['module'], 'os')
        self.assertEqual(result['alias'], 'operating_system')

        # Test from import
        import_node = ast.parse('from os import path').body[0]
        result = self.analyzer._process_import(import_node)
        self.assertEqual(result['type'], 'importfrom')
        self.assertEqual(result['module'], 'os')
        self.assertEqual(result['name'], 'path')

    def test_build_dependency_graph(self):
        imports_data = [
            {
                'file': 'main.py',
                'imports': [
                    {
                        'type': 'import',
                        'module': 'os'
                    },
                    {
                        'type': 'importfrom',
                        'module': 'utils',
                        'name': 'helper'
                    }
                ]
            },
            {
                'file': 'utils.py',
                'imports': [
                    {
                        'type': 'import',
                        'module': 'sys'
                    }
                ]
            }
        ]

        graph = self.analyzer.build_dependency_graph(imports_data)

        self.assertIsInstance(graph, nx.DiGraph)
        # Verify the exact nodes we expect to see, including the 'utils' module
        expected_nodes = {'main.py', 'utils.py', 'os', 'sys', 'helper', 'utils'}
        self.assertEqual(set(graph.nodes), expected_nodes)

