import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch._utils")

from typing import Dict, List, Optional
import ast
import os
import logging
import networkx as nx
from transformers import AutoTokenizer, AutoModel
import torch
from .dependency_analyzer import DependencyAnalyzer
from .pattern_recognizer import PatternRecognizer
from .exceptions import CodeParsingError, ModelLoadError, DependencyAnalysisError, PatternAnalysisError
from .logging_config import get_logger

logger = get_logger(__name__)  # Fix: Add __name__ as parameter

class CodeAnalyzer:
    def __init__(self, model_name: str = "microsoft/codebert-base"):
        self.logger = get_logger(__name__)  # Fix: Add __name__ as parameter
        try:
            self.logger.info(f"Initializing CodeAnalyzer with model: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.knowledge_graph = nx.DiGraph()
            self.dependency_analyzer = DependencyAnalyzer()
            self.pattern_recognizer = PatternRecognizer(self.model)
        except Exception as e:
            self.logger.error(f"Failed to initialize CodeAnalyzer: {str(e)}")
            raise ModelLoadError(f"Failed to load model {model_name}: {str(e)}")
        
    def scan_repository(self, repo_path: str) -> Dict:
        """Scans repository and builds knowledge base."""
        try:
            if not os.path.exists(repo_path):
                raise FileNotFoundError(f"Repository path not found: {repo_path}")
            
            self.logger.info(f"Starting repository scan: {repo_path}")
            self.files = self._collect_files(repo_path)
            self.logger.info(f"Found {len(self.files)} source files")
            
            self.ast_trees = self._parse_files()
            self.logger.info(f"Successfully parsed {len(self.ast_trees)} files")
            
            self.dependencies = self._analyze_dependencies()
            self.logger.info("Dependency analysis completed")
            
            knowledge = self._build_knowledge_representation()
            self.logger.info("Knowledge base built successfully")
            return knowledge
        
        except FileNotFoundError as e:
            self.logger.error(f"Repository path not found: {str(e)}")
            raise CodeParsingError(f"Failed to scan repository: {str(e)}")
        except Exception as e:
            self.logger.error(f"Repository scan failed: {str(e)}")
            raise CodeParsingError(f"Failed to scan repository: {str(e)}")
    
    def _collect_files(self, path: str) -> List[str]:
        """Recursively collects all relevant source files."""
        try:
            source_files = []
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(('.py', '.js', '.java', '.cpp', '.h')):
                        source_files.append(os.path.join(root, file))
            return source_files
        except Exception as e:
            self.logger.error(f"File collection failed: {str(e)}")
            raise CodeParsingError(f"Failed to collect files: {str(e)}")

    def _parse_files(self) -> Dict:
        """Parses source files into AST trees."""
        ast_trees = {}
        for file_path in self.files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast_trees[file_path] = {
                    'ast': ast.parse(content),
                    'content': content
                }
            except SyntaxError as e:
                self.logger.error(f"Failed to parse {file_path}: {str(e)}")
                raise CodeParsingError(f"Invalid syntax in {file_path}: {str(e)}")
            except Exception as e:
                self.logger.error(f"Failed to parse {file_path}: {str(e)}")
                raise CodeParsingError(f"Failed to parse {file_path}: {str(e)}")
        return ast_trees

    def _analyze_dependencies(self) -> Dict:
        """Analyzes dependencies between files."""
        try:
            dependencies = {}
            for file_path, tree_info in self.ast_trees.items():
                imports = []
                for node in ast.walk(tree_info['ast']):
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            imports.append({'module': name.name, 'type': 'import'})
                    elif isinstance(node, ast.ImportFrom):
                        for name in node.names:
                            imports.append({
                                'module': node.module,
                                'name': name.name,
                                'type': 'importfrom'
                            })
                dependencies[file_path] = {'imports': imports}
            return dependencies
        except Exception as e:
            self.logger.error(f"Dependency analysis failed: {str(e)}")
            raise DependencyAnalysisError(str(e))

    def _build_knowledge_representation(self) -> Dict:
        """Builds comprehensive knowledge representation."""
        try:
            patterns = self.pattern_recognizer.analyze(self.ast_trees)
            self.logger.info(f"Identified {len(patterns)} code patterns")
            
            return {
                'files': self.files,
                'dependencies': self.dependencies,
                'patterns': patterns,
                'graph': self.knowledge_graph
            }
        except Exception as e:
            self.logger.error(f"Knowledge representation build failed: {str(e)}")
            raise PatternAnalysisError(str(e))

    def identify_patterns(self, code_snippet: str) -> List[Dict]:
        """Identifies common patterns in code."""
        pass

    def test_build_knowledge_representation(self):
        # Setup test data
        self.analyzer.files = [
            os.path.join(self.test_dir, 'main.py'),
            os.path.join(self.test_dir, 'utils.py')
        ]
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
        
        self.assertIn('files', knowledge)
        self.assertIn('dependencies', knowledge)
        self.assertIn('patterns', knowledge)
        self.assertIn('graph', knowledge)
