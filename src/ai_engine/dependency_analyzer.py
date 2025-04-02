from typing import Dict, List
import networkx as nx
import ast
from pathlib import Path
from .logging_config import get_logger

logger = get_logger(__name__)

class DependencyAnalyzer:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.dependency_graph = nx.DiGraph()
        
    def analyze_imports(self, ast_tree: ast.AST, file_path: str) -> Dict:
        """Analyzes import statements and their relationships."""
        imports = []
        for node in ast.walk(ast_tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(self._process_import(node))
        return {'file': file_path, 'imports': imports}
    
    def _process_import(self, node: ast.AST) -> Dict:
        """Processes individual import statements."""
        if isinstance(node, ast.Import):
            return {
                'type': 'import',
                'module': node.names[0].name,
                'alias': node.names[0].asname
            }
        elif isinstance(node, ast.ImportFrom):
            return {
                'type': 'importfrom',
                'module': node.module,
                'name': node.names[0].name,
                'alias': node.names[0].asname
            }
            
    def build_dependency_graph(self, imports_data: List[Dict]):
        """Builds a graph representation of project dependencies."""
        for file_data in imports_data:
            file_path = file_data['file']
            self.dependency_graph.add_node(file_path, type='file')
            
            for imp in file_data['imports']:
                module = imp.get('module')
                if module:
                    self.dependency_graph.add_node(module, type='module')
                    self.dependency_graph.add_edge(file_path, module, type=imp['type'])
                
                # Add imported name if it exists
                if 'name' in imp:
                    self.dependency_graph.add_node(imp['name'], type='import')
                    self.dependency_graph.add_edge(module, imp['name'], type='provides')
        
        return self.dependency_graph

    def analyze(self, ast_trees: Dict) -> Dict:
        """Analyzes dependencies in AST trees."""
        result = {}
        for file_path, tree_data in ast_trees.items():
            imports = self.analyze_imports(tree_data['ast'], file_path)
            result[file_path] = imports
        return result



