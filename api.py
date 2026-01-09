"""
api.py
FastAPI application for Book Sharing Platform
Provides RESTful API endpoints with interactive Swagger UI
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from contextlib import asynccontextmanager
import json

from database import BookSharingDatabase
from user_manager import UserManager
from book_manager import BookManager
from recommendation_engine import RecommendationEngine
from gamification import GamificationSystem

# Global variables for database and managers
db = None
user_mgr = None
book_mgr = None
recommender = None
gamification = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db, user_mgr, book_mgr, recommender, gamification
    db = BookSharingDatabase()
    user_mgr = UserManager(db)
    book_mgr = BookManager(db)
    recommender = RecommendationEngine(db)
    gamification = GamificationSystem(db)
    print("🚀 Book Sharing Platform API Started!")
    print("📖 Swagger UI available at: http://localhost:8000/")
    print("📚 ReDoc available at: http://localhost:8000/redoc")
    
    yield
    
    # Shutdown
    db.close()
    print("👋 API Shutdown Complete")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Book Sharing Platform API",
    description="Community-based book sharing and recommendation system with gamification",
    version="1.0.0",
    docs_url="/",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Models for Request/Response
class ParentRegistration(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Rajesh Kumar",
                "email": "rajesh@email.com",
                "phone": "9876543210",
                "community_name": "Green Valley Apartments",
                "subscription_type": "annual"
            }
        }
    )
    
    name: str
    email: str
    phone: str
    community_name: str
    subscription_type: str = "monthly"


class ChildRegistration(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Aarav Kumar",
                "parent_id": 1,
                "age": 10
            }
        }
    )
    
    name: str
    parent_id: int
    age: int


class BookAddition(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Harry Potter and the Philosopher's Stone",
                "author": "J.K. Rowling",
                "genre": "Fantasy",
                "age_group": "9-12",
                "owner_id": 1,
                "condition": "good",
                "book_type": "story"
            }
        }
    )
    
    title: str
    author: str
    genre: str
    age_group: str
    owner_id: int
    condition: str = "good"
    book_type: str = "story"


class BorrowRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "book_id": 1,
                "borrower_id": 2,
                "days": 14
            }
        }
    )
    
    book_id: int
    borrower_id: int
    days: int = 14


class ReturnRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "book_id": 1,
                "borrower_id": 2,
                "rating": 5,
                "review": "Amazing book! Loved it!"
            }
        }
    )
    
    book_id: int
    borrower_id: int
    rating: Optional[int] = None
    review: Optional[str] = None


# API Endpoints

@app.get("/health")
async def health_check():
    """Check API health status"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# User Management Endpoints
@app.post("/api/parents/register", tags=["Users"])
async def register_parent(parent: ParentRegistration):
    """Register a new parent user"""
    user_id = user_mgr.register_parent(
        parent.name,
        parent.email,
        parent.phone,
        parent.community_name,
        parent.subscription_type
    )
    
    if not user_id:
        raise HTTPException(status_code=400, detail="Failed to register parent")
    
    return {
        "success": True,
        "user_id": user_id,
        "message": f"Parent {parent.name} registered successfully"
    }


@app.post("/api/children/register", tags=["Users"])
async def register_child(child: ChildRegistration):
    """Register a new child user"""
    user_id = user_mgr.register_child(
        child.name,
        child.parent_id,
        child.age
    )
    
    if not user_id:
        raise HTTPException(status_code=400, detail="Failed to register child")
    
    return {
        "success": True,
        "user_id": user_id,
        "message": f"Child {child.name} registered successfully"
    }


@app.get("/api/users/{user_id}/subscription", tags=["Users"])
async def check_subscription(user_id: int):
    """Check user's subscription status"""
    is_active = user_mgr.check_subscription(user_id)
    
    cursor = db.conn.cursor()
    cursor.execute("""
        SELECT subscription_type, subscription_expiry 
        FROM users WHERE user_id = ?
    """, (user_id,))
    result = cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_id,
        "is_active": is_active,
        "subscription_type": result[0],
        "expiry_date": result[1]
    }


