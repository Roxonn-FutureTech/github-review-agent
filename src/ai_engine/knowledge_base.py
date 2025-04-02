import sqlite3
import json
import logging
from typing import Dict, List
from .exceptions import KnowledgeBaseError

logger = logging.getLogger(__name__)

class KnowledgeBase:
    def __init__(self, db_path: str):
        self.logger = logging.getLogger(__name__)
        try:
            self.conn = sqlite3.connect(db_path)
            self._initialize_db()
            self.logger.info(f"Knowledge base initialized: {db_path}")
        except Exception as e:
            self.logger.error(f"Failed to initialize knowledge base: {str(e)}")
            raise KnowledgeBaseError(f"Database initialization failed: {str(e)}")
    
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
            with self.conn:
                self.conn.execute(
                    """
                    INSERT INTO code_patterns (pattern_type, pattern_data, frequency)
                    VALUES (?, ?, ?)
                    """,
                    (
                        pattern['pattern_type'],
                        json.dumps(pattern['data']),
                        pattern['frequency']
                    )
                )
            self.logger.debug(f"Stored pattern: {pattern['pattern_type']}")
        except Exception as e:
            self.logger.error(f"Failed to store pattern: {str(e)}")
            raise KnowledgeBaseError(f"Failed to store pattern: {str(e)}")
    
    def query_knowledge(self, query: Dict) -> List[Dict]:
        """Queries the knowledge base for specific patterns or insights."""
        try:
            pattern_type = query.get('pattern_type')
            limit = query.get('limit', 10)
            
            with self.conn:
                if pattern_type:
                    cursor = self.conn.execute(
                        """
                        SELECT pattern_type, pattern_data, frequency 
                        FROM code_patterns 
                        WHERE pattern_type = ? 
                        ORDER BY frequency DESC 
                        LIMIT ?
                        """,
                        (pattern_type, limit)
                    )
                else:
                    cursor = self.conn.execute(
                        """
                        SELECT pattern_type, pattern_data, frequency 
                        FROM code_patterns 
                        ORDER BY frequency DESC 
                        LIMIT ?
                        """,
                        (limit,)
                    )
                    
            results = []
            for row in cursor:
                results.append({
                    'pattern_type': row[0],
                    'data': json.loads(row[1]),
                    'frequency': row[2]
                })
            
            self.logger.info(f"Query returned {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"Knowledge base query failed: {str(e)}")
            raise KnowledgeBaseError(f"Failed to query knowledge base: {str(e)}")
