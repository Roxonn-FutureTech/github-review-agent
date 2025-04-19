import pytest
import networkx as nx
import ast
from unittest.mock import patch, MagicMock
from src.ai_engine.dependency_analyzer import DependencyAnalyzer
from src.ai_engine.exceptions import DependencyAnalysisError

class TestDependencyAnalyzerExtended:
    @pytest.fixture
    def analyzer(self):
        return DependencyAnalyzer()

    @pytest.fixture
    def complex_sample_code(self):
        return """
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
import numpy as np
import pandas as pd
from .local_module import LocalClass, local_function
from ..parent_module import ParentClass
import package.submodule as submod
try:
    import optional_package
except ImportError:
    optional_package = None
"""

    def test_analyze_imports_complex(self, analyzer, complex_sample_code):
        """Test analyze_imports with complex import statements."""
        imports = analyzer.analyze_imports(complex_sample_code)

        # Check standard library imports
        assert len(imports['standard']) == 6  # os, sys, datetime, timedelta, typing (List, Dict, etc.)
        assert 'os' in imports['standard']
        assert 'sys' in imports['standard']
        assert 'datetime' in imports['standard']
        assert 'timedelta' in imports['standard']
        assert 'typing' in imports['standard']

        # Check third-party imports
        assert len(imports['third_party']) == 3  # numpy, pandas, optional_package
        assert 'numpy' in imports['third_party']
        assert 'pandas' in imports['third_party']
        assert 'optional_package' in imports['third_party']

        # Check local imports
        assert len(imports['local']) == 3  # .local_module, ..parent_module, package.submodule
        assert '.local_module' in imports['local']
        assert '..parent_module' in imports['local']
        assert 'package.submodule' in imports['local']

        # Check import details
        assert imports['details']['.local_module'] == ['LocalClass', 'local_function']
        assert imports['details']['..parent_module'] == ['ParentClass']
        assert imports['details']['package.submodule'] == ['submod']

    def test_analyze_imports_with_comments(self, analyzer):
        """Test analyze_imports with comments in the code."""
        code_with_comments = """
# Standard imports
import os
import sys

# Third-party imports
import numpy as np  # For numerical operations
import pandas as pd  # For data analysis

# Local imports
from .local_module import LocalClass  # Our custom class
"""
        imports = analyzer.analyze_imports(code_with_comments)

        assert len(imports['standard']) == 2
        assert len(imports['third_party']) == 2
        assert len(imports['local']) == 1

        assert 'os' in imports['standard']
        assert 'numpy' in imports['third_party']
        assert '.local_module' in imports['local']

    def test_analyze_imports_with_multiline(self, analyzer):
        """Test analyze_imports with multiline import statements."""
        multiline_imports = """
from module import (
    Class1,
    Class2,
    function1,
    function2
)

import long_module_name_that_requires_line_break as \\
    short_name
"""
        imports = analyzer.analyze_imports(multiline_imports)

        assert 'module' in imports['local']
        assert imports['details']['module'] == ['Class1', 'Class2', 'function1', 'function2']
        assert 'long_module_name_that_requires_line_break' in imports['local']

    def test_build_dependency_graph_complex(self, analyzer):
        """Test build_dependency_graph with complex dependencies."""
        files = {
            'module_a.py': 'import module_b\nimport module_c\nfrom module_d import Class',
            'module_b.py': 'from module_c import func\nimport module_e',
            'module_c.py': 'import os\nimport sys',
            'module_d.py': 'import module_c\nimport module_e',
            'module_e.py': 'import os'
        }

        graph = analyzer.build_dependency_graph(files)

        # Check nodes
        assert len(graph.nodes()) == 5  # 5 modules

        # Check edges
        assert graph.has_edge('module_a.py', 'module_b.py')
        assert graph.has_edge('module_a.py', 'module_c.py')
        assert graph.has_edge('module_a.py', 'module_d.py')
        assert graph.has_edge('module_b.py', 'module_c.py')
        assert graph.has_edge('module_b.py', 'module_e.py')
        assert graph.has_edge('module_d.py', 'module_c.py')
        assert graph.has_edge('module_d.py', 'module_e.py')

        # Check edge attributes
        assert graph.get_edge_data('module_a.py', 'module_b.py')['type'] == 'imports'
        assert graph.get_edge_data('module_a.py', 'module_d.py')['imported_symbols'] == ['Class']

    def test_build_dependency_graph_with_error(self, analyzer):
        """Test build_dependency_graph with syntax error in a file."""
        files = {
            'module_a.py': 'import module_b',
            'module_b.py': 'from import error'  # Syntax error
        }

        with pytest.raises(ValueError):
            analyzer.build_dependency_graph(files)

    def test_analyze_dependency_complexity_with_threshold(self, analyzer):
        """Test analyze_dependency_complexity with different thresholds."""
        # Create a test graph
        analyzer.graph = nx.DiGraph()
        analyzer.graph.add_edges_from([
            ('a.py', 'b.py'),
            ('a.py', 'c.py'),
            ('a.py', 'd.py'),
            ('b.py', 'c.py'),
            ('b.py', 'd.py'),
            ('e.py', 'a.py'),
            ('e.py', 'b.py'),
            ('f.py', 'a.py')
        ])

        # Test with threshold = 2
        complex_modules = analyzer.analyze_dependency_complexity(threshold=2)
        assert 'a.py' in complex_modules
        assert 'b.py' in complex_modules
        assert len(complex_modules) == 2

        # Test with threshold = 3
        complex_modules = analyzer.analyze_dependency_complexity(threshold=3)
        assert 'a.py' in complex_modules
        assert len(complex_modules) == 1

        # Test with threshold = 4
        complex_modules = analyzer.analyze_dependency_complexity(threshold=4)
        assert len(complex_modules) == 0

    def test_detect_cycles_complex(self, analyzer):
        """Test detect_cycles with multiple cycles."""
        analyzer.graph = nx.DiGraph()
        analyzer.graph.add_edges_from([
            ('a.py', 'b.py'),
            ('b.py', 'c.py'),
            ('c.py', 'a.py'),  # Cycle 1
            ('d.py', 'e.py'),
            ('e.py', 'f.py'),
            ('f.py', 'd.py'),  # Cycle 2
            ('g.py', 'h.py'),
            ('h.py', 'i.py')   # No cycle
        ])

        cycles = analyzer.detect_cycles()

        assert len(cycles) == 2

        # Check cycle 1
        cycle1 = next(cycle for cycle in cycles if 'a.py' in cycle)
        assert len(cycle1) == 3
        assert 'a.py' in cycle1
        assert 'b.py' in cycle1
        assert 'c.py' in cycle1

        # Check cycle 2
        cycle2 = next(cycle for cycle in cycles if 'd.py' in cycle)
        assert len(cycle2) == 3
        assert 'd.py' in cycle2
        assert 'e.py' in cycle2
        assert 'f.py' in cycle2

    def test_find_external_dependencies_with_versions(self, analyzer):
        """Test find_external_dependencies with version information."""
        analyzer.graph = nx.DiGraph()

        # Add edges with version information
        analyzer.graph.add_edge('a.py', 'requests', type='third_party', name='requests', version='2.25.1')
        analyzer.graph.add_edge('b.py', 'numpy', type='third_party', name='numpy', version='1.20.1')
        analyzer.graph.add_edge('c.py', 'pandas', type='third_party', name='pandas', version='1.2.3')
        analyzer.graph.add_edge('d.py', 'requests', type='third_party', name='requests', version='2.25.1')

        external_deps = analyzer.find_external_dependencies()

        assert len(external_deps) == 3
        assert 'requests' in external_deps
        assert 'numpy' in external_deps
        assert 'pandas' in external_deps

        # Check version information
        assert external_deps['requests']['version'] == '2.25.1'
        assert external_deps['requests']['count'] == 2  # Used in 2 files
        assert external_deps['numpy']['version'] == '1.20.1'
        assert external_deps['pandas']['version'] == '1.2.3'

    def test_analyze_module_dependencies(self, analyzer):
        """Test analyze_module_dependencies method."""
        # Create a test graph
        analyzer.graph = nx.DiGraph()
        analyzer.graph.add_edges_from([
            ('module_a/file1.py', 'module_b/file1.py'),
            ('module_a/file2.py', 'module_b/file2.py'),
            ('module_a/file3.py', 'module_c/file1.py'),
            ('module_b/file1.py', 'module_c/file1.py'),
            ('module_b/file2.py', 'module_c/file2.py'),
            ('module_c/file1.py', 'module_d/file1.py')
        ])

        module_deps = analyzer.analyze_module_dependencies()

        assert len(module_deps) == 4  # 4 module-to-module dependencies

        # Check module_a -> module_b dependency
        assert ('module_a', 'module_b') in module_deps
        assert module_deps[('module_a', 'module_b')] == 2  # 2 files in module_a depend on module_b

        # Check module_a -> module_c dependency
        assert ('module_a', 'module_c') in module_deps
        assert module_deps[('module_a', 'module_c')] == 1

        # Check module_b -> module_c dependency
        assert ('module_b', 'module_c') in module_deps
        assert module_deps[('module_b', 'module_c')] == 2

    def test_get_dependency_metrics(self, analyzer):
        """Test get_dependency_metrics method."""
        # Create a test graph
        analyzer.graph = nx.DiGraph()
        analyzer.graph.add_edges_from([
            ('a.py', 'b.py'),
            ('a.py', 'c.py'),
            ('b.py', 'd.py'),
            ('c.py', 'd.py'),
            ('d.py', 'e.py'),
            ('f.py', 'a.py')
        ])

        metrics = analyzer.get_dependency_metrics()

        assert metrics['total_files'] == 6
        assert metrics['total_dependencies'] == 6
        assert metrics['avg_dependencies_per_file'] == 1.0
        assert metrics['max_dependencies'] == 2  # a.py has 2 dependencies
        assert metrics['files_with_no_dependencies'] == 1  # e.py has no dependencies
        assert metrics['files_with_most_dependencies'] == ['a.py']
        assert metrics['most_depended_upon_files'] == ['d.py']  # 2 files depend on d.py

    def test_visualize_dependencies(self, analyzer):
        """Test visualize_dependencies method."""
        # Create a test graph
        analyzer.graph = nx.DiGraph()
        analyzer.graph.add_edges_from([
            ('a.py', 'b.py'),
            ('a.py', 'c.py'),
            ('b.py', 'd.py')
        ])

        # Mock the nx.draw function
        with patch('networkx.draw') as mock_draw:
            with patch('matplotlib.pyplot.savefig') as mock_savefig:
                analyzer.visualize_dependencies('test_output.png')

                # Verify the functions were called
                mock_draw.assert_called_once()
                mock_savefig.assert_called_once_with('test_output.png')

    def test_get_module_from_file(self, analyzer):
        """Test _get_module_from_file method."""
        assert analyzer._get_module_from_file('module_a/file.py') == 'module_a'
        assert analyzer._get_module_from_file('module_a/submodule/file.py') == 'module_a/submodule'
        assert analyzer._get_module_from_file('file.py') == ''
        assert analyzer._get_module_from_file('') == ''

    def test_analyze_imports_error_handling(self, analyzer):
        """Test error handling in analyze_imports method."""
        # Test with invalid Python code
        with pytest.raises(ValueError):
            analyzer.analyze_imports("import 123")

        # Test with empty string
        result = analyzer.analyze_imports("")
        assert result['standard'] == []
        assert result['third_party'] == []
        assert result['local'] == []
        assert result['details'] == {}

    def test_get_import_type(self, analyzer):
        """Test _get_import_type method."""
        # Standard library imports
        assert analyzer._get_import_type('os') == 'standard'
        assert analyzer._get_import_type('sys') == 'standard'
        assert analyzer._get_import_type('datetime') == 'standard'

        # Third-party imports
        assert analyzer._get_import_type('numpy') == 'third_party'
        assert analyzer._get_import_type('pandas') == 'third_party'
        assert analyzer._get_import_type('requests') == 'third_party'

        # Local imports
        assert analyzer._get_import_type('.local_module') == 'local'
        assert analyzer._get_import_type('..parent_module') == 'local'
        assert analyzer._get_import_type('package.submodule') == 'local'

    def test_is_standard_library(self, analyzer):
        """Test _is_standard_library method."""
        # Standard library modules
        assert analyzer._is_standard_library('os')
        assert analyzer._is_standard_library('sys')
        assert analyzer._is_standard_library('datetime')
        assert analyzer._is_standard_library('collections')
        assert analyzer._is_standard_library('json')

        # Non-standard library modules
        assert not analyzer._is_standard_library('numpy')
        assert not analyzer._is_standard_library('pandas')
        assert not analyzer._is_standard_library('requests')
        assert not analyzer._is_standard_library('.local_module')
        assert not analyzer._is_standard_library('package.submodule')
