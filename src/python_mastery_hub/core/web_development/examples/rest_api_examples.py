"""
REST API Examples for Web Development Learning.

Complete REST API implementation with filtering, pagination, and validation.
Organized from basic to advanced concepts with multiple approaches.
"""

from typing import Dict, Any


def get_rest_api_examples() -> Dict[str, Any]:
    """Get comprehensive REST API examples."""
    return {
        "basic_crud_api": {
            "code": '''
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

app = FastAPI(title="Basic CRUD API", version="1.0.0")

# Simple Pydantic models
class BookBase(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# In-memory storage
books_db: Dict[int, Book] = {}
book_counter = 1

# Basic CRUD operations
@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate):
    """Create a new book."""
    global book_counter
    
    new_book = Book(
        id=book_counter,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        created_at=datetime.now()
    )
    
    books_db[book_counter] = new_book
    book_counter += 1
    
    return new_book

@app.get("/books", response_model=List[Book])
async def get_books():
    """Get all books."""
    return list(books_db.values())

@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: int):
    """Get a specific book."""
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    return books_db[book_id]

@app.put("/books/{book_id}", response_model=Book)
async def update_book(book_id: int, book: BookCreate):
    """Update a book."""
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    
    updated_book = Book(
        id=book_id,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        created_at=books_db[book_id].created_at
    )
    
    books_db[book_id] = updated_book
    return updated_book

@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    """Delete a book."""
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    
    deleted_book = books_db.pop(book_id)
    return {"message": f"Book '{deleted_book.title}' deleted successfully"}

# Health check
@app.get("/health")
async def health_check():
    """API health check."""
    return {"status": "healthy", "books_count": len(books_db)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
            "explanation": "Basic CRUD API demonstrating fundamental REST operations with simple validation"
        },
        
        "intermediate_api_with_validation": {
            "code": '''
from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field, validator, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum

app = FastAPI(title="Intermediate API with Validation", version="1.0.0")

# Enums for better validation
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

# Advanced Pydantic models with validation
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, regex="^[a-zA-Z0-9_]+$")
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class User(UserBase):
    id: int
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    status: PostStatus = PostStatus.DRAFT

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    status: Optional[PostStatus] = None

class Post(PostBase):
    id: int
    author_id: int
    author_username: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Storage
users_db: Dict[int, User] = {}
posts_db: Dict[int, Post] = {}
user_counter = 1
post_counter = 1

# User endpoints with validation
@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Create a new user with validation."""
    global user_counter
    
    # Check for duplicate username
    for existing_user in users_db.values():
        if existing_user.username == user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        if existing_user.email == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    new_user = User(
        id=user_counter,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        created_at=datetime.now()
    )
    
    users_db[user_counter] = new_user
    user_counter += 1
    
    return new_user

@app.get("/users", response_model=List[User])
async def get_users(
    role: Optional[UserRole] = None,
    active_only: bool = Query(True, description="Filter active users only")
):
    """Get users with optional filtering."""
    users = list(users_db.values())
    
    if role:
        users = [u for u in users if u.role == role]
    
    if active_only:
        users = [u for u in users if u.is_active]
    
    return users

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get a specific user."""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return users_db[user_id]

# Post endpoints with relationships
@app.post("/posts", response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, author_id: int = Query(..., description="Author user ID")):
    """Create a new post."""
    global post_counter
    
    # Verify author exists
    if author_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Author not found"
        )
    
    author = users_db[author_id]
    now = datetime.now()
    
    new_post = Post(
        id=post_counter,
        title=post.title,
        content=post.content,
        status=post.status,
        author_id=author_id,
        author_username=author.username,
        created_at=now,
        updated_at=now
    )
    
    posts_db[post_counter] = new_post
    post_counter += 1
    
    return new_post

@app.get("/posts", response_model=List[Post])
async def get_posts(
    status: Optional[PostStatus] = None,
    author_id: Optional[int] = None,
    limit: int = Query(10, ge=1, le=100, description="Number of posts to return")
):
    """Get posts with filtering."""
    posts = list(posts_db.values())
    
    if status:
        posts = [p for p in posts if p.status == status]
    
    if author_id:
        posts = [p for p in posts if p.author_id == author_id]
    
    # Sort by creation date, newest first
    posts.sort(key=lambda x: x.created_at, reverse=True)
    
    return posts[:limit]