@app.get("/api/users", tags=["Users"])
async def get_all_users(
    community: Optional[str] = None,
    user_type: Optional[str] = None
):
    """Get all users with optional filters"""
    cursor = db.conn.cursor()
    
    query = "SELECT * FROM users WHERE 1=1"
    params = []
    
    if community:
        query += " AND community_name = ?"
        params.append(community)
    
    if user_type:
        query += " AND user_type = ?"
        params.append(user_type)
    
    cursor.execute(query, params)
    users = cursor.fetchall()
    
    return {
        "total": len(users),
        "users": [
            {
                "user_id": u[0],
                "name": u[1],
                "email": u[2],
                "community": u[4],
                "type": u[5],
                "age": u[7]
            }
            for u in users
        ]
    }


# Book Management Endpoints
@app.post("/api/books/add", tags=["Books"])
async def add_book(book: BookAddition):
    """Add a new book to the catalog"""
    book_id = book_mgr.add_book(
        book.title,
        book.author,
        book.genre,
        book.age_group,
        book.owner_id,
        book.condition,
        book.book_type
    )
    
    if not book_id:
        raise HTTPException(status_code=400, detail="Failed to add book")
    
    return {
        "success": True,
        "book_id": book_id,
        "message": f"Book '{book.title}' added successfully"
    }


@app.get("/api/books/search", tags=["Books"])
async def search_books(
    community_name: str,
    genre: Optional[str] = None,
    age_group: Optional[str] = None,
    available_only: bool = True,
    search_term: Optional[str] = None
):
    """Search for books in a community"""
    books = book_mgr.search_books(
        community_name,
        genre,
        age_group,
        available_only,
        search_term
    )
    
    return {
        "total": len(books),
        "books": [
            {
                "book_id": b[0],
                "title": b[1],
                "author": b[2],
                "genre": b[3],
                "age_group": b[4],
                "condition": b[5],
                "available": bool(b[6]),
                "owner_name": b[7],
                "book_type": b[8]
            }
            for b in books
        ]
    }


@app.get("/api/books/{book_id}", tags=["Books"])
async def get_book_details(book_id: int):
    """Get detailed information about a specific book"""
    cursor = db.conn.cursor()
    cursor.execute("""
        SELECT b.*, u.name as owner_name
        FROM books b
        JOIN users u ON b.owner_id = u.user_id
        WHERE b.book_id = ?
    """, (book_id,))
    
    book = cursor.fetchone()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return {
        "book_id": book[0],
        "title": book[1],
        "author": book[2],
        "genre": book[3],
        "age_group": book[4],
        "owner_id": book[5],
        "condition": book[6],
        "book_type": book[7],
        "available": bool(book[8]),
        "added_date": book[9],
        "owner_name": book[10]
    }


@app.get("/api/books/popular/{community_name}", tags=["Books"])
async def get_popular_books(community_name: str, limit: int = 10):
    """Get most popular books in a community"""
    books = book_mgr.get_popular_books(community_name, limit)
    
    return {
        "community": community_name,
        "total": len(books),
        "books": [
            {
                "title": b[0],
                "author": b[1],
                "borrow_count": b[2],
                "avg_rating": round(b[3], 2) if b[3] else None
            }
            for b in books
        ]
    }


