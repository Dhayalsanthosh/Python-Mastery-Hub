"""
Flask Examples for Web Development Learning.

Comprehensive Flask examples from basic to advanced concepts.
"""

from typing import Dict, Any


def get_flask_basics() -> Dict[str, Any]:
    """Get basic Flask examples."""
    return {
        "basic_flask_app": {
            "code": '''
from flask import Flask, request, jsonify, render_template_string
from flask import session, redirect, url_for, flash
import os
from datetime import datetime

# Create Flask application
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change in production!

# In-memory data store (use database in production)
users = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
}
posts = []

# Basic routes
@app.route('/')
def home():
    """Home page with basic HTML."""
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Flask Demo</title></head>
    <body>
        <h1>Welcome to Flask Demo!</h1>
        <ul>
            <li><a href="/users">View Users</a></li>
            <li><a href="/posts">View Posts</a></li>
            <li><a href="/create-post">Create Post</a></li>
            <li><a href="/about">About</a></li>
        </ul>
    </body>
    </html>
    """
    return html

@app.route('/about')
def about():
    """About page with template."""
    return render_template_string("""
    <h1>About This App</h1>
    <p>This is a Flask demonstration application.</p>
    <p>Current time: {{ current_time }}</p>
    <a href="{{ url_for('home') }}">Back to Home</a>
    """, current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# RESTful routes for users
@app.route('/users')
def get_users():
    """Get all users."""
    return jsonify(list(users.values()))

@app.route('/users/<int:user_id>')
def get_user(user_id):
    """Get specific user."""
    user = users.get(user_id)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['POST'])
def create_user():
    """Create new user."""
    data = request.get_json()
    
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({"error": "Name and email required"}), 400
    
    user_id = max(users.keys()) + 1 if users else 1
    user = {
        "id": user_id,
        "name": data['name'],
        "email": data['email']
    }
    users[user_id] = user
    
    return jsonify(user), 201

# Form handling
@app.route('/create-post', methods=['GET', 'POST'])
def create_post():
    """Handle post creation form."""
    if request.method == 'GET':
        return render_template_string("""
        <h1>Create New Post</h1>
        <form method="POST">
            <p>
                <label>Title:</label><br>
                <input type="text" name="title" required>
            </p>
            <p>
                <label>Content:</label><br>
                <textarea name="content" rows="5" cols="50" required></textarea>
            </p>
            <p>
                <label>Author ID:</label><br>
                <input type="number" name="author_id" required>
            </p>
            <p>
                <input type="submit" value="Create Post">
            </p>
        </form>
        <a href="{{ url_for('home') }}">Back to Home</a>
        """)
    
    # POST request - create post
    title = request.form.get('title')
    content = request.form.get('content')
    author_id = request.form.get('author_id', type=int)
    
    if not all([title, content, author_id]):
        flash('All fields are required!')
        return redirect(url_for('create_post'))
    
    if author_id not in users:
        flash('Invalid author ID!')
        return redirect(url_for('create_post'))
    
    post = {
        "id": len(posts) + 1,
        "title": title,
        "content": content,
        "author_id": author_id,
        "author_name": users[author_id]['name'],
        "created_at": datetime.now().isoformat()
    }
    posts.append(post)
    
    flash('Post created successfully!')
    return redirect(url_for('get_posts'))

@app.route('/posts')
def get_posts():
    """Display all posts."""
    posts_html = "".join([f"""
    <div style="border: 1px solid #ccc; margin: 10px; padding: 10px;">
        <h3>{post['title']}</h3>
        <p>{post['content']}</p>
        <small>By {post['author_name']} at {post['created_at']}</small>
    </div>
    """ for post in posts])
    
    return render_template_string(f"""
    <h1>All Posts</h1>
    {posts_html if posts else '<p>No posts yet.</p>'}
    <a href="{{{{ url_for('create_post') }}}}">Create New Post</a> |
    <a href="{{{{ url_for('home') }}}}">Back to Home</a>
    """)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500

# Configuration and middleware
@app.before_request
def before_request():
    """Run before each request."""
    print(f"Request: {request.method} {request.path}")

@app.after_request
def after_request(response):
    """Run after each request."""
    response.headers['X-Custom-Header'] = 'Flask Demo'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
''',
            "explanation": "Basic Flask application with routes, forms, templates, and error handling"
        },
        
        "flask_templates": {
            "code": '''
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'demo-secret-key'

# Sample data
blog_posts = [
    {
        "id": 1,
        "title": "Welcome to Flask",
        "content": "This is your first blog post using Flask templates.",
        "author": "Admin",
        "date": datetime(2023, 1, 1)
    },
    {
        "id": 2,
        "title": "Template Inheritance",
        "content": "Learn how to use template inheritance in Flask.",
        "author": "Flask Dev",
        "date": datetime(2023, 1, 15)
    }
]

# Template examples (would be in templates/ directory)
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Flask Blog{% endblock %}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        header { background: #333; color: white; padding: 1rem; margin-bottom: 2rem; }
        nav a { color: white; text-decoration: none; margin-right: 1rem; }
        .container { max-width: 800px; margin: 0 auto; }
        .post { border: 1px solid #ddd; padding: 1rem; margin-bottom: 1rem; }
        .flash-messages { margin-bottom: 1rem; }
        .flash-success { background: #d4edda; color: #155724; padding: 0.5rem; }
        .flash-error { background: #f8d7da; color: #721c24; padding: 0.5rem; }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>Flask Blog Demo</h1>
            <nav>
                <a href="{{ url_for('index') }}">Home</a>
                <a href="{{ url_for('new_post') }}">New Post</a>
                <a href="{{ url_for('about') }}">About</a>
            </nav>
        </div>
    </header>
    
    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-messages">
                    {% for category, message in messages %}
                        <div class="flash-{{ category }}">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

INDEX_TEMPLATE = """
{% extends "base.html" %}

{% block title %}Home - Flask Blog{% endblock %}

{% block content %}
<h2>Latest Blog Posts</h2>

{% if posts %}
    {% for post in posts %}
        <article class="post">
            <h3>{{ post.title }}</h3>
            <p>{{ post.content }}</p>
            <footer>
                <small>
                    By {{ post.author }} on {{ post.date.strftime('%B %d, %Y') }}
                    | <a href="{{ url_for('view_post', post_id=post.id) }}">Read More</a>
                </small>
            </footer>
        </article>
    {% endfor %}
{% else %}
    <p>No blog posts yet. <a href="{{ url_for('new_post') }}">Create the first one!</a></p>
{% endif %}
{% endblock %}
"""

POST_TEMPLATE = """
{% extends "base.html" %}

{% block title %}{{ post.title }} - Flask Blog{% endblock %}

{% block content %}
<article class="post">
    <h2>{{ post.title }}</h2>
    <p>{{ post.content }}</p>
    <footer>
        <small>By {{ post.author }} on {{ post.date.strftime('%B %d, %Y') }}</small>
    </footer>
</article>

<a href="{{ url_for('index') }}">&larr; Back to Home</a>
{% endblock %}
"""

NEW_POST_TEMPLATE = """
{% extends "base.html" %}

{% block title %}New Post - Flask Blog{% endblock %}

{% block content %}
<h2>Create New Post</h2>

<form method="POST">
    <div style="margin-bottom: 1rem;">
        <label for="title">Title:</label><br>
        <input type="text" id="title" name="title" required 
               style="width: 100%; padding: 0.5rem;">
    </div>
    
    <div style="margin-bottom: 1rem;">
        <label for="content">Content:</label><br>
        <textarea id="content" name="content" required rows="10" 
                  style="width: 100%; padding: 0.5rem;"></textarea>
    </div>
    
    <div style="margin-bottom: 1rem;">
        <label for="author">Author:</label><br>
        <input type="text" id="author" name="author" required 
               style="width: 100%; padding: 0.5rem;">
    </div>
    
    <button type="submit" style="padding: 0.5rem 1rem; background: #007bff; color: white; border: none;">
        Create Post
    </button>
</form>

<a href="{{ url_for('index') }}">&larr; Back to Home</a>
{% endblock %}
"""

# Routes using templates
@app.route('/')
def index():
    """Home page with blog posts."""
    return render_template_string(INDEX_TEMPLATE, posts=blog_posts)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    """View individual blog post."""
    post = next((p for p in blog_posts if p['id'] == post_id), None)
    if not post:
        flash('Post not found.', 'error')
        return redirect(url_for('index'))
    
    return render_template_string(POST_TEMPLATE, post=post)

@app.route('/new', methods=['GET', 'POST'])
def new_post():
    """Create new blog post."""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author = request.form.get('author')
        
        if all([title, content, author]):
            new_id = max([p['id'] for p in blog_posts]) + 1 if blog_posts else 1
            post = {
                'id': new_id,
                'title': title,
                'content': content,
                'author': author,
                'date': datetime.now()
            }
            blog_posts.append(post)
            flash('Post created successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('All fields are required.', 'error')
    
    return render_template_string(NEW_POST_TEMPLATE)

@app.route('/about')
def about():
    """About page."""
    about_template = """
    {% extends "base.html" %}
    
    {% block title %}About - Flask Blog{% endblock %}
    
    {% block content %}
    <h2>About This Blog</h2>
    <p>This is a demonstration Flask blog application showcasing:</p>
    <ul>
        <li>Template inheritance</li>
        <li>Form handling</li>
        <li>Flash messages</li>
        <li>URL routing</li>
        <li>Template filters and functions</li>
    </ul>
    
    <h3>Template Features Used:</h3>
    <ul>
        <li><strong>Base template:</strong> Common layout and navigation</li>
        <li><strong>Block inheritance:</strong> {% raw %}{% block content %}{% endraw %}</li>
        <li><strong>URL generation:</strong> {% raw %}{{ url_for('route_name') }}{% endraw %}</li>
        <li><strong>Flash messages:</strong> {% raw %}{% with messages = get_flashed_messages() %}{% endraw %}</li>
        <li><strong>Conditional rendering:</strong> {% raw %}{% if condition %}{% endraw %}</li>
        <li><strong>Loops:</strong> {% raw %}{% for item in items %}{% endraw %}</li>
        <li><strong>Filters:</strong> {% raw %}{{ date.strftime('%B %d, %Y') }}{% endraw %}</li>
    </ul>
    
    <p>Current time: {{ current_time.strftime('%Y-%m-%d %H:%M:%S') }}</p>
    
    <a href="{{ url_for('index') }}">&larr; Back to Home</a>
    {% endblock %}
    """
    
    return render_template_string(about_template, current_time=datetime.now())

# Custom template filters
@app.template_filter('datetime')
def datetime_filter(dt):
    """Custom filter for formatting datetime."""
    return dt.strftime('%B %d, %Y at %I:%M %p')

# Template context processors
@app.context_processor
def inject_template_vars():
    """Inject variables into all templates."""
    return {
        'current_year': datetime.now().year,
        'app_name': 'Flask Blog Demo'
    }

if __name__ == '__main__':
    app.run(debug=True)
''',
            "explanation": "Flask templates with inheritance, forms, and template features"
        }
    }


def get_flask_advanced() -> Dict[str, Any]:
    """Get advanced Flask examples."""
    return {
        "flask_blueprints": {
            "code": '''
from flask import Flask, Blueprint, jsonify, request
from datetime import datetime

# Create main app
app = Flask(__name__)

# User blueprint
users_bp = Blueprint('users', __name__, url_prefix='/api/users')

# In-memory user store
users_store = {}
user_id_counter = 1

@users_bp.route('/', methods=['GET'])
def list_users():
    """List all users."""
    return jsonify({
        "users": list(users_store.values()),
        "count": len(users_store)
    })

@users_bp.route('/', methods=['POST'])
def create_user():
    """Create a new user."""
    global user_id_counter
    
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Name is required"}), 400
    
    user = {
        "id": user_id_counter,
        "name": data['name'],
        "email": data.get('email'),
        "created_at": datetime.now().isoformat()
    }
    
    users_store[user_id_counter] = user
    user_id_counter += 1
    
    return jsonify(user), 201

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get specific user."""
    user = users_store.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user."""
    user = users_store.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    user.update({
        "name": data.get('name', user['name']),
        "email": data.get('email', user['email']),
        "updated_at": datetime.now().isoformat()
    })
    
    return jsonify(user)

@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user."""
    if user_id not in users_store:
        return jsonify({"error": "User not found"}), 404
    
    deleted_user = users_store.pop(user_id)
    return jsonify({
        "message": f"User {deleted_user['name']} deleted successfully"
    })

# Posts blueprint
posts_bp = Blueprint('posts', __name__, url_prefix='/api/posts')

# In-memory posts store
posts_store = {}
post_id_counter = 1

@posts_bp.route('/', methods=['GET'])
def list_posts():
    """List all posts."""
    return jsonify({
        "posts": list(posts_store.values()),
        "count": len(posts_store)
    })

@posts_bp.route('/', methods=['POST'])
def create_post():
    """Create a new post."""
    global post_id_counter
    
    data = request.get_json()
    required_fields = ['title', 'content', 'author_id']
    
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Title, content, and author_id are required"}), 400
    
    # Verify author exists
    if data['author_id'] not in users_store:
        return jsonify({"error": "Author not found"}), 400
    
    post = {
        "id": post_id_counter,
        "title": data['title'],
        "content": data['content'],
        "author_id": data['author_id'],
        "author_name": users_store[data['author_id']]['name'],
        "created_at": datetime.now().isoformat()
    }
    
    posts_store[post_id_counter] = post
    post_id_counter += 1
    
    return jsonify(post), 201

@posts_bp.route('/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Get specific post."""
    post = posts_store.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(post)

# Register blueprints
app.register_blueprint(users_bp)
app.register_blueprint(posts_bp)

# Main routes
@app.route('/')
def index():
    """API documentation."""
    return jsonify({
        "message": "Flask Blueprints API Demo",
        "endpoints": {
            "users": "/api/users",
            "posts": "/api/posts"
        },
        "version": "1.0"
    })

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "users_count": len(users_store),
        "posts_count": len(posts_store)
    })

if __name__ == '__main__':
    app.run(debug=True)
''',
            "explanation": "Flask Blueprints for modular application organization"
        },
        
        "flask_middleware": {
            "code": '''
from flask import Flask, request, jsonify, g
from functools import wraps
import time
import logging
from datetime import datetime

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom middleware using before/after request hooks
@app.before_request
def before_request_func():
    """Execute before each request."""
    g.start_time = time.time()
    g.request_id = f"req_{int(time.time() * 1000)}"
    
    logger.info(f"[{g.request_id}] {request.method} {request.path} - Started")
    
    # Add CORS headers for all requests
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

@app.after_request
def after_request_func(response):
    """Execute after each request."""
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        logger.info(f"[{g.request_id}] {request.method} {request.path} - "
                   f"Completed in {duration:.3f}s with status {response.status_code}")
    
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Access-Control-Allow-Origin'] = '*'
    
    return response

# Custom decorators for middleware-like functionality
def timing_decorator(f):
    """Decorator to time function execution."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        
        # Add timing info to response if it's JSON
        if hasattr(result, 'json') or isinstance(result, tuple):
            duration = end_time - start_time
            logger.info(f"Function {f.__name__} took {duration:.3f}s")
        
        return result
    return decorated_function

def require_json(f):
    """Decorator to require JSON content type."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_requests=10, per_seconds=60):
    """Simple rate limiting decorator."""
    requests = {}
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = time.time()
            
            # Clean old requests
            if client_ip in requests:
                requests[client_ip] = [
                    req_time for req_time in requests[client_ip]
                    if current_time - req_time < per_seconds
                ]
            else:
                requests[client_ip] = []
            
            # Check rate limit
            if len(requests[client_ip]) >= max_requests:
                return jsonify({
                    "error": "Rate limit exceeded",
                    "retry_after": per_seconds
                }), 429
            
            # Add current request
            requests[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Sample data
items = []
item_counter = 1

# Routes with middleware
@app.route('/')
@timing_decorator
def index():
    """Home endpoint with timing."""
    return jsonify({
        "message": "Flask Middleware Demo",
        "timestamp": datetime.now().isoformat(),
        "request_id": g.request_id if hasattr(g, 'request_id') else None
    })

@app.route('/items', methods=['GET'])
@timing_decorator
@rate_limit(max_requests=20, per_seconds=60)
def get_items():
    """Get all items with rate limiting."""
    return jsonify({
        "items": items,
        "count": len(items),
        "request_id": g.request_id
    })

@app.route('/items', methods=['POST'])
@require_json
@timing_decorator
@rate_limit(max_requests=5, per_seconds=60)
def create_item():
    """Create new item with JSON validation and rate limiting."""
    global item_counter
    
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({"error": "Name is required"}), 400
    
    item = {
        "id": item_counter,
        "name": data['name'],
        "description": data.get('description', ''),
        "created_at": datetime.now().isoformat(),
        "request_id": g.request_id
    }
    
    items.append(item)
    item_counter += 1
    
    logger.info(f"[{g.request_id}] Created item: {item['name']}")
    
    return jsonify(item), 201

@app.route('/items/<int:item_id>', methods=['GET'])
@timing_decorator
def get_item(item_id):
    """Get specific item."""
    item = next((item for item in items if item['id'] == item_id), None)
    
    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    return jsonify(item)

@app.route('/slow')
@timing_decorator
def slow_endpoint():
    """Slow endpoint to demonstrate timing middleware."""
    import time
    time.sleep(2)  # Simulate slow operation
    
    return jsonify({
        "message": "This was a slow operation",
        "duration": "2 seconds",
        "request_id": g.request_id
    })

# Error handlers with middleware
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Not found",
        "path": request.path,
        "method": request.method,
        "request_id": g.request_id if hasattr(g, 'request_id') else None
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"[{g.request_id if hasattr(g, 'request_id') else 'unknown'}] "
                f"Internal error: {str(error)}")
    
    return jsonify({
        "error": "Internal server error",
        "request_id": g.request_id if hasattr(g, 'request_id') else None
    }), 500

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check with system info."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "items_count": len(items),
        "uptime": "running",
        "request_id": g.request_id
    })

if __name__ == '__main__':
    app.run(debug=True)
''',
            "explanation": "Flask middleware implementation with decorators and request hooks"
        }
    }