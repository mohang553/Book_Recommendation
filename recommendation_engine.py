"""
recommendation_engine.py
Machine Learning-based book recommendation system
"""

from collections import defaultdict

class RecommendationEngine:
    """ML-based book recommendation system"""
    
    def __init__(self, db):
        self.db = db
    
    def get_user_reading_profile(self, user_id):
        """
        Build a profile of user's reading preferences
        
        Args:
            user_id: User's ID
        
        Returns:
            dict: User's reading preferences with scores
        """
        cursor = self.db.conn.cursor()
        
        # Get books read and ratings
        cursor.execute("""
            SELECT b.genre, b.author, b.age_group, rh.rating
            FROM reading_history rh
            JOIN books b ON rh.book_id = b.book_id
            WHERE rh.user_id = ?
        """, (user_id,))
        
        history = cursor.fetchall()
        
        # Calculate preferences
        genre_scores = defaultdict(float)
        author_scores = defaultdict(float)
        
        for genre, author, age_group, rating in history:
            if rating:  # Only count if user rated the book
                genre_scores[genre] += rating
                author_scores[author] += rating
        
        profile = {
            'genres': dict(genre_scores),
            'authors': dict(author_scores),
            'total_books': len(history)
        }
        
        print(f"✓ Reading profile created for user {user_id}")
        print(f"  Total books read: {len(history)}")
        if genre_scores:
            top_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"  Favorite genres: {top_genres}")
        
        return profile
    
    def recommend_books(self, user_id, limit=5):
        """
        Recommend books using collaborative and content-based filtering
        
        Algorithm:
        1. Content-based: Match user's preferred genres and authors
        2. Collaborative: Find books liked by similar users
        3. Combine scores and return top recommendations
        
        Args:
            user_id: User's ID
            limit: Number of recommendations to return
        
        Returns:
            list: List of recommended books with scores
        """
        cursor = self.db.conn.cursor()
        
        # Get user's community and age
        cursor.execute("""
            SELECT community_name, age FROM users WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        if not result:
            print("✗ User not found")
            return []
        
        community, age = result
        
        # Determine age group
        if age <= 8:
            age_group = '5-8'
        elif age <= 12:
            age_group = '9-12'
        elif age <= 16:
            age_group = '13-16'
        else:
            age_group = '16+'
        
        # Get user's reading profile
        profile = self.get_user_reading_profile(user_id)
        
        # Get books user hasn't read yet
        cursor.execute("""
            SELECT b.book_id, b.title, b.author, b.genre
            FROM books b
            JOIN users u ON b.owner_id = u.user_id
            WHERE u.community_name = ?
            AND b.age_group = ?
            AND b.available = 1
            AND b.book_id NOT IN (
                SELECT book_id FROM reading_history WHERE user_id = ?
            )
            AND b.book_id NOT IN (
                SELECT book_id FROM borrowing_records 
                WHERE borrower_id = ? AND status = 'active'
            )
        """, (community, age_group, user_id, user_id))
        
        available_books = cursor.fetchall()
        
        if not available_books:
            print("✗ No new books available for recommendations")
            return []
        
        # Score each book
        recommendations = []
        for book_id, title, author, genre in available_books:
            score = 0
            
            # Content-based filtering: Genre preference
            if genre in profile['genres']:
                genre_score = profile['genres'][genre] * 2.0
                score += genre_score
            
            # Content-based filtering: Author preference
            if author in profile['authors']:
                author_score = profile['authors'][author] * 1.5
                score += author_score
            
            # Collaborative filtering: Average rating from all users
            cursor.execute("""
                SELECT AVG(rating) 
                FROM reading_history 
                WHERE book_id = ?
            """, (book_id,))
            
            avg_rating = cursor.fetchone()[0]
            if avg_rating:
                score += avg_rating
            else:
                # New books get a neutral score
                score += 3.0
            
            # Collaborative filtering: Similar users' preferences
            # Find users who liked same books as current user
            cursor.execute("""
                SELECT COUNT(*) as common_books
                FROM reading_history rh1
                JOIN reading_history rh2 ON rh1.book_id = rh2.book_id
                WHERE rh1.user_id = ? 
                AND rh2.user_id != ?
                AND rh1.rating >= 4
                AND rh2.rating >= 4
            """, (user_id, user_id))
            
            similar_users = cursor.fetchone()[0]
            if similar_users > 0:
                score += similar_users * 0.5
            
            recommendations.append((book_id, title, author, genre, score))
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x[4], reverse=True)
        
        print(f"\n✓ Generated {len(recommendations)} recommendations")
        print(f"  Returning top {limit}")
        
        return recommendations[:limit]
    
    def find_similar_books(self, book_id, limit=5):
        """
        Find books similar to a given book
        
        Args:
            book_id: Book's ID
            limit: Number of similar books to return
        
        Returns:
            list: List of similar books
        """
        cursor = self.db.conn.cursor()
        
        # Get the target book's details
        cursor.execute("""
            SELECT genre, author, age_group
            FROM books
            WHERE book_id = ?
        """, (book_id,))
        
        result = cursor.fetchone()
        if not result:
            return []
        
        target_genre, target_author, target_age = result
        
        # Find similar books
        cursor.execute("""
            SELECT b.book_id, b.title, b.author, b.genre,
                   CASE 
                       WHEN b.genre = ? THEN 3
                       ELSE 0
                   END +
                   CASE
                       WHEN b.author = ? THEN 2
                       ELSE 0
                   END as similarity_score
            FROM books b
            WHERE b.book_id != ?
            AND b.age_group = ?
            AND b.available = 1
            ORDER BY similarity_score DESC
            LIMIT ?
        """, (target_genre, target_author, book_id, target_age, limit))
        
        return cursor.fetchall()
    
    def get_trending_books(self, community_name, days=30, limit=5):
        """
        Get trending books (most borrowed recently)
        
        Args:
            community_name: Name of the community
            days: Number of days to look back
            limit: Number of books to return
        
        Returns:
            list: List of trending books
        """
        from datetime import datetime, timedelta
        
        cursor = self.db.conn.cursor()
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT b.book_id, b.title, b.author, COUNT(*) as borrow_count
            FROM borrowing_records br
            JOIN books b ON br.book_id = b.book_id
            JOIN users u ON b.owner_id = u.user_id
            WHERE u.community_name = ?
            AND br.borrow_date >= ?
            GROUP BY b.book_id
            ORDER BY borrow_count DESC
            LIMIT ?
        """, (community_name, cutoff_date, limit))
        
        return cursor.fetchall()
    
    def recommend_by_genre(self, user_id, genre, limit=5):
        """
        Recommend books from a specific genre
        
        Args:
            user_id: User's ID
            genre: Genre to filter by
            limit: Number of recommendations
        
        Returns:
            list: List of books in the genre
        """
        cursor = self.db.conn.cursor()
        
        # Get user's community and age
        cursor.execute("""
            SELECT community_name, age FROM users WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        if not result:
            return []
        
        community, age = result
        
        # Determine age group
        if age <= 8:
            age_group = '5-8'
        elif age <= 12:
            age_group = '9-12'
        elif age <= 16:
            age_group = '13-16'
        else:
            age_group = '16+'
        
        # Get books in the genre
        cursor.execute("""
            SELECT b.book_id, b.title, b.author, b.genre, 
                   COALESCE(AVG(rh.rating), 3.0) as avg_rating
            FROM books b
            JOIN users u ON b.owner_id = u.user_id
            LEFT JOIN reading_history rh ON b.book_id = rh.book_id
            WHERE u.community_name = ?
            AND b.genre = ?
            AND b.age_group = ?
            AND b.available = 1
            AND b.book_id NOT IN (
                SELECT book_id FROM reading_history WHERE user_id = ?
            )
            GROUP BY b.book_id
            ORDER BY avg_rating DESC
            LIMIT ?
        """, (community, genre, age_group, user_id, limit))
        
        return cursor.fetchall()


if __name__ == "__main__":
    from database import BookSharingDatabase
    from user_manager import UserManager
    from book_manager import BookManager
    
    # Test recommendation engine
    print("Testing Recommendation Engine...")
    db = BookSharingDatabase()
    user_mgr = UserManager(db)
    book_mgr = BookManager(db)
    recommender = RecommendationEngine(db)
    
    # Create test data
    parent_id = user_mgr.register_parent(
        "Test Parent", "test@email.com", "1234567890",
        "Test Community", "monthly"
    )
    
    child_id = user_mgr.register_child("Test Child", parent_id, 10)
    
    # Add some books
    book1 = book_mgr.add_book(
        "Harry Potter", "J.K. Rowling", "Fantasy",
        "9-12", parent_id
    )
    
    book2 = book_mgr.add_book(
        "Percy Jackson", "Rick Riordan", "Fantasy",
        "9-12", parent_id
    )
    
    # Get recommendations
    recommendations = recommender.recommend_books(child_id, limit=3)
    
    print(f"\n✓ Recommendations:")
    for rec in recommendations:
        print(f"  - {rec[1]} by {rec[2]} (Score: {rec[4]:.2f})")
    
    db.close()