# Borrowing Endpoints
@app.post("/api/borrow", tags=["Borrowing"])
async def borrow_book(request: BorrowRequest):
    """Borrow a book"""
    success, message = book_mgr.borrow_book(
        request.book_id,
        request.borrower_id,
        request.days
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {
        "success": True,
        "message": message
    }


@app.post("/api/return", tags=["Borrowing"])
async def return_book(request: ReturnRequest):
    """Return a borrowed book"""
    success = book_mgr.return_book(
        request.book_id,
        request.borrower_id,
        request.rating,
        request.review
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to return book")
    
    # Update gamification stats if rating provided
    if request.rating:
        stats = gamification.update_reading_stats(request.borrower_id)
    
    return {
        "success": True,
        "message": "Book returned successfully",
        "stats_updated": bool(request.rating)
    }


@app.get("/api/borrowing/history/{user_id}", tags=["Borrowing"])
async def get_borrowing_history(user_id: int):
    """Get borrowing history for a user"""
    cursor = db.conn.cursor()
    cursor.execute("""
        SELECT b.title, br.borrow_date, br.due_date, 
               br.return_date, br.status
        FROM borrowing_records br
        JOIN books b ON br.book_id = b.book_id
        WHERE br.borrower_id = ?
        ORDER BY br.borrow_date DESC
    """, (user_id,))
    
    records = cursor.fetchall()
    
    return {
        "user_id": user_id,
        "total_records": len(records),
        "history": [
            {
                "title": r[0],
                "borrow_date": r[1],
                "due_date": r[2],
                "return_date": r[3],
                "status": r[4]
            }
            for r in records
        ]
    }


# Recommendation Endpoints
@app.get("/api/recommendations/{user_id}", tags=["Recommendations"])
async def get_recommendations(user_id: int, limit: int = 5):
    """Get personalized book recommendations for a user"""
    recommendations = recommender.recommend_books(user_id, limit)
    
    return {
        "user_id": user_id,
        "total": len(recommendations),
        "recommendations": [
            {
                "book_id": r[0],
                "title": r[1],
                "author": r[2],
                "genre": r[3],
                "score": round(r[4], 2)
            }
            for r in recommendations
        ]
    }


@app.get("/api/recommendations/similar/{book_id}", tags=["Recommendations"])
async def get_similar_books(book_id: int, limit: int = 5):
    """Find books similar to a given book"""
    similar = recommender.find_similar_books(book_id, limit)
    
    return {
        "book_id": book_id,
        "total": len(similar),
        "similar_books": [
            {
                "book_id": s[0],
                "title": s[1],
                "author": s[2],
                "genre": s[3],
                "similarity_score": s[4]
            }
            for s in similar
        ]
    }


@app.get("/api/recommendations/trending/{community_name}", tags=["Recommendations"])
async def get_trending_books(
    community_name: str,
    days: int = 30,
    limit: int = 5
):
    """Get trending books in a community"""
    trending = recommender.get_trending_books(community_name, days, limit)
    
    return {
        "community": community_name,
        "period_days": days,
        "total": len(trending),
        "trending_books": [
            {
                "book_id": t[0],
                "title": t[1],
                "author": t[2],
                "borrow_count": t[3]
            }
            for t in trending
        ]
    }


@app.get("/api/recommendations/genre/{user_id}", tags=["Recommendations"])
async def get_genre_recommendations(
    user_id: int,
    genre: str,
    limit: int = 5
):
    """Get recommendations from a specific genre"""
    books = recommender.recommend_by_genre(user_id, genre, limit)
    
    return {
        "user_id": user_id,
        "genre": genre,
        "total": len(books),
        "books": [
            {
                "book_id": b[0],
                "title": b[1],
                "author": b[2],
                "genre": b[3],
                "avg_rating": round(b[4], 2)
            }
            for b in books
        ]
    }


# Gamification Endpoints
@app.get("/api/gamification/stats/{user_id}", tags=["Gamification"])
async def get_user_stats(user_id: int):
    """Get complete gamification statistics for a user"""
    stats = gamification.get_user_stats(user_id)
    
    if not stats:
        raise HTTPException(status_code=404, detail="User stats not found")
    
    return stats


@app.post("/api/gamification/update/{user_id}", tags=["Gamification"])
async def update_stats(user_id: int):
    """Manually update reading statistics (for testing)"""
    result = gamification.update_reading_stats(user_id)
    
    if not result:
        raise HTTPException(status_code=400, detail="Failed to update stats")
    
    return result


@app.get("/api/gamification/leaderboard/{community_name}", tags=["Gamification"])
async def get_leaderboard(community_name: str, limit: int = 10):
    """Get community leaderboard"""
    results = gamification.get_leaderboard(community_name, limit)
    
    return {
        "community": community_name,
        "total": len(results),
        "leaderboard": [
            {
                "rank": idx + 1,
                "name": r[0],
                "books_read": r[1],
                "total_points": r[2],
                "current_streak": r[3],
                "longest_streak": r[4]
            }
            for idx, r in enumerate(results)
        ]
    }


# Analytics Endpoints
@app.get("/api/analytics/community/{community_name}", tags=["Analytics"])
async def get_community_analytics(community_name: str):
    """Get comprehensive analytics for a community"""
    cursor = db.conn.cursor()
    
    # Total users
    cursor.execute("""
        SELECT COUNT(*) FROM users WHERE community_name = ?
    """, (community_name,))
    total_users = cursor.fetchone()[0]
    
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
    
    return {
        "community": community_name,
        "total_users": total_users,
        "total_books": total_books,
        "total_borrows": total_borrows,
        "most_popular_genre": {
            "genre": popular_genre[0] if popular_genre else None,
            "count": popular_genre[1] if popular_genre else 0
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)