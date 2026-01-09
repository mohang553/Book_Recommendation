"""
database.py
Handles all database setup and basic operations
"""

import sqlite3
from datetime import datetime

class BookSharingDatabase:
    """Handles all database operations"""
    
    def __init__(self, db_name="book_sharing.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.create_tables()
    
    def create_tables(self):
        """Create all necessary tables"""
        cursor = self.conn.cursor()
        
        # Users table (Parents and Children)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                community_name TEXT,
                user_type TEXT, -- 'parent' or 'child'
                parent_id INTEGER,
                age INTEGER,
                created_date TEXT,
                subscription_type TEXT, -- 'monthly' or 'annual'
                subscription_expiry TEXT,
                FOREIGN KEY (parent_id) REFERENCES users(user_id)
            )
        """)
        
        # Books table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                genre TEXT,
                age_group TEXT, -- '5-8', '9-12', '13-16', etc.
                owner_id INTEGER,
                condition TEXT, -- 'new', 'good', 'fair'
                book_type TEXT, -- 'story', 'textbook', 'reference'
                available INTEGER DEFAULT 1, -- 1 = available, 0 = borrowed
                added_date TEXT,
                FOREIGN KEY (owner_id) REFERENCES users(user_id)
            )
        """)
        
        # Borrowing records
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS borrowing_records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                borrower_id INTEGER,
                borrow_date TEXT,
                due_date TEXT,
                return_date TEXT,
                status TEXT, -- 'active', 'returned', 'overdue'
                FOREIGN KEY (book_id) REFERENCES books(book_id),
                FOREIGN KEY (borrower_id) REFERENCES users(user_id)
            )
        """)
        
        # Reading history and ratings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reading_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                book_id INTEGER,
                rating INTEGER, -- 1-5 stars
                completed_date TEXT,
                review TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (book_id) REFERENCES books(book_id)
            )
        """)
        
        # Gamification - User achievements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER PRIMARY KEY,
                total_books_read INTEGER DEFAULT 0,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                total_points INTEGER DEFAULT 0,
                badges TEXT, -- JSON list of badges
                last_activity_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        self.conn.commit()
        print("✓ Database tables created successfully")
    
    def get_connection(self):
        """Get database connection"""
        return self.conn
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        print("✓ Database connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    
    def commit(self):
        """Commit changes to database"""
        self.conn.commit()


if __name__ == "__main__":
    # Test database creation
    print("Creating database...")
    db = BookSharingDatabase()
    print("Database created successfully!")
    db.close()