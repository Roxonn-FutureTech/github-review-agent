import sqlite3
import json
import logging
from typing import Dict, List, Optional
from .exceptions import KnowledgeBaseError
import networkx as nx
from .logging_config import get_logger

logger = logging.getLogger(__name__)

class KnowledgeBase:
    def __init__(self, db_path: str = "knowledge.db"):
        self.logger = get_logger(__name__)
        self.db_path = db_path
        self.graph = nx.DiGraph()  # Initialize graph in constructor
        self.conn = sqlite3.connect(self.db_path)  # Initialize database connection
        self._initialize_db()
    
    def __del__(self):
        """Cleanup database connection on object destruction."""
        if hasattr(self, 'conn'):
            self.conn.close()
    
    def _initialize_db(self):
        """Initializes database tables."""
        try:
            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS code_patterns (
                        id INTEGER PRIMARY KEY,
                        pattern_type TEXT NOT NULL,
                        pattern_data TEXT NOT NULL,
                        frequency INTEGER DEFAULT 1
                    )
                """)
                
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS dependencies (
                        id INTEGER PRIMARY KEY,
                        source_file TEXT NOT NULL,
                        target_file TEXT NOT NULL,
                        dependency_type TEXT NOT NULL
                    )
                """)
            self.logger.debug("Database tables initialized")
        except Exception as e:
            self.logger.error(f"Database initialization failed: {str(e)}")
            raise KnowledgeBaseError(f"Failed to create tables: {str(e)}")
    
    def store_pattern(self, pattern: Dict):
        """Stores a code pattern in the database."""
        try:
            # Use pattern_type directly from input
            pattern_type = pattern.get('pattern_type')
            pattern_data = json.dumps(pattern.get('data', {}))
            frequency = pattern.get('frequency', 1)
            
            with self.conn:
                self.conn.execute(
                    """
                    INSERT INTO code_patterns (pattern_type, pattern_data, frequency)
                    VALUES (?, ?, ?)
                    """,
                    (pattern_type, pattern_data, frequency)
                )
            self.logger.debug(f"Stored pattern: {pattern_type}")
        except Exception as e:
            self.logger.error(f"Failed to store pattern: {str(e)}")
            raise KnowledgeBaseError(f"Failed to store pattern: {str(e)}")

    def get_patterns(self, file_path: str) -> List[Dict]:
        """Retrieves all patterns for a specific file."""
        try:
            cursor = self.conn.execute(
                """
                SELECT pattern_type, pattern_data, frequency 
                FROM code_patterns 
                WHERE json_extract(pattern_data, '$.file') = ?
                """,
                (file_path,)
            )
            
            patterns = []
            for row in cursor:
                patterns.append({
                    'type': row[0],
                    'data': json.loads(row[1]),
                    'frequency': row[2]
                })
            return patterns
        except Exception as e:
            self.logger.error(f"Failed to retrieve patterns: {str(e)}")
            raise KnowledgeBaseError(f"Failed to retrieve patterns: {str(e)}")

    def build_graph(self, nodes, edges):
        """Build knowledge graph from nodes and edges"""
        # Clear existing graph
        self.graph.clear()
        
        # Add nodes and edges
        for node, attrs in nodes:
            self.graph.add_node(node, **attrs)
        for src, dst, attrs in edges:
            self.graph.add_edge(src, dst, **attrs)

    def get_related_components(self, node):
        """Get all components related to a node"""
        # Get both predecessors and successors
        related = list(self.graph.predecessors(node)) + list(self.graph.successors(node))
        return list(set(related))  # Remove duplicates

    def has_dependency(self, source, target):
        """Check if source depends on target"""
        return self.graph.has_edge(source, target)

    def query_knowledge(self, query: Dict) -> List[Dict]:
        """Query the knowledge base for patterns matching specific criteria."""
        try:
            cursor = self.conn.cursor()
            
            # Build the SQL query based on the filter criteria
            sql = "SELECT pattern_type, pattern_data, frequency FROM code_patterns"
            params = []
            
            # Add WHERE clause if pattern_type is specified
            if 'pattern_type' in query:
                sql += " WHERE pattern_type = ?"
                params.append(query['pattern_type'])
                
            # Add LIMIT if specified
            if 'limit' in query:
                sql += " LIMIT ?"
                params.append(query['limit'])
                
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # Convert rows to list of dictionaries
            results = []
            for row in rows:
                results.append({
                    'pattern_type': row[0],
                    'data': json.loads(row[1]),
                    'frequency': row[2]
                })
                
            return results
        except Exception as e:
            self.logger.error(f"Failed to query knowledge base: {str(e)}")
            raise KnowledgeBaseError(f"Query failed: {str(e)}")

    def store_patterns(self, patterns: List[Dict]) -> None:
        """Store multiple patterns in the database."""
        try:
            for pattern in patterns:
                # Convert the pattern format to match store_pattern expectations
                converted_pattern = {
                    'pattern_type': pattern['type'],
                    'data': {
                        'name': pattern['name'],
                        'file': pattern['file']
                    },
                    'frequency': 1  # Default frequency for new patterns
                }
                self.store_pattern(converted_pattern)
            self.logger.debug(f"Stored {len(patterns)} patterns")
        except Exception as e:
            self.logger.error(f"Failed to store patterns: {str(e)}")
            raise KnowledgeBaseError(f"Failed to store patterns: {str(e)}")