@app.put("/posts/{post_id}", response_model=Post)
async def update_post(post_id: int, post_update: PostUpdate):
    """Update a post with partial updates."""
    if post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    post = posts_db[post_id]
    update_data = post_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(post, field, value)
    
    post.updated_at = datetime.now()
    return post

@app.get("/stats")
async def get_api_stats():
    """Get API statistics."""
    return {
        "users": {
            "total": len(users_db),
            "active": len([u for u in users_db.values() if u.is_active]),
            "by_role": {
                role.value: len([u for u in users_db.values() if u.role == role])
                for role in UserRole
            }
        },
        "posts": {
            "total": len(posts_db),
            "by_status": {
                status.value: len([p for p in posts_db.values() if p.status == status])
                for status in PostStatus
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
            "explanation": "Intermediate API with advanced validation, enums, relationships, and filtering"
        },
        
        "advanced_api_with_pagination": {
            "code": '''
from fastapi import FastAPI, HTTPException, status, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import math

app = FastAPI(title="Advanced API with Pagination", version="1.0.0")

# Advanced enums and models
class ItemStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class ItemCategory(str, Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    BOOKS = "books"
    HOME = "home"
    SPORTS = "sports"

# Advanced Pydantic models
class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0, le=1000000)
    category: ItemCategory
    status: ItemStatus = ItemStatus.ACTIVE
    tags: List[str] = Field(default_factory=list, max_items=10)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0, le=1000000)
    category: Optional[ItemCategory] = None
    status: Optional[ItemStatus] = None
    tags: Optional[List[str]] = Field(None, max_items=10)

class Item(ItemBase):
    id: str
    created_at: datetime
    updated_at: datetime
    view_count: int = 0
    
    class Config:
        from_attributes = True

class PaginationMeta(BaseModel):
    page: int
    size: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool

class PaginatedResponse(BaseModel):
    items: List[Item]
    meta: PaginationMeta

class FilterParams(BaseModel):
    status: Optional[ItemStatus] = None
    category: Optional[ItemCategory] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    search: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None

# Storage
items_db: Dict[str, Item] = {}

# Helper functions
def generate_id() -> str:
    """Generate unique ID."""
    return str(uuid.uuid4())

def apply_filters(items: List[Item], filters: FilterParams) -> List[Item]:
    """Apply filtering to items."""
    filtered = items
    
    if filters.status:
        filtered = [item for item in filtered if item.status == filters.status]
    
    if filters.category:
        filtered = [item for item in filtered if item.category == filters.category]
    
    if filters.min_price is not None:
        filtered = [item for item in filtered if item.price >= filters.min_price]
    
    if filters.max_price is not None:
        filtered = [item for item in filtered if item.price <= filters.max_price]
    
    if filters.search:
        search_lower = filters.search.lower()
        filtered = [
            item for item in filtered
            if search_lower in item.name.lower() or 
               (item.description and search_lower in item.description.lower())
        ]
    
    if filters.tags:
        filtered = [
            item for item in filtered
            if any(tag in item.tags for tag in filters.tags)
        ]
    
    return filtered

def sort_items(items: List[Item], sort_by: str, order: SortOrder) -> List[Item]:
    """Sort items by specified field."""
    reverse = (order == SortOrder.DESC)
    
    sort_map = {
        "name": lambda x: x.name.lower(),
        "price": lambda x: x.price,
        "created_at": lambda x: x.created_at,
        "updated_at": lambda x: x.updated_at,
        "view_count": lambda x: x.view_count
    }
    
    sort_key = sort_map.get(sort_by, sort_map["created_at"])
    return sorted(items, key=sort_key, reverse=reverse)

def paginate_items(items: List[Item], page: int, size: int) -> tuple[List[Item], PaginationMeta]:
    """Apply pagination to items."""
    total = len(items)
    pages = math.ceil(total / size) if total > 0 else 1
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    
    paginated_items = items[start_idx:end_idx]
    
    meta = PaginationMeta(
        page=page,
        size=size,
        total=total,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )
    
    return paginated_items, meta

# Dependency functions
async def get_filter_params(
    status: Optional[ItemStatus] = None,
    category: Optional[ItemCategory] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    search: Optional[str] = Query(None, min_length=1),
    tags: Optional[List[str]] = Query(None)
) -> FilterParams:
    """Extract filter parameters."""
    return FilterParams(
        status=status,
        category=category,
        min_price=min_price,
        max_price=max_price,
        search=search,
        tags=tags
    )

# Advanced CRUD endpoints
@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item_data: ItemCreate):
    """Create a new item."""
    # Check for duplicate names
    existing_names = [item.name.lower() for item in items_db.values()]
    if item_data.name.lower() in existing_names:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item with this name already exists"
        )
    
    item_id = generate_id()
    now = datetime.now()
    
    item = Item(
        id=item_id,
        name=item_data.name,
        description=item_data.description,
        price=item_data.price,
        category=item_data.category,
        status=item_data.status,
        tags=item_data.tags,
        created_at=now,
        updated_at=now
    )
    
    items_db[item_id] = item
    return item

@app.get("/items", response_model=PaginatedResponse)
async def get_items(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    sort_by: str = Query("created_at", regex="^(name|price|created_at|updated_at|view_count)$"),
    order: SortOrder = SortOrder.DESC,
    filters: FilterParams = Depends(get_filter_params)
):
    """Get items with advanced filtering, sorting, and pagination."""
    all_items = list(items_db.values())
    
    # Apply filters
    filtered_items = apply_filters(all_items, filters)
    
    # Apply sorting
    sorted_items = sort_items(filtered_items, sort_by, order)
    
    # Apply pagination
    paginated_items, meta = paginate_items(sorted_items, page, size)
    
    return PaginatedResponse(items=paginated_items, meta=meta)

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: str):
    """Get a specific item and increment view count."""
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    item = items_db[item_id]
    item.view_count += 1  # Track views
    return item

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item_update: ItemUpdate):
    """Update an existing item."""
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    item = items_db[item_id]
    update_data = item_update.dict(exclude_unset=True)
    
    # Check for name conflicts if updating name
    if "name" in update_data:
        existing_names = [
            other_item.name.lower() 
            for other_id, other_item in items_db.items() 
            if other_id != item_id
        ]
        if update_data["name"].lower() in existing_names:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item with this name already exists"
            )
    
    # Update fields
    for field, value in update_data.items():
        setattr(item, field, value)
    
    item.updated_at = datetime.now()
    return item

@app.patch("/items/{item_id}/status", response_model=Item)
async def update_item_status(item_id: str, new_status: ItemStatus):
    """Update only the status of an item."""
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    item = items_db[item_id]
    item.status = new_status
    item.updated_at = datetime.now()
    
    return item

@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    """Delete an item."""
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    deleted_item = items_db.pop(item_id)
    return {"message": f"Item '{deleted_item.name}' deleted successfully"}

@app.delete("/items")
async def bulk_delete_items(item_ids: List[str]):
    """Bulk delete multiple items."""
    deleted_items = []
    not_found_ids = []
    
    for item_id in item_ids:
        if item_id in items_db:
            deleted_item = items_db.pop(item_id)
            deleted_items.append(deleted_item.name)
        else:
            not_found_ids.append(item_id)
    
    result = {
        "deleted_count": len(deleted_items),
        "deleted_items": deleted_items
    }
    
    if not_found_ids:
        result["not_found_ids"] = not_found_ids
    
    return result

# Analytics endpoints
@app.get("/items/stats/summary")
async def get_items_summary():
    """Get comprehensive item statistics."""
    all_items = list(items_db.values())
    
    if not all_items:
        return {"message": "No items found"}
    
    total_items = len(all_items)
    total_value = sum(item.price for item in all_items)
    avg_price = total_value / total_items
    total_views = sum(item.view_count for item in all_items)
    
    # Status breakdown
    status_counts = {}
    for status in ItemStatus:
        status_counts[status.value] = len([item for item in all_items if item.status == status])
    
    # Category breakdown
    category_counts = {}
    for category in ItemCategory:
        category_counts[category.value] = len([item for item in all_items if item.category == category])
    
    # Price statistics
    prices = [item.price for item in all_items]
    price_stats = {
        "min": min(prices),
        "max": max(prices),
        "average": avg_price,
        "median": sorted(prices)[len(prices) // 2]
    }
    
    # Most popular items
    popular_items = sorted(all_items, key=lambda x: x.view_count, reverse=True)[:5]
    popular_items_data = [
        {"id": item.id, "name": item.name, "views": item.view_count}
        for item in popular_items
    ]
    
    return {
        "total_items": total_items,
        "total_value": total_value,
        "total_views": total_views,
        "average_price": avg_price,
        "status_breakdown": status_counts,
        "category_breakdown": category_counts,
        "price_statistics": price_stats,
        "popular_items": popular_items_data
    }

@app.get("/categories/{category}/items", response_model=PaginatedResponse)
async def get_items_by_category(
    category: ItemCategory,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(name|price|created_at|view_count)$"),
    order: SortOrder = SortOrder.DESC
):
    """Get items in a specific category."""
    category_items = [item for item in items_db.values() if item.category == category]
    
    # Apply sorting
    sorted_items = sort_items(category_items, sort_by, order)
    
    # Apply pagination
    paginated_items, meta = paginate_items(sorted_items, page, size)
    
    return PaginatedResponse(items=paginated_items, meta=meta)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
            "explanation": "Advanced API with comprehensive pagination, filtering, sorting, analytics, and dependency injection"
        },
        
        "flask_rest_comparison": {
            "code": '''
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from werkzeug.exceptions import BadRequest, NotFound
from datetime import datetime
from typing import Dict, List, Optional
import uuid

app = Flask(__name__)
api = Api(app)

# Simple data models
class Book:
    def __init__(self, title: str, author: str, isbn: str = None):
        self.id = str(uuid.uuid4())
        self.title = title
        self.author = author
        self.isbn = isbn
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "created_at": self.created_at.isoformat()
        }

# Storage
books_storage: Dict[str, Book] = {}

# Flask-RESTful Resource classes
class BookListResource(Resource):
    def get(self):
        """Get all books."""
        return [book.to_dict() for book in books_storage.values()]
    
    def post(self):
        """Create a new book."""
        data = request.get_json()
        
        if not data:
            return {"error": "JSON data required"}, 400
        
        # Simple validation
        required_fields = ["title", "author"]
        for field in required_fields:
            if field not in data:
                return {"error": f"'{field}' is required"}, 400
        
        book = Book(
            title=data["title"],
            author=data["author"],
            isbn=data.get("isbn")
        )
        
        books_storage[book.id] = book
        return book.to_dict(), 201

class BookResource(Resource):
    def get(self, book_id):
        """Get a specific book."""
        if book_id not in books_storage:
            return {"error": "Book not found"}, 404
        
        return books_storage[book_id].to_dict()
    
    def put(self, book_id):
        """Update a book."""
        if book_id not in books_storage:
            return {"error": "Book not found"}, 404
        
        data = request.get_json()
        if not data:
            return {"error": "JSON data required"}, 400
        
        book = books_storage[book_id]
        
        # Update fields if provided
        if "title" in data:
            book.title = data["title"]
        if "author" in data:
            book.author = data["author"]
        if "isbn" in data:
            book.isbn = data["isbn"]
        
        return book.to_dict()
    
    def delete(self, book_id):
        """Delete a book."""
        if book_id not in books_storage:
            return {"error": "Book not found"}, 404
        
        deleted_book = books_storage.pop(book_id)
        return {"message": f"Book '{deleted_book.title}' deleted successfully"}

# Traditional Flask routes (for comparison)
@app.route('/api/books/search')
def search_books():
    """Search books by title or author."""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    matching_books = []
    for book in books_storage.values():
        if query in book.title.lower() or query in book.author.lower():
            matching_books.append(book.to_dict())
    
    return jsonify({
        "query": query,
        "results": matching_books,
        "count": len(matching_books)
    })

@app.route('/api/stats')
def get_stats():
    """Get book statistics."""
    total_books = len(books_storage)
    
    if total_books == 0:
        return jsonify({"total_books": 0, "authors": [], "recent_books": []})
    
    # Count unique authors
    authors = set(book.author for book in books_storage.values())
    
    # Get recent books (last 5)
    recent_books = sorted(
        books_storage.values(),
        key=lambda x: x.created_at,
        reverse=True
    )[:5]
    
    return jsonify({
        "total_books": total_books,
        "unique_authors": len(authors),
        "authors": list(authors),
        "recent_books": [book.to_dict() for book in recent_books]
    })

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Register resources
api.add_resource(BookListResource, '/api/books')
api.add_resource(BookResource, '/api/books/<string:book_id>')

# Health check
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "books_count": len(books_storage),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Add some sample data
    sample_books = [
        Book("The Python Tutorial", "Guido van Rossum", "978-0123456789"),
        Book("Flask Web Development", "Miguel Grinberg", "978-1449372627"),
        Book("REST API Design", "Mark Masse", "978-1449358068")
    ]
    
    for book in sample_books:
        books_storage[book.id] = book
    
    app.run(debug=True)
''',
            "explanation": "Flask REST API implementation using Flask-RESTful for comparison with FastAPI patterns"
        }
    }