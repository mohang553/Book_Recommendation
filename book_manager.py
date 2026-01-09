"""
book_manager.py
Manages book catalog, borrowing, and returns
"""

from datetime import datetime, timedelta

class BookManager:
    """Manages book catalog and borrowing"""
    
    def __init__(self, db):
        self.db = db
    
    def add_book(self, title, author, genre, age_group, owner_id, 
                 condition='good', book_type='story'):
        """Add a new book to the catalog"""
        cursor = self.db.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO books (title, author, genre, age_group, owner_id, 
                                 condition, book_type, added_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, author, genre, age_group, owner_id, condition, 
                  book_type, datetime.now().strftime('%Y-%m-%d')))
            
            self.db.conn.commit()
            print(f"✓ Book added: {title} by {author}")
            return cursor.lastrowid
        
        except Exception as e:
            print(f"✗ Error adding book: {e}")
            return None
    
    def search_books(self, community_name, genre=None, age_group=None, 
                     available_only=True, search_term=None):
        """Search for books in a community"""
        cursor = self.db.conn.cursor()
        
        query = """
            SELECT b.book_id, b.title, b.author, b.genre, b.age_group, 
                   b.condition, b.available, u.name as owner_name, b.book_type
            FROM books b
            JOIN users u ON b.owner_id = u.user_id
            WHERE u.community_name = ?
        """
        params = [community_name]
        
        if available_only:
            query += " AND b.available = 1"
        if genre:
            query += " AND b.genre = ?"
            params.append(genre)
        if age_group:
            query += " AND b.age_group = ?"
            params.append(age_group)
        if search_term:
            query += " AND (b.title LIKE ? OR b.author LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        print(f"✓ Found {len(results)} books")
        return results
    
    def borrow_book(self, book_id, borrower_id, days=14):
        """Borrow a book"""
        cursor = self.db.conn.cursor()
        
        cursor.execute("SELECT available, title FROM books WHERE book_id = ?", (book_id,))
        result = cursor.fetchone()
        
        if not result:
            return False, "Book not found"
        
        if not result[0]:
            return False, "Book is currently borrowed"
        
        book_title = result[1]
        
        try:
            borrow_date = datetime.now()
            due_date = borrow_date + timedelta(days=days)
            
            cursor.execute("""
                INSERT INTO borrowing_records (book_id, borrower_id, borrow_date, 
                                              due_date, status)
                VALUES (?, ?, ?, ?, 'active')
            """, (book_id, borrower_id, borrow_date.strftime('%Y-%m-%d'),
                  due_date.strftime('%Y-%m-%d')))
            
            cursor.execute("UPDATE books SET available = 0 WHERE book_id = ?", (book_id,))
            
            self.db.conn.commit()
            print(f"✓ Book borrowed: {book_title}")
            return True, "Book borrowed successfully"
        
        except Exception as e:
            print(f"✗ Error borrowing book: {e}")
            return False, f"Error: {e}"
    
    def return_book(self, book_id, borrower_id, rating=None, review=None):
        """Return a borrowed book"""
        cursor = self.db.conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE borrowing_records 
                SET return_date = ?, status = 'returned'
                WHERE book_id = ? AND borrower_id = ? AND status = 'active'
            """, (datetime.now().strftime('%Y-%m-%d'), book_id, borrower_id))
            
            cursor.execute("UPDATE books SET available = 1 WHERE book_id = ?", (book_id,))
            
            if rating:
                cursor.execute("""
                    INSERT INTO reading_history (user_id, book_id, rating, 
                                                completed_date, review)
                    VALUES (?, ?, ?, ?, ?)
                """, (borrower_id, book_id, rating, 
                      datetime.now().strftime('%Y-%m-%d'), review))
            
            self.db.conn.commit()
            print(f"✓ Book returned successfully")
            if rating:
                print(f"  Rating: {rating}/5 stars")
            return True
        
        except Exception as e:
            print(f"✗ Error returning book: {e}")
            return False
    
    def get_popular_books(self, community_name, limit=10):
        """Get most borrowed books in a community"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT b.title, b.author, COUNT(*) as borrow_count,
                   AVG(rh.rating) as avg_rating
            FROM borrowing_records br
            JOIN books b ON br.book_id = b.book_id
            JOIN users u ON b.owner_id = u.user_id
            LEFT JOIN reading_history rh ON b.book_id = rh.book_id
            WHERE u.community_name = ?
            GROUP BY b.book_id
            ORDER BY borrow_count DESC
            LIMIT ?
        """, (community_name, limit))
        
        return cursor.fetchall()