import sqlite3
import json
import networkx as nx
from typing import Dict, List, Any, Optional
from pathlib import Path
from .exceptions import KnowledgeBaseError

class KnowledgeBase:
    """Manages code knowledge and patterns."""

    def __init__(self, db_path: str = "knowledge.db"):
        self.db_path = db_path
        self.graph = nx.DiGraph()
        self.conn = None
        self.initialize_db()

    def initialize_db(self) -> None:
        """Initialize the SQLite database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern_type TEXT NOT NULL,
                        pattern_data TEXT NOT NULL,
                        frequency INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to initialize database: {str(e)}")

    def store_pattern(self, pattern_type: str, pattern_data: Dict[str, Any], frequency: int = 1) -> bool:
        """Store a code pattern in the database."""
        try:
            if pattern_type is None or pattern_data is None:
                raise ValueError("Pattern type and data cannot be None")

            pattern_data_json = json.dumps(pattern_data)

            with sqlite3.connect(self.db_path) as conn:
                self.conn = conn  # Store connection for test access
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO patterns (pattern_type, pattern_data, frequency)
                    VALUES (?, ?, ?)
                """, (pattern_type, pattern_data_json, frequency))
                conn.commit()
            return True
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to store pattern: {str(e)}")

    def store_patterns(self, patterns: List[Dict[str, Any]]) -> bool:
        """Store multiple patterns at once."""
        try:
            for pattern in patterns:
                pattern_type = pattern.get('type')
                pattern_data = pattern.get('data')
                if pattern_type and pattern_data:
                    self.store_pattern(pattern_type, pattern_data)
            return True
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to store patterns: {str(e)}")

    def retrieve_patterns(self, pattern_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve patterns from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if pattern_type:
                    cursor.execute("""
                        SELECT pattern_type, pattern_data, frequency
                        FROM patterns
                        WHERE pattern_type = ?
                    """, (pattern_type,))
                else:
                    cursor.execute("""
                        SELECT pattern_type, pattern_data, frequency
                        FROM patterns
                    """)

                patterns = []
                for row in cursor.fetchall():
                    patterns.append({
                        'pattern_type': row[0],
                        'data': json.loads(row[1]),
                        'frequency': row[2]
                    })
                return patterns
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to retrieve patterns: {str(e)}")

    def update_pattern_frequency(self, pattern_type: str, new_frequency: int) -> bool:
        """Update the frequency of a pattern."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                self.conn = conn  # Store connection for test access
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE patterns
                    SET frequency = ?
                    WHERE pattern_type = ?
                """, (new_frequency, pattern_type))
                conn.commit()
            return True
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to update pattern frequency: {str(e)}")

    def delete_pattern(self, pattern_type: str) -> bool:
        """Delete a pattern from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                self.conn = conn  # Store connection for test access
                cursor = conn.cursor()
                cursor.execute("DELETE FROM patterns WHERE pattern_type = ?", (pattern_type,))
                conn.commit()
            return True
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to delete pattern: {str(e)}")

    def clear(self) -> bool:
        """Clear all patterns from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                self.conn = conn  # Store connection for test access
                cursor = conn.cursor()
                cursor.execute("DELETE FROM patterns")
                conn.commit()
            return True
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to clear knowledge base: {str(e)}")

    def build_graph(self, nodes: List[tuple], edges: List[tuple]) -> None:
        """Build a knowledge graph."""
        try:
            self.graph.clear()
            self.graph.add_nodes_from(nodes)
            self.graph.add_edges_from(edges)
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to build graph: {str(e)}")

    def has_dependency(self, source: str, target: str) -> bool:
        """Check if there is a dependency between two nodes."""
        return self.graph.has_edge(source, target)

    def get_dependencies(self, node: str) -> List[str]:
        """Get all dependencies of a node."""
        return list(self.graph.successors(node))

    def get_dependents(self, node: str) -> List[str]:
        """Get all nodes that depend on the given node."""
        return list(self.graph.predecessors(node))

    def get_graph_metrics(self) -> Dict[str, Any]:
        """Calculate graph metrics."""
        return {
            'nodes': len(self.graph),
            'edges': len(self.graph.edges()),
            'density': nx.density(self.graph),
            'is_dag': nx.is_directed_acyclic_graph(self.graph)
        }

    def get_patterns(self, file_path: str) -> List[Dict[str, Any]]:
        """Get patterns for a specific file."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                self.conn = conn  # Store connection for test access
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT pattern_type, pattern_data, frequency
                    FROM patterns
                    WHERE json_extract(pattern_data, '$.file') = ?
                """, (file_path,))

                patterns = []
                for row in cursor.fetchall():
                    patterns.append({
                        'type': row[0],
                        'data': json.loads(row[1]),
                        'frequency': row[2]
                    })
                return patterns
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to get patterns: {str(e)}")

    def get_related_components(self, component_id: str) -> List[str]:
        """Get components related to the given component."""
        try:
            # Get all neighbors (both predecessors and successors)
            related = list(self.graph.successors(component_id))
            related.extend(list(self.graph.predecessors(component_id)))

            # Remove duplicates
            return list(set(related))
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to get related components: {str(e)}")
