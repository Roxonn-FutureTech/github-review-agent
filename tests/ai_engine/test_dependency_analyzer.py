import pytest
import networkx as nx
from src.ai_engine.dependency_analyzer import DependencyAnalyzer

class TestDependencyAnalyzer:
    @pytest.fixture
    def analyzer(self):
        return DependencyAnalyzer()

    @pytest.fixture
    def sample_code(self):
        return """
import os
from datetime import datetime
from .local_module import LocalClass
import sys as system
from typing import List, Optional
"""

    def test_analyze_imports(self, analyzer, sample_code):
        imports = analyzer.analyze_imports(sample_code)
        assert len(imports['standard']) == 4  # os, datetime, sys, typing
        assert len(imports['local']) == 1     # .local_module
        assert 'os' in imports['standard']
        assert '.local_module' in imports['local']

    def test_build_dependency_graph(self, analyzer):
        files = {
            'module_a.py': 'import module_b\nfrom module_c import func',
            'module_b.py': 'from module_c import Class',
            'module_c.py': 'import os'
        }
        graph = analyzer.build_dependency_graph(files)
        assert len(graph.nodes()) == 3
        assert len(graph.edges()) == 3

    def test_analyze_dependency_complexity(self, analyzer):
        # Create a test graph
        analyzer.graph.add_edges_from([
            ('a.py', 'b.py'),
            ('a.py', 'c.py'),
            ('b.py', 'c.py'),
            ('d.py', 'a.py'),
            ('d.py', 'b.py'),
            ('d.py', 'c.py')
        ])
        complex_modules = analyzer.analyze_dependency_complexity(threshold=2)
        assert 'd.py' in complex_modules
        assert len(complex_modules) == 1

    def test_detect_cycles(self, analyzer):
        analyzer.graph.add_edges_from([
            ('a.py', 'b.py'),
            ('b.py', 'c.py'),
            ('c.py', 'a.py')
        ])
        cycles = analyzer.detect_cycles()
        assert len(cycles) == 1
        assert len(cycles[0]) == 3

    def test_find_external_dependencies(self, analyzer):
        analyzer.graph.add_edge('a.py', 'requests', type='third_party', name='requests')
        analyzer.graph.add_edge('b.py', 'numpy', type='third_party', name='numpy')
        external_deps = analyzer.find_external_dependencies()
        assert len(external_deps) == 2
        assert 'requests' in external_deps
        assert 'numpy' in external_deps

    def test_analyze_imports_with_syntax_error(self, analyzer):
        with pytest.raises(ValueError):
            analyzer.analyze_imports("import os\nfrom import error")

    def test_get_dependency_metrics(self, analyzer):
        analyzer.graph.add_edges_from([
            ('a.py', 'b.py'),
            ('b.py', 'c.py'),
            ('c.py', 'd.py')
        ])
        metrics = analyzer.get_dependency_metrics()
        assert 'avg_dependencies' in metrics
        assert 'max_depth' in metrics
        assert 'modularity' in metrics

if __name__ == '__main__':
    pytest.main()
