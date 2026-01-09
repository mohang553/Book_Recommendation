"""
test_recommendations_auto.py
Automated script to test the recommendation engine
Run this after starting the API server
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_step(text):
    print(f"\n>>> {text}")

def print_result(response):
    if response.status_code in [200, 201]:
        print("✅ SUCCESS")
        return response.json()
    else:
        print(f"❌ FAILED: {response.status_code}")
        print(response.text)
        return None

def test_recommendation_engine():
    print_header("🎯 AUTOMATED RECOMMENDATION ENGINE TEST")
    
    # Step 1: Register Parents
    print_step("STEP 1: Registering Parents")
    
    parent1_data = {
        "name": "Test Parent 1",
        "email": "parent1@test.com",
        "phone": "1111111111",
        "community_name": "Test Community",
        "subscription_type": "annual"
    }
    
    response = requests.post(f"{API_BASE}/api/parents/register", json=parent1_data)
    parent1 = print_result(response)
    if not parent1:
        return
    parent1_id = parent1['user_id']
    print(f"   Parent 1 ID: {parent1_id}")
    
    # Step 2: Register Children
    print_step("STEP 2: Registering Children")
    
    children_data = [
        {"name": "Alice (Fantasy Lover)", "parent_id": parent1_id, "age": 10},
        {"name": "Bob (Adventure Lover)", "parent_id": parent1_id, "age": 11},
    ]
    
    child_ids = []
    for child_data in children_data:
        response = requests.post(f"{API_BASE}/api/children/register", json=child_data)
        child = print_result(response)
        if child:
            child_ids.append(child['user_id'])
            print(f"   {child_data['name']} ID: {child['user_id']}")
    
    child1_id, child2_id = child_ids
    
    # Step 3: Add Books
    print_step("STEP 3: Adding Books to Library")
    
    books_data = [
        # Fantasy Books
        {"title": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", 
         "genre": "Fantasy", "age_group": "9-12", "owner_id": parent1_id},
        {"title": "Percy Jackson: The Lightning Thief", "author": "Rick Riordan", 
         "genre": "Fantasy", "age_group": "9-12", "owner_id": parent1_id},
        {"title": "The Hobbit", "author": "J.R.R. Tolkien", 
         "genre": "Fantasy", "age_group": "9-12", "owner_id": parent1_id},
        
        # Adventure Books
        {"title": "Treasure Island", "author": "Robert Louis Stevenson", 
         "genre": "Adventure", "age_group": "9-12", "owner_id": parent1_id},
        {"title": "The Secret Seven", "author": "Enid Blyton", 
         "genre": "Adventure", "age_group": "9-12", "owner_id": parent1_id},
        {"title": "Hatchet", "author": "Gary Paulsen", 
         "genre": "Adventure", "age_group": "9-12", "owner_id": parent1_id},
        
        # Fiction Books
        {"title": "Charlotte's Web", "author": "E.B. White", 
         "genre": "Fiction", "age_group": "9-12", "owner_id": parent1_id},
        {"title": "Matilda", "author": "Roald Dahl", 
         "genre": "Fiction", "age_group": "9-12", "owner_id": parent1_id},
    ]
    
    book_ids = []
    for book_data in books_data:
        response = requests.post(f"{API_BASE}/api/books/add", json=book_data)
        book = print_result(response)
        if book:
            book_ids.append(book['book_id'])
            print(f"   Added: {book_data['title']} (ID: {book['book_id']})")
    
    # Step 4: Create Reading History for Alice (Fantasy Lover)
    print_step("STEP 4: Alice Reads and Rates Fantasy Books")
    
    # Alice reads Harry Potter
    print("   📖 Alice borrows Harry Potter...")
    borrow_data = {"book_id": book_ids[0], "borrower_id": child1_id, "days": 14}
    requests.post(f"{API_BASE}/api/borrow", json=borrow_data)
    
    time.sleep(0.5)
    
    print("   ⭐ Alice returns with 5-star rating...")
    return_data = {
        "book_id": book_ids[0], 
        "borrower_id": child1_id, 
        "rating": 5,
        "review": "Absolutely magical! Best book ever!"
    }
    response = requests.post(f"{API_BASE}/api/return", json=return_data)
    print_result(response)
    
    # Alice reads Percy Jackson
    print("   📖 Alice borrows Percy Jackson...")
    borrow_data = {"book_id": book_ids[1], "borrower_id": child1_id, "days": 14}
    requests.post(f"{API_BASE}/api/borrow", json=borrow_data)
    
    time.sleep(0.5)
    
    print("   ⭐ Alice returns with 5-star rating...")
    return_data = {
        "book_id": book_ids[1], 
        "borrower_id": child1_id, 
        "rating": 5,
        "review": "Greek mythology is so cool!"
    }
    response = requests.post(f"{API_BASE}/api/return", json=return_data)
    print_result(response)
    
    # Step 5: Create Reading History for Bob (Adventure Lover)
    print_step("STEP 5: Bob Reads and Rates Adventure Books")
    
    # Bob reads Treasure Island
    print("   📖 Bob borrows Treasure Island...")
    borrow_data = {"book_id": book_ids[3], "borrower_id": child2_id, "days": 14}
    requests.post(f"{API_BASE}/api/borrow", json=borrow_data)
    
    time.sleep(0.5)
    
    print("   ⭐ Bob returns with 5-star rating...")
    return_data = {
        "book_id": book_ids[3], 
        "borrower_id": child2_id, 
        "rating": 5,
        "review": "Pirates are awesome!"
    }
    response = requests.post(f"{API_BASE}/api/return", json=return_data)
    print_result(response)
    
    # Bob reads Secret Seven
    print("   📖 Bob borrows The Secret Seven...")
    borrow_data = {"book_id": book_ids[4], "borrower_id": child2_id, "days": 14}
    requests.post(f"{API_BASE}/api/borrow", json=borrow_data)
    
    time.sleep(0.5)
    
    print("   ⭐ Bob returns with 4-star rating...")
    return_data = {
        "book_id": book_ids[4], 
        "borrower_id": child2_id, 
        "rating": 4,
        "review": "Great mystery!"
    }
    response = requests.post(f"{API_BASE}/api/return", json=return_data)
    print_result(response)
    
    # Step 6: Test Recommendations for Alice
    print_step("STEP 6: Testing Recommendations for Alice (Fantasy Lover)")
    
    response = requests.get(f"{API_BASE}/api/recommendations/{child1_id}?limit=5")
    recommendations = print_result(response)
    
    if recommendations:
        print("\n   🎯 ALICE'S RECOMMENDATIONS:")
        print("   " + "-"*60)
        for rec in recommendations['recommendations']:
            print(f"   {rec['title']:<40} Genre: {rec['genre']:<12} Score: {rec['score']:.1f}")
        
        # Analyze results
        print("\n   📊 ANALYSIS:")
        fantasy_books = [r for r in recommendations['recommendations'] if r['genre'] == 'Fantasy']
        if fantasy_books:
            avg_fantasy_score = sum(r['score'] for r in fantasy_books) / len(fantasy_books)
            print(f"   ✅ Fantasy books found: {len(fantasy_books)}")
            print(f"   ✅ Average Fantasy score: {avg_fantasy_score:.1f}")
            if avg_fantasy_score > 8:
                print("   ✅ HIGH SCORES for Fantasy genre - WORKING CORRECTLY!")
            else:
                print("   ⚠️  Fantasy scores lower than expected")
        else:
            print("   ⚠️  No Fantasy books in recommendations (might be all read)")
    
    # Step 7: Test Recommendations for Bob
    print_step("STEP 7: Testing Recommendations for Bob (Adventure Lover)")
    
    response = requests.get(f"{API_BASE}/api/recommendations/{child2_id}?limit=5")
    recommendations = print_result(response)
    
    if recommendations:
        print("\n   🎯 BOB'S RECOMMENDATIONS:")
        print("   " + "-"*60)
        for rec in recommendations['recommendations']:
            print(f"   {rec['title']:<40} Genre: {rec['genre']:<12} Score: {rec['score']:.1f}")
        
        # Analyze results
        print("\n   📊 ANALYSIS:")
        adventure_books = [r for r in recommendations['recommendations'] if r['genre'] == 'Adventure']
        if adventure_books:
            avg_adventure_score = sum(r['score'] for r in adventure_books) / len(adventure_books)
            print(f"   ✅ Adventure books found: {len(adventure_books)}")
            print(f"   ✅ Average Adventure score: {avg_adventure_score:.1f}")
            if avg_adventure_score > 8:
                print("   ✅ HIGH SCORES for Adventure genre - WORKING CORRECTLY!")
            else:
                print("   ⚠️  Adventure scores lower than expected")
        else:
            print("   ⚠️  No Adventure books in recommendations (might be all read)")
    
    # Step 8: Test Similar Books
    print_step("STEP 8: Testing Similar Books Feature")
    
    response = requests.get(f"{API_BASE}/api/recommendations/similar/{book_ids[0]}?limit=3")
    similar = print_result(response)
    
    if similar:
        print("\n   📚 BOOKS SIMILAR TO 'Harry Potter':")
        print("   " + "-"*60)
        for book in similar['similar_books']:
            print(f"   {book['title']:<40} Score: {book['similarity_score']}")
    
    # Step 9: Test Trending Books
    print_step("STEP 9: Testing Trending Books")
    
    response = requests.get(f"{API_BASE}/api/recommendations/trending/Test Community?days=30&limit=5")
    trending = print_result(response)
    
    if trending:
        print("\n   🔥 TRENDING BOOKS:")
        print("   " + "-"*60)
        for book in trending['trending_books']:
            print(f"   {book['title']:<40} Borrows: {book['borrow_count']}")
    
    # Step 10: View User Stats
    print_step("STEP 10: Checking Gamification Stats")
    
    response = requests.get(f"{API_BASE}/api/gamification/stats/{child1_id}")
    stats = print_result(response)
    
    if stats:
        print(f"\n   👤 ALICE'S STATS:")
        print(f"   📚 Books Read: {stats['total_books_read']}")
        print(f"   ⚡ Points: {stats['total_points']}")
        print(f"   🔥 Streak: {stats['current_streak']} days")
        print(f"   🏆 Badges: {len(stats['badges'])}")
    
    # Step 11: Leaderboard
    print_step("STEP 11: Community Leaderboard")
    
    response = requests.get(f"{API_BASE}/api/gamification/leaderboard/Test Community?limit=10")
    leaderboard = print_result(response)
    
    if leaderboard:
        print("\n   🏆 LEADERBOARD:")
        print("   " + "-"*70)
        print(f"   {'Rank':<6} {'Name':<25} {'Books':<8} {'Points':<10} {'Streak':<10}")
        print("   " + "-"*70)
        for entry in leaderboard['leaderboard']:
            print(f"   {entry['rank']:<6} {entry['name']:<25} {entry['books_read']:<8} "
                  f"{entry['total_points']:<10} {entry['current_streak']:<10}")
    
    # Final Summary
    print_header("🎉 TEST COMPLETE - SUMMARY")
    print("\n✅ Recommendation Engine Test Results:")
    print(f"   • Created {len(book_ids)} books in library")
    print(f"   • Alice read 2 Fantasy books (both rated 5 stars)")
    print(f"   • Bob read 2 Adventure books (4-5 stars)")
    print(f"   • Generated personalized recommendations")
    print(f"   • Tested similar books feature")
    print(f"   • Checked trending books")
    print(f"   • Verified gamification stats")
    
    print("\n🎯 Expected Behavior:")
    print("   • Alice should see Fantasy books with HIGH scores (8-15)")
    print("   • Bob should see Adventure books with HIGH scores (8-15)")
    print("   • Both should see unread books from their preferred genres")
    print("   • Trending should show the 4 books that were borrowed")
    
    print("\n📖 Next Steps:")
    print("   • Check the scores in the recommendations above")
    print("   • Open http://localhost:8000/ to manually explore more")
    print("   • Add more books and create more diverse reading patterns")
    print("   • Test with more children to see collaborative filtering")
    
    print("\n" + "="*70)
    print("  Thank you for testing! 🚀")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        # Check if API is running
        print("Checking if API is running...")
        response = requests.get(f"{API_BASE}/health", timeout=2)
        if response.status_code == 200:
            print("✅ API is online!\n")
            time.sleep(1)
            test_recommendation_engine()
        else:
            print("❌ API returned unexpected status")
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API")
        print("   Make sure the API is running:")
        print("   1. Open a terminal")
        print("   2. Run: python api.py")
        print("   3. Wait for 'Uvicorn running on...'")
        print("   4. Then run this script again")
    except Exception as e:
        print(f"❌ ERROR: {e}")