"""
Database Connection Module
Handles PostgreSQL connections and queries
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config

class Database:
    """Database connection handler"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**Config.get_db_config())
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def execute_query(self, query, params=None):
        """Execute a SELECT query and return results"""
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Query error: {e}")
            return []
    
    def execute_one(self, query, params=None):
        """Execute a SELECT query and return one result"""
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Query error: {e}")
            return None
    
    def execute_insert(self, query, params=None):
        """Execute an INSERT query and return the inserted ID"""
        try:
            self.cursor.execute(query, params or ())
            self.conn.commit()
            
            # Try to get the inserted ID
            if 'RETURNING' in query.upper():
                result = self.cursor.fetchone()
                return result if result else None
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Insert error: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """Execute an UPDATE query"""
        try:
            self.cursor.execute(query, params or ())
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            print(f"Update error: {e}")
            return 0
    
    def execute_delete(self, query, params=None):
        """Execute a DELETE query"""
        try:
            self.cursor.execute(query, params or ())
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            print(f"Delete error: {e}")
            return 0

def get_db():
    """Get database connection"""
    db = Database()
    if db.connect():
        return db
    return None
