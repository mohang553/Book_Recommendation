"""
user_manager.py
Manages user registration, authentication, and subscriptions
"""

from datetime import datetime, timedelta

class UserManager:
    """Manages user registration, subscription, etc."""
    
    def __init__(self, db):
        self.db = db
    
    def register_parent(self, name, email, phone, community_name, subscription_type='monthly'):
        """
        Register a new parent
        
        Args:
            name: Parent's full name
            email: Email address
            phone: Phone number
            community_name: Name of gated community
            subscription_type: 'monthly' or 'annual'
        
        Returns:
            user_id: ID of newly created parent
        """
        cursor = self.db.conn.cursor()
        
        # Calculate subscription expiry
        if subscription_type == 'monthly':
            expiry = datetime.now() + timedelta(days=30)
        else:  # annual
            expiry = datetime.now() + timedelta(days=365)
        
        try:
            cursor.execute("""
                INSERT INTO users (name, email, phone, community_name, user_type, 
                                 created_date, subscription_type, subscription_expiry)
                VALUES (?, ?, ?, ?, 'parent', ?, ?, ?)
            """, (name, email, phone, community_name, 
                  datetime.now().strftime('%Y-%m-%d'),
                  subscription_type, expiry.strftime('%Y-%m-%d')))
            
            self.db.conn.commit()
            print(f"✓ Parent registered: {name} ({email})")
            return cursor.lastrowid
        
        except Exception as e:
            print(f"✗ Error registering parent: {e}")
            return None
    
    def register_child(self, name, parent_id, age):
        """
        Register a child under a parent
        
        Args:
            name: Child's name
            parent_id: Parent's user_id
            age: Child's age
        
        Returns:
            user_id: ID of newly created child
        """
        cursor = self.db.conn.cursor()
        
        # Get parent's community
        cursor.execute("SELECT community_name FROM users WHERE user_id = ?", (parent_id,))
        result = cursor.fetchone()
        
        if not result:
            print(f"✗ Parent with ID {parent_id} not found")
            return None
        
        community = result[0]
        
        try:
            cursor.execute("""
                INSERT INTO users (name, user_type, parent_id, age, community_name, created_date)
                VALUES (?, 'child', ?, ?, ?, ?)
            """, (name, parent_id, age, community, datetime.now().strftime('%Y-%m-%d')))
            
            child_id = cursor.lastrowid
            
            # Initialize stats for the child
            cursor.execute("""
                INSERT INTO user_stats (user_id, badges)
                VALUES (?, ?)
            """, (child_id, '[]'))
            
            self.db.conn.commit()
            print(f"✓ Child registered: {name} (Age: {age})")
            return child_id
        
        except Exception as e:
            print(f"✗ Error registering child: {e}")
            return None
    
    def check_subscription(self, user_id):
        """Check if user's subscription is active"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT subscription_expiry FROM users WHERE user_id = ?
        """, (user_id,))
        
        expiry = cursor.fetchone()
        if expiry and expiry[0]:
            expiry_date = datetime.strptime(expiry[0], '%Y-%m-%d')
            is_active = datetime.now() < expiry_date
            
            if is_active:
                days_left = (expiry_date - datetime.now()).days
                print(f"✓ Subscription active ({days_left} days remaining)")
            else:
                print("✗ Subscription expired")
            
            return is_active
        
        return False


if __name__ == "__main__":
    from database import BookSharingDatabase
    
    print("Testing User Manager...")
    db = BookSharingDatabase()
    user_mgr = UserManager(db)
    
    parent_id = user_mgr.register_parent(
        "Test Parent", "test@email.com", "1234567890",
        "Test Community", "monthly"
    )
    
    if parent_id:
        child_id = user_mgr.register_child("Test Child", parent_id, 10)
        user_mgr.check_subscription(parent_id)
    
    db.close()