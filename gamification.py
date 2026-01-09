"""
gamification.py
Gamification system to motivate kids - like Duolingo
"""

import json
from datetime import datetime

class GamificationSystem:
    """Motivates kids to read more - like Duolingo"""
    
    def __init__(self, db):
        self.db = db
        self.badges = {
            'first_book': {
                'name': 'First Steps',
                'description': 'Read your first book!',
                'icon': '📖'
            },
            'week_streak': {
                'name': 'Week Warrior',
                'description': '7-day reading streak',
                'icon': '🔥'
            },
            'month_streak': {
                'name': 'Monthly Master',
                'description': '30-day reading streak',
                'icon': '⭐'
            },
            'bookworm': {
                'name': 'Bookworm',
                'description': 'Read 10 books',
                'icon': '🐛'
            },
            'scholar': {
                'name': 'Scholar',
                'description': 'Read 25 books',
                'icon': '🎓'
            },
            'genius': {
                'name': 'Reading Genius',
                'description': 'Read 50 books',
                'icon': '🧠'
            }
        }
    
    def update_reading_stats(self, user_id):
        """Update user statistics after completing a book"""
        cursor = self.db.conn.cursor()
        
        cursor.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
        stats = cursor.fetchone()
        
        if not stats:
            print("✗ User stats not found")
            return None
        
        total_books = stats[1] + 1
        current_streak = stats[2]
        longest_streak = stats[3]
        total_points = stats[4]
        badges = json.loads(stats[5])
        last_activity = stats[6]
        
        if last_activity:
            last_date = datetime.strptime(last_activity, '%Y-%m-%d')
            today = datetime.now()
            days_diff = (today - last_date).days
            
            if days_diff == 1:
                current_streak += 1
            elif days_diff > 1:
                current_streak = 1
                print("  ⚠️  Streak broken! Starting fresh.")
        else:
            current_streak = 1
        
        if current_streak > longest_streak:
            longest_streak = current_streak
            print(f"  🏆 New longest streak: {longest_streak} days!")
        
        base_points = 10
        streak_bonus = current_streak * 2
        points_earned = base_points + streak_bonus
        total_points += points_earned
        
        old_badges = badges.copy()
        new_badges_list = self._check_badges(user_id, total_books, current_streak, badges)
        newly_earned = [b for b in new_badges_list if b not in old_badges]
        
        cursor.execute("""
            UPDATE user_stats 
            SET total_books_read = ?,
                current_streak = ?,
                longest_streak = ?,
                total_points = ?,
                badges = ?,
                last_activity_date = ?
            WHERE user_id = ?
        """, (total_books, current_streak, longest_streak, total_points,
              json.dumps(new_badges_list), datetime.now().strftime('%Y-%m-%d'), user_id))
        
        self.db.conn.commit()
        
        print(f"\n✓ Reading stats updated!")
        print(f"  📚 Total books: {total_books}")
        print(f"  ⚡ Points earned: {points_earned} (Total: {total_points})")
        print(f"  🔥 Current streak: {current_streak} days")
        
        if newly_earned:
            print(f"\n  🎉 NEW BADGES EARNED:")
            for badge_key in newly_earned:
                badge = self.badges[badge_key]
                print(f"     {badge['icon']} {badge['name']} - {badge['description']}")
        
        return {
            'points_earned': points_earned,
            'total_points': total_points,
            'new_badges': newly_earned,
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'total_books': total_books
        }
    
    def _check_badges(self, user_id, total_books, current_streak, current_badges):
        """Check and award new badges"""
        badges = current_badges.copy()
        
        if total_books >= 1 and 'first_book' not in badges:
            badges.append('first_book')
        
        if current_streak >= 7 and 'week_streak' not in badges:
            badges.append('week_streak')
        
        if current_streak >= 30 and 'month_streak' not in badges:
            badges.append('month_streak')
        
        if total_books >= 10 and 'bookworm' not in badges:
            badges.append('bookworm')
        
        if total_books >= 25 and 'scholar' not in badges:
            badges.append('scholar')
        
        if total_books >= 50 and 'genius' not in badges:
            badges.append('genius')
        
        return badges
    
    def get_leaderboard(self, community_name, limit=10):
        """Get top readers in the community"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT u.name, us.total_books_read, us.total_points, 
                   us.current_streak, us.longest_streak
            FROM user_stats us
            JOIN users u ON us.user_id = u.user_id
            WHERE u.community_name = ? AND u.user_type = 'child'
            ORDER BY us.total_points DESC
            LIMIT ?
        """, (community_name, limit))
        
        results = cursor.fetchall()
        
        print(f"\n🏆 LEADERBOARD - {community_name}")
        print("=" * 70)
        print(f"{'Rank':<6} {'Name':<20} {'Books':<8} {'Points':<10} {'Streak':<10}")
        print("-" * 70)
        
        for rank, (name, books, points, streak, longest) in enumerate(results, 1):
            print(f"{rank:<6} {name:<20} {books:<8} {points:<10} {streak} days")
        
        return results
    
    def get_user_stats(self, user_id):
        """Get complete statistics for a user"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT us.*, u.name
            FROM user_stats us
            JOIN users u ON us.user_id = u.user_id
            WHERE us.user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        if result:
            badges = json.loads(result[5])
            badge_details = [self.badges[b] for b in badges if b in self.badges]
            
            return {
                'user_id': result[0],
                'name': result[7],
                'total_books_read': result[1],
                'current_streak': result[2],
                'longest_streak': result[3],
                'total_points': result[4],
                'badges': badge_details,
                'last_activity_date': result[6]
            }
        return None