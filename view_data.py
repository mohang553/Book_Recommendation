"""
view_data.py
Tool to view and analyze data in the database
"""

import sqlite3
from datetime import datetime

class DataViewer:
    """View and analyze database contents"""
    
    def __init__(self, db_name="book_sharing.db"):
        try:
            self.conn = sqlite3.connect(db_name)
            print(f"✓ Connected to database: {db_name}\n")
        except Exception as e:
            print(f"✗ Error connecting to database: {e}")
            self.conn = None
    
    def show_all_users(self):
        """Display all users (parents and children)"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        
        print("\n" + "=" * 100)
        print("ALL USERS")
        print("=" * 100)
        
        cursor.execute("""
            SELECT user_id, name, email, community_name, user_type, age, 
                   subscription_type, subscription_expiry
            FROM users
            ORDER BY user_type, user_id
        """)
        
        results = cursor.fetchall()
        
        if not results:
            print("No users found in database.")
            return
        
        print(f"\n{'ID':<5} {'Name':<20} {'Email':<25} {'Community':<20} {'Type':<8} {'Age':<5} {'Subscription':<15}")
        print("-" * 100)
        
        for row in results:
            user_id, name, email, community, user_type, age, sub_type, expiry = row
            age_str = str(age) if age else '-'
            sub_str = sub_type if sub_type else '-'
            print(f"{user_id:<5} {name:<20} {email or '-':<25} {community:<20} {user_type:<8} {age_str:<5} {sub_str:<15}")
        
        print(f"\nTotal Users: {len(results)}")
    
    def show_all_books(self):
        """Display all books in the catalog"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        
        print("\n" + "=" * 120)
        print("ALL BOOKS")
        print("=" * 120)
        
        cursor.execute("""
            SELECT b.book_id, b.title, b.author, b.genre, b.age_group, 
                   b.condition, b.available, u.name as owner_name
            FROM books b
            JOIN users u ON b.owner_id = u.user_id
            ORDER BY b.book_id
        """)
        
        results = cursor.fetchall()
        
        if not results:
            print("No books found in database.")
            return
        
        print(f"\n{'ID':<5} {'Title':<35} {'Author':<20} {'Genre':<12} {'Age':<8} {'Status':<12} {'Owner':<20}")
        print("-" * 120)
        
        for row in results:
            book_id, title, author, genre, age_group, condition, available, owner = row
            status = "Available" if available else "Borrowed"
            print(f"{book_id:<5} {title:<35} {author:<20} {genre:<12} {age_group:<8} {status:<12} {owner:<20}")
        
        print(f"\nTotal Books: {len(results)}")
        print(f"Available: {sum(1 for r in results if r[6] == 1)}")
        print(f"Borrowed: {sum(1 for r in results if r[6] == 0)}")
    
    def show_borrowing_history(self):
        """Display borrowing history"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        
        print("\n" + "=" * 120)
        print("BORROWING HISTORY")
        print("=" * 120)
        
        cursor.execute("""
            SELECT b.title, u.name as borrower, br.borrow_date, 
                   br.due_date, br.return_date, br.status
            FROM borrowing_records br
            JOIN books b ON br.book_id = b.book_id
            JOIN users u ON br.borrower_id = u.user_id
            ORDER BY br.borrow_date DESC
        """)
        
        results = cursor.fetchall()
        
        if not results:
            print("No borrowing records found.")
            return
        
        print(f"\n{'Book Title':<35} {'Borrower':<20} {'Borrowed':<12} {'Due':<12} {'Returned':<12} {'Status':<10}")
        print("-" * 120)
        
        for row in results:
            title, borrower, borrow_date, due_date, return_date, status = row
            return_str = return_date if return_date else '-'
            print(f"{title:<35} {borrower:<20} {borrow_date:<12} {due_date:<12} {return_str:<12} {status:<10}")
        
        print(f"\nTotal Records: {len(results)}")
    
    def show_reading_stats(self):
        """Display reading statistics for all children"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        
        print("\n" + "=" * 100)
        print("READING STATISTICS")
        print("=" * 100)
        
        cursor.execute("""
            SELECT u.name, us.total_books_read, us.current_streak, 
                   us.longest_streak, us.total_points, us.last_activity_date
            FROM user_stats us
            JOIN users u ON us.user_id = u.user_id
            ORDER BY us.total_points DESC
        """)
        
        results = cursor.fetchall()
        
        if not results:
            print("No reading statistics found.")
            return
        
        print(f"\n{'Name':<20} {'Books':<8} {'Streak':<10} {'Longest':<10} {'Points':<10} {'Last Activity':<15}")
        print("-" * 100)
        
        for row in results:
            name, books, streak, longest, points, last_activity = row
            last_str = last_activity if last_activity else '-'
            print(f"{name:<20} {books:<8} {streak:<10} {longest:<10} {points:<10} {last_str:<15}")
        
        print(f"\nTotal Readers: {len(results)}")
    
    def show_reviews(self):
        """Display all book reviews"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        
        print("\n" + "=" * 120)
        print("BOOK REVIEWS")
        print("=" * 120)
        
        cursor.execute("""
            SELECT b.title, u.name as reviewer, rh.rating, rh.review, rh.completed_date
            FROM reading_history rh
            JOIN books b ON rh.book_id = b.book_id
            JOIN users u ON rh.user_id = u.user_id
            WHERE rh.review IS NOT NULL
            ORDER BY rh.completed_date DESC
        """)
        
        results = cursor.fetchall()
        
        if not results:
            print("No reviews found.")
            return
        
        for i, (title, reviewer, rating, review, date) in enumerate(results, 1):
            print(f"\n{i}. {title}")
            print(f"   Reviewer: {reviewer} | Rating: {rating}/5 ⭐ | Date: {date}")
            print(f"   Review: {review}")
        
        print(f"\nTotal Reviews: {len(results)}")
    
    def show_community_stats(self, community_name):
        """Display statistics for a specific community"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        
        print("\n" + "=" * 100)
        print(f"COMMUNITY STATISTICS: {community_name}")
        print("=" * 100)
        
        # Total users
        cursor.execute("""
            SELECT COUNT(*) FROM users WHERE community_name = ?
        """, (community_name,))
        total_users = cursor.fetchone()[0]
        
        # Total parents
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE community_name = ? AND user_type = 'parent'
        """, (community_name,))
        total_parents = cursor.fetchone()[0]
        
        # Total children
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE community_name = ? AND user_type = 'child'
        """, (community_name,))
        total_children = cursor.fetchone()[0]
        
        # Total books
        cursor.execute("""
            SELECT COUNT(*) FROM books b
            JOIN users u ON b.owner_id = u.user_id
            WHERE u.community_name = ?
        """, (community_name,))
        total_books = cursor.fetchone()[0]
        
        # Total borrows
        cursor.execute("""
            SELECT COUNT(*) FROM borrowing_records br
            JOIN users u ON br.borrower_id = u.user_id
            WHERE u.community_name = ?
        """, (community_name,))
        total_borrows = cursor.fetchone()[0]
        
        # Active subscriptions
        cursor.execute("""
            SELECT COUNT(*) FROM users
            WHERE community_name = ? 
            AND user_type = 'parent'
            AND subscription_expiry >= date('now')
        """, (community_name,))
        active_subs = cursor.fetchone()[0]
        
        print(f"\n📊 Overview:")
        print(f"  Total Users: {total_users} ({total_parents} parents, {total_children} children)")
        print(f"  Total Books: {total_books}")
        print(f"  Total Borrows: {total_borrows}")
        print(f"  Active Subscriptions: {active_subs}/{total_parents}")
        
        # Most popular genre
        cursor.execute("""
            SELECT b.genre, COUNT(*) as count
            FROM borrowing_records br
            JOIN books b ON br.book_id = b.book_id
            JOIN users u ON br.borrower_id = u.user_id
            WHERE u.community_name = ?
            GROUP BY b.genre
            ORDER BY count DESC
            LIMIT 1
        """, (community_name,))
        
        popular_genre = cursor.fetchone()
        if popular_genre:
            print(f"\n📚 Most Popular Genre: {popular_genre[0]} ({popular_genre[1]} borrows)")
        
        # Top reader
        cursor.execute("""
            SELECT u.name, us.total_books_read, us.total_points
            FROM user_stats us
            JOIN users u ON us.user_id = u.user_id
            WHERE u.community_name = ?
            ORDER BY us.total_points DESC
            LIMIT 1
        """, (community_name,))
        
        top_reader = cursor.fetchone()
        if top_reader:
            print(f"🏆 Top Reader: {top_reader[0]} ({top_reader[1]} books, {top_reader[2]} points)")
    
    def show_all_communities(self):
        """Display all communities"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        
        print("\n" + "=" * 100)
        print("ALL COMMUNITIES")
        print("=" * 100)
        
        cursor.execute("""
            SELECT community_name, COUNT(*) as user_count
            FROM users
            WHERE community_name IS NOT NULL
            GROUP BY community_name
            ORDER BY user_count DESC
        """)
        
        results = cursor.fetchall()
        
        if not results:
            print("No communities found.")
            return
        
        print(f"\n{'Community Name':<30} {'Total Users':<15}")
        print("-" * 100)
        
        for community, count in results:
            print(f"{community:<30} {count:<15}")
        
        print(f"\nTotal Communities: {len(results)}")
    
    def export_to_csv(self, table_name, filename):
        """Export a table to CSV file"""
        if not self.conn:
            return
        
        import csv
        
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        
        rows = cursor.fetchall()
        
        if not rows:
            print(f"No data found in table: {table_name}")
            return
        
        # Get column names
        column_names = [description[0] for description in cursor.description]
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(column_names)
            writer.writerows(rows)
        
        print(f"✓ Exported {len(rows)} rows from {table_name} to {filename}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("\n✓ Database connection closed")


def main():
    """Main menu for data viewer"""
    
    print("\n" + "=" * 70)
    print("BOOK SHARING PLATFORM - DATABASE VIEWER")
    print("=" * 70)
    
    viewer = DataViewer()
    
    if not viewer.conn:
        print("Could not connect to database. Make sure book_sharing.db exists.")
        print("Run main.py first to create the database.")
        return
    
    try:
        while True:
            print("\n" + "-" * 70)
            print("MENU OPTIONS:")
            print("-" * 70)
            print("1.  View All Users")
            print("2.  View All Books")
            print("3.  View Borrowing History")
            print("4.  View Reading Statistics")
            print("5.  View Book Reviews")
            print("6.  View All Communities")
            print("7.  View Community Statistics")
            print("8.  Export Table to CSV")
            print("0.  Exit")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '0':
                print("\n👋 Goodbye!")
                break
            elif choice == '1':
                viewer.show_all_users()
            elif choice == '2':
                viewer.show_all_books()
            elif choice == '3':
                viewer.show_borrowing_history()
            elif choice == '4':
                viewer.show_reading_stats()
            elif choice == '5':
                viewer.show_reviews()
            elif choice == '6':
                viewer.show_all_communities()
            elif choice == '7':
                community = input("\nEnter community name: ").strip()
                viewer.show_community_stats(community)
            elif choice == '8':
                print("\nAvailable tables:")
                print("  • users")
                print("  • books")
                print("  • borrowing_records")
                print("  • reading_history")
                print("  • user_stats")
                table = input("\nEnter table name: ").strip()
                filename = input("Enter output filename (e.g., data.csv): ").strip()
                viewer.export_to_csv(table, filename)
            else:
                print("\n⚠️  Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted by user")
    finally:
        viewer.close()


if __name__ == "__main__":
    main()