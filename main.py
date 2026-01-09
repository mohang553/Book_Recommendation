"""
main.py
Main application entry point - Runs the complete system demo
"""

from database import BookSharingDatabase
from user_manager import UserManager
from book_manager import BookManager
from recommendation_engine import RecommendationEngine
from gamification import GamificationSystem

class BookSharingPlatform:
    """Main application that ties everything together"""
    
    def __init__(self):
        print("\n" + "=" * 70)
        print("BOOK SHARING PLATFORM - INITIALIZING")
        print("=" * 70)
        
        self.db = BookSharingDatabase()
        self.user_mgr = UserManager(self.db)
        self.book_mgr = BookManager(self.db)
        self.recommender = RecommendationEngine(self.db)
        self.gamification = GamificationSystem(self.db)
        
        print("✓ All modules loaded successfully!\n")
    
    def run_demo(self):
        """Run a complete demonstration of the system"""
        
        print("\n" + "=" * 70)
        print("RUNNING COMPLETE SYSTEM DEMO")
        print("=" * 70)
        
        # Step 1: Register Parents
        print("\n【STEP 1】 REGISTERING PARENTS")
        print("-" * 70)
        
        parent1 = self.user_mgr.register_parent(
            "Rajesh Kumar", "rajesh@email.com", "9876543210",
            "Green Valley Apartments", "annual"
        )
        
        parent2 = self.user_mgr.register_parent(
            "Priya Sharma", "priya@email.com", "9876543211",
            "Green Valley Apartments", "monthly"
        )
        
        parent3 = self.user_mgr.register_parent(
            "Amit Patel", "amit@email.com", "9876543212",
            "Green Valley Apartments", "annual"
        )
        
        # Step 2: Register Children
        print("\n【STEP 2】 REGISTERING CHILDREN")
        print("-" * 70)
        
        child1 = self.user_mgr.register_child("Aarav Kumar", parent1, 10)
        child2 = self.user_mgr.register_child("Diya Sharma", parent2, 9)
        child3 = self.user_mgr.register_child("Rohan Patel", parent3, 11)
        
        # Step 3: Add Books
        print("\n【STEP 3】 ADDING BOOKS TO COMMUNITY LIBRARY")
        print("-" * 70)
        
        books = [
            ("Harry Potter and the Philosopher's Stone", "J.K. Rowling", "Fantasy", "9-12", parent1),
            ("The Secret Seven", "Enid Blyton", "Adventure", "9-12", parent2),
            ("Charlotte's Web", "E.B. White", "Fiction", "9-12", parent1),
            ("Percy Jackson: The Lightning Thief", "Rick Riordan", "Fantasy", "9-12", parent3),
            ("Matilda", "Roald Dahl", "Fiction", "9-12", parent2),
            ("The Hobbit", "J.R.R. Tolkien", "Fantasy", "9-12", parent3),
        ]
        
        book_ids = []
        for title, author, genre, age_group, owner in books:
            book_id = self.book_mgr.add_book(title, author, genre, age_group, owner)
            book_ids.append(book_id)
        
        # Step 4: Browse Books
        print("\n【STEP 4】 BROWSING AVAILABLE BOOKS")
        print("-" * 70)
        
        available_books = self.book_mgr.search_books("Green Valley Apartments", age_group="9-12")
        
        print(f"\n📚 Available Books:")
        for i, book in enumerate(available_books, 1):
            print(f"  {i}. {book[1]} by {book[2]} ({book[3]})")
        
        # Step 5: Borrow Books
        print("\n【STEP 5】 BORROWING BOOKS")
        print("-" * 70)
        
        self.book_mgr.borrow_book(book_ids[0], child1)
        self.book_mgr.borrow_book(book_ids[3], child2)
        
        # Step 6: Return Books
        print("\n【STEP 6】 RETURNING BOOKS WITH RATINGS")
        print("-" * 70)
        
        self.book_mgr.return_book(book_ids[0], child1, rating=5, 
                                 review="Amazing book! Loved it!")
        self.gamification.update_reading_stats(child1)
        
        self.book_mgr.return_book(book_ids[3], child2, rating=5,
                                 review="So exciting!")
        self.gamification.update_reading_stats(child2)
        
        # Step 7: Recommendations
        print("\n【STEP 7】 PERSONALIZED RECOMMENDATIONS")
        print("-" * 70)
        
        print(f"\n🎯 Recommendations for Aarav:")
        recommendations = self.recommender.recommend_books(child1, limit=3)
        
        for i, (book_id, title, author, genre, score) in enumerate(recommendations, 1):
            print(f"  {i}. {title} by {author} (Score: {score:.2f})")
        
        # Step 8: Leaderboard
        print("\n【STEP 8】 COMMUNITY LEADERBOARD")
        print("-" * 70)
        
        self.gamification.get_leaderboard("Green Valley Apartments")
        
        # Final Summary
        print("\n" + "=" * 70)
        print("DEMO COMPLETED SUCCESSFULLY! ✨")
        print("=" * 70)
        print("\n💾 Database saved as: book_sharing.db")
        print("📱 Ready to build web/mobile interface!")
    
    def close(self):
        """Close database connection"""
        self.db.close()


def main():
    """Main entry point"""
    
    print("\n" + "=" * 70)
    print("WELCOME TO BOOK SHARING PLATFORM")
    print("=" * 70)
    
    platform = BookSharingPlatform()
    
    try:
        print("\nChoose mode:")
        print("1. Run Demo (Recommended)")
        print("2. Exit")
        
        choice = input("\nEnter your choice (1/2): ").strip()
        
        if choice == '1':
            platform.run_demo()
        else:
            print("\nGoodbye!")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted")
    except Exception as e:
        print(f"\n✗ Error: {e}")
    finally:
        platform.close()


if __name__ == "__main__":
    main()