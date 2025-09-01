"""
Flask Blog Exercise for Web Development Learning.

Build a complete blog application with Flask, SQLAlchemy, templates,
and user authentication using traditional web development patterns.
"""

from typing import Dict, Any


def get_exercise() -> Dict[str, Any]:
    """Get the complete Flask blog exercise."""
    return {
        "title": "Flask Blog Application",
        "description": "Build a full-featured blog with Flask, Jinja2 templates, SQLAlchemy, and user authentication",
        "difficulty": "medium",
        "estimated_time": "5-7 hours",
        "learning_objectives": [
            "Structure Flask applications with blueprints",
            "Implement Jinja2 templates with inheritance",
            "Handle forms with Flask-WTF and validation", 
            "Integrate SQLAlchemy ORM with relationships",
            "Add user authentication and sessions",
            "Implement file uploads for images",
            "Create pagination for blog posts",
            "Add search and filtering functionality"
        ],
        "requirements": [
            "Flask web framework",
            "SQLAlchemy for database ORM",
            "Flask-WTF for form handling",
            "Flask-Login for authentication",
            "Jinja2 for templating",
            "Werkzeug for file uploads",
            "Flask-Migrate for database migrations"
        ],
        "starter_code": '''
"""
Flask Blog Application - Starter Code

Complete the TODO sections to build a full-featured blog application.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from wtforms import StringField, TextAreaField, PasswordField, FileField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from datetime import datetime
import os
from urllib.parse import urlparse, urljoin

# TODO: Create Flask application and configure
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# TODO: Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

# TODO: Create database models
class User(UserMixin, db.Model):
    """User model for authentication."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.Text)
    avatar = db.Column(db.String(200), default='default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # TODO: Add relationship to posts
    # posts = db.relationship('Post', backref='author', lazy=True)
    
    def set_password(self, password):
        # TODO: Implement password hashing
        pass
    
    def check_password(self, password):
        # TODO: Implement password verification
        pass

class Category(db.Model):
    """Category model for organizing posts."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # TODO: Add relationship to posts
    # posts = db.relationship('Post', backref='category', lazy=True)

class Post(db.Model):
    """Blog post model."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(300))
    featured_image = db.Column(db.String(200))
    published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    
    # TODO: Add foreign keys and relationships
    # author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    
    def __repr__(self):
        return f'<Post {self.title}>'

# TODO: Implement user loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # TODO: Load user by ID
    pass

# TODO: Create WTForms
class LoginForm(FlaskForm):
    """User login form."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    """User registration form."""
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=4, max=20)
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=8)
    ])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(), 
        EqualTo('password')
    ])

class PostForm(FlaskForm):
    """Blog post creation/editing form."""
    title = StringField('Title', validators=[
        DataRequired(), 
        Length(min=1, max=200)
    ])
    content = TextAreaField('Content', validators=[DataRequired()])
    summary = StringField('Summary', validators=[Length(max=300)])
    category_id = SelectField('Category', coerce=int)
    featured_image = FileField('Featured Image')
    published = SelectField('Status', choices=[
        (True, 'Published'), 
        (False, 'Draft')
    ], coerce=bool)

class ProfileForm(FlaskForm):
    """User profile editing form."""
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=4, max=20)
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    avatar = FileField('Avatar Image')

# TODO: Create authentication blueprint
from flask import Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    # TODO: Implement login functionality
    # 1. Create LoginForm instance
    # 2. Handle form submission
    # 3. Validate user credentials
    # 4. Login user if valid
    # 5. Redirect to next page or home
    # 6. Render login template for GET
    pass

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    # TODO: Implement registration functionality
    # 1. Create RegistrationForm instance
    # 2. Handle form submission
    # 3. Validate form data
    # 4. Check if username/email already exists
    # 5. Create new user
    # 6. Redirect to login page
    # 7. Render registration template for GET
    pass

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    # TODO: Implement logout functionality
    # 1. Logout current user
    # 2. Flash success message
    # 3. Redirect to home page
    pass

# TODO: Create main blog blueprint
blog_bp = Blueprint('blog', __name__)

@blog_bp.route('/')
def index():
    """Blog home page with post listing."""
    # TODO: Implement home page
    # 1. Get page number from request args
    # 2. Query published posts with pagination
    # 3. Order by creation date (newest first)
    # 4. Render index template with posts
    pass

@blog_bp.route('/post/<int:post_id>')
def view_post(post_id):
    """View individual blog post."""
    # TODO: Implement post view
    # 1. Get post by ID or 404
    # 2. Check if post is published (unless author)
    # 3. Increment view count
    # 4. Render post template
    pass

@blog_bp.route('/category/<int:category_id>')
def view_category(category_id):
    """View posts in a category."""
    # TODO: Implement category view
    # 1. Get category by ID or 404
    # 2. Get posts in category with pagination
    # 3. Render category template
    pass

@blog_bp.route('/search')
def search():
    """Search blog posts."""
    # TODO: Implement search functionality
    # 1. Get search query from request args
    # 2. Search posts by title and content
    # 3. Apply pagination
    # 4. Render search results template
    pass

# TODO: Create admin/editor blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def dashboard():
    """Admin dashboard."""
    # TODO: Implement admin dashboard
    # 1. Check if user is authenticated
    # 2. Get user's posts with counts
    # 3. Get recent activity
    # 4. Render dashboard template
    pass

@admin_bp.route('/new-post', methods=['GET', 'POST'])
@login_required
def new_post():
    """Create new blog post."""
    # TODO: Implement post creation
    # 1. Create PostForm instance
    # 2. Populate category choices
    # 3. Handle form submission
    # 4. Process file upload if provided
    # 5. Create new post
    # 6. Redirect to post or dashboard
    # 7. Render new post template for GET
    pass

@admin_bp.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit existing blog post."""
    # TODO: Implement post editing
    # 1. Get post by ID or 404
    # 2. Check if current user is author
    # 3. Create PostForm instance with post data
    # 4. Handle form submission
    # 5. Update post with new data
    # 6. Handle image upload/replacement
    # 7. Render edit template for GET
    pass

@admin_bp.route('/delete-post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete blog post."""
    # TODO: Implement post deletion
    # 1. Get post by ID or 404
    # 2. Check if current user is author
    # 3. Delete post from database
    # 4. Delete associated files
    # 5. Flash success message
    # 6. Redirect to dashboard
    pass

@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Edit user profile."""
    # TODO: Implement profile editing
    # 1. Create ProfileForm with current user data
    # 2. Handle form submission
    # 3. Update user information
    # 4. Handle avatar upload
    # 5. Render profile template
    pass

# TODO: Create utility functions
def allowed_file(filename):
    """Check if uploaded file is allowed."""
    # TODO: Implement file type validation
    # 1. Check if filename has extension
    # 2. Check if extension is in allowed list
    # 3. Return boolean result
    pass

def save_uploaded_file(file, upload_folder):
    """Save uploaded file securely."""
    # TODO: Implement secure file upload
    # 1. Validate file
    # 2. Generate secure filename
    # 3. Ensure upload directory exists
    # 4. Save file
    # 5. Return filename
    pass

def is_safe_url(target):
    """Check if redirect URL is safe."""
    # TODO: Implement URL safety check
    # 1. Parse target URL
    # 2. Check if URL is relative or same host
    # 3. Return boolean result
    pass

# TODO: Create Jinja2 template filters
@app.template_filter('markdown')
def markdown_filter(text):
    """Convert markdown to HTML (basic implementation)."""
    # TODO: Implement basic markdown conversion
    # Or integrate python-markdown library
    pass

@app.template_filter('truncate_words')
def truncate_words(text, count=50):
    """Truncate text to specified word count."""
    # TODO: Implement word truncation
    pass

# TODO: Create context processors
@app.context_processor
def inject_template_vars():
    """Inject common variables into all templates."""
    # TODO: Provide common template variables
    # 1. Get all categories for navigation
    # 2. Get site statistics
    # 3. Return dictionary of variables
    pass

# TODO: Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(blog_bp)
app.register_blueprint(admin_bp)

# TODO: Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
''',
        "template_structure": '''
# Required Template Files Structure

templates/
├── base.html                 # Base template with common layout
├── auth/
│   ├── login.html           # Login form
│   └── register.html        # Registration form
├── blog/
│   ├── index.html           # Home page with post listing
│   ├── post.html            # Individual post view
│   ├── category.html        # Category post listing
│   └── search.html          # Search results
└── admin/
    ├── dashboard.html       # Admin dashboard
    ├── new_post.html        # Create new post
    ├── edit_post.html       # Edit existing post
    └── profile.html         # User profile editing

# Example base.html template:
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{% endblock %} - My Blog</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <!-- Navigation content -->
    </nav>
    
    <main class="container mt-4">
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-info">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </main>
    
    <footer class="bg-light mt-5 py-4">
        <!-- Footer content -->
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
''',
        "testing_guide": '''
# Testing Your Flask Blog Application

## 1. Setup and Run
```bash
# Install dependencies
pip install flask flask-sqlalchemy flask-wtf flask-login

# Run the application
python app.py
```

## 2. Manual Testing Checklist

### Authentication
- [ ] User can register with valid information
- [ ] User cannot register with duplicate username/email
- [ ] User can login with correct credentials
- [ ] User cannot login with incorrect credentials
- [ ] User can logout successfully
- [ ] Protected pages redirect to login

### Blog Functionality
- [ ] Home page displays published posts
- [ ] Posts are paginated correctly
- [ ] Individual posts can be viewed
- [ ] Post view count increments
- [ ] Categories display their posts
- [ ] Search functionality works

### Admin Features
- [ ] Authenticated users can access dashboard
- [ ] Users can create new posts
- [ ] Users can edit their own posts
- [ ] Users can delete their own posts
- [ ] File upload works for images
- [ ] Profile editing works

## 3. Test Data Setup
```python
# Add to your app for test data
def create_test_data():
    # Create test user
    user = User(username='admin', email='admin@example.com')
    user.set_password('password123')
    db.session.add(user)
    
    # Create test category
    category = Category(name='Technology', description='Tech posts')
    db.session.add(category)
    
    # Create test post
    post = Post(
        title='Welcome to My Blog',
        content='This is the first post...',
        author=user,
        category=category,
        published=True
    )
    db.session.add(post)
    db.session.commit()
```

## 4. Unit Testing Examples
```python
import unittest
from app import app, db, User, Post

class BlogTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
    
    def test_user_registration(self):
        response = self.client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'password2': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
    
    def test_login_logout(self):
        # Create user first
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        # Test login
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)
```
''',
        "implementation_hints": [
            "Use Flask-WTF for CSRF protection on all forms",
            "Implement proper file upload validation and size limits",
            "Use SQLAlchemy relationships for clean data access",
            "Add pagination to prevent large page loads",
            "Implement proper error handling for 404 and 500 errors",
            "Use Flask-Login's @login_required decorator consistently",
            "Validate and sanitize all user input",
            "Use secure_filename() for uploaded files",
            "Implement proper URL validation for redirects",
            "Add proper database constraints and indexes"
        ],
        "bonus_features": [
            "Add comment system for blog posts",
            "Implement post tagging with many-to-many relationships",
            "Add RSS feed generation for blog posts",
            "Create email subscription system",
            "Add social media sharing buttons",
            "Implement post scheduling for future publication",
            "Add rich text editor for post content",
            "Create sitemap generation for SEO",
            "Add admin panel for user management",
            "Implement post analytics and statistics"
        ],
        "deployment_notes": '''
# Production Deployment Considerations

## Security
- Use environment variables for SECRET_KEY
- Enable HTTPS in production
- Configure proper session cookies
- Implement rate limiting
- Add input validation and sanitization

## Database
- Use PostgreSQL or MySQL instead of SQLite
- Implement database migrations with Flask-Migrate
- Set up database backups
- Configure connection pooling

## File Handling
- Use cloud storage (AWS S3) for uploaded files
- Implement image resizing and optimization
- Set up CDN for static assets

## Performance
- Enable Flask caching
- Optimize database queries
- Use Gunicorn with multiple workers
- Set up reverse proxy with Nginx
'''
    }