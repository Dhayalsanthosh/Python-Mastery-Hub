# File: scripts/seed_data.py
# Sample data generation script for development and testing

import os
import sys
import argparse
import random
import logging
from datetime import datetime, timedelta
from faker import Faker

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import create_app, db
    from app.models import User, Role, Permission, Post, Comment, Category, Tag
    from werkzeug.security import generate_password_hash
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure you're in the virtual environment and dependencies are installed")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker()

class DataSeeder:
    """Data seeding class for generating sample data"""
    
    def __init__(self, environment='development'):
        """Initialize the seeder with environment configuration"""
        self.environment = environment
        self.app = None
        self.setup_app()
    
    def setup_app(self):
        """Setup Flask application"""
        try:
            os.environ['FLASK_ENV'] = self.environment
            self.app = create_app()
            logger.info(f"Application setup completed for environment: {self.environment}")
        except Exception as e:
            logger.error(f"Failed to setup application: {e}")
            raise
    
    def clear_existing_data(self):
        """Clear existing data from tables"""
        try:
            with self.app.app_context():
                logger.info("Clearing existing data...")
                
                # Clear tables in reverse dependency order
                db.session.execute("DELETE FROM post_tags")
                db.session.execute("DELETE FROM comments")
                db.session.execute("DELETE FROM posts")
                db.session.execute("DELETE FROM tags")
                db.session.execute("DELETE FROM categories")
                db.session.execute("DELETE FROM user_roles")
                db.session.execute("DELETE FROM role_permissions")
                db.session.execute("DELETE FROM users")
                db.session.execute("DELETE FROM roles")
                db.session.execute("DELETE FROM permissions")
                
                db.session.commit()
                logger.info("Existing data cleared successfully")
                
        except Exception as e:
            logger.error(f"Failed to clear existing data: {e}")
            db.session.rollback()
            raise
    
    def create_permissions(self):
        """Create basic permissions"""
        try:
            with self.app.app_context():
                logger.info("Creating permissions...")
                
                permissions_data = [
                    {'name': 'read_posts', 'description': 'Read posts'},
                    {'name': 'create_posts', 'description': 'Create posts'},
                    {'name': 'edit_posts', 'description': 'Edit posts'},
                    {'name': 'delete_posts', 'description': 'Delete posts'},
                    {'name': 'manage_users', 'description': 'Manage users'},
                    {'name': 'manage_roles', 'description': 'Manage roles'},
                    {'name': 'admin_access', 'description': 'Admin panel access'},
                    {'name': 'moderate_comments', 'description': 'Moderate comments'},
                ]
                
                permissions = []
                for perm_data in permissions_data:
                    permission = Permission(
                        name=perm_data['name'],
                        description=perm_data['description']
                    )
                    permissions.append(permission)
                    db.session.add(permission)
                
                db.session.commit()
                logger.info(f"Created {len(permissions)} permissions")
                return permissions
                
        except Exception as e:
            logger.error(f"Failed to create permissions: {e}")
            db.session.rollback()
            raise
    
    def create_roles(self, permissions):
        """Create roles and assign permissions"""
        try:
            with self.app.app_context():
                logger.info("Creating roles...")
                
                # Admin role - all permissions
                admin_role = Role(
                    name='admin',
                    description='Administrator with full access'
                )
                admin_role.permissions = permissions
                db.session.add(admin_role)
                
                # Editor role - content management permissions
                editor_permissions = [p for p in permissions if p.name in [
                    'read_posts', 'create_posts', 'edit_posts', 'delete_posts', 'moderate_comments'
                ]]
                editor_role = Role(
                    name='editor',
                    description='Content editor'
                )
                editor_role.permissions = editor_permissions
                db.session.add(editor_role)
                
                # Author role - basic content permissions
                author_permissions = [p for p in permissions if p.name in [
                    'read_posts', 'create_posts', 'edit_posts'
                ]]
                author_role = Role(
                    name='author',
                    description='Content author'
                )
                author_role.permissions = author_permissions
                db.session.add(author_role)
                
                # User role - read only
                user_permissions = [p for p in permissions if p.name in ['read_posts']]
                user_role = Role(
                    name='user',
                    description='Regular user'
                )
                user_role.permissions = user_permissions
                db.session.add(user_role)
                
                db.session.commit()
                logger.info("Created 4 roles with permissions")
                
                return {
                    'admin': admin_role,
                    'editor': editor_role,
                    'author': author_role,
                    'user': user_role
                }
                
        except Exception as e:
            logger.error(f"Failed to create roles: {e}")
            db.session.rollback()
            raise
    
    def create_users(self, roles, count=50):
        """Create sample users"""
        try:
            with self.app.app_context():
                logger.info(f"Creating {count} users...")
                
                users = []
                
                # Create admin user
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    password_hash=generate_password_hash('admin123'),
                    first_name='Admin',
                    last_name='User',
                    is_active=True,
                    is_verified=True,
                    created_at=fake.date_time_between(start_date='-1y', end_date='now')
                )
                admin_user.roles = [roles['admin']]
                users.append(admin_user)
                db.session.add(admin_user)
                
                # Create test users with different roles
                role_distribution = ['user'] * 40 + ['author'] * 7 + ['editor'] * 2
                random.shuffle(role_distribution)
                
                for i in range(count - 1):
                    role_name = role_distribution[i] if i < len(role_distribution) else 'user'
                    
                    user = User(
                        username=fake.unique.user_name(),
                        email=fake.unique.email(),
                        password_hash=generate_password_hash('password123'),
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        is_active=random.choice([True, True, True, False]),  # 75% active
                        is_verified=random.choice([True, True, False]),  # 66% verified
                        created_at=fake.date_time_between(start_date='-1y', end_date='now'),
                        bio=fake.text(max_nb_chars=200) if random.choice([True, False]) else None,
                        avatar_url=fake.image_url() if random.choice([True, False]) else None
                    )
                    
                    user.roles = [roles[role_name]]
                    users.append(user)
                    db.session.add(user)
                
                db.session.commit()
                logger.info(f"Created {len(users)} users")
                return users
                
        except Exception as e:
            logger.error(f"Failed to create users: {e}")
            db.session.rollback()
            raise
    
    def create_categories(self, count=10):
        """Create sample categories"""
        try:
            with self.app.app_context():
                logger.info(f"Creating {count} categories...")
                
                category_names = [
                    'Technology', 'Science', 'Health', 'Travel', 'Food',
                    'Sports', 'Entertainment', 'Business', 'Education', 'Lifestyle',
                    'Politics', 'Environment', 'Art', 'Music', 'Photography'
                ]
                
                categories = []
                for i in range(min(count, len(category_names))):
                    category = Category(
                        name=category_names[i],
                        description=fake.text(max_nb_chars=150),
                        slug=category_names[i].lower().replace(' ', '-'),
                        created_at=fake.date_time_between(start_date='-6m', end_date='now')
                    )
                    categories.append(category)
                    db.session.add(category)
                
                db.session.commit()
                logger.info(f"Created {len(categories)} categories")
                return categories
                
        except Exception as e:
            logger.error(f"Failed to create categories: {e}")
            db.session.rollback()
            raise
    
    def create_tags(self, count=30):
        """Create sample tags"""
        try:
            with self.app.app_context():
                logger.info(f"Creating {count} tags...")
                
                tag_names = [
                    'python', 'javascript', 'react', 'vue', 'angular', 'django', 'flask',
                    'machine-learning', 'ai', 'blockchain', 'cryptocurrency', 'web-development',
                    'mobile', 'ios', 'android', 'cloud', 'aws', 'docker', 'kubernetes',
                    'devops', 'security', 'database', 'postgresql', 'mongodb', 'redis',
                    'tutorial', 'guide', 'best-practices', 'tips', 'review'
                ]
                
                tags = []
                for i in range(min(count, len(tag_names))):
                    tag = Tag(
                        name=tag_names[i],
                        description=fake.text(max_nb_chars=100),
                        created_at=fake.date_time_between(start_date='-6m', end_date='now')
                    )
                    tags.append(tag)
                    db.session.add(tag)
                
                db.session.commit()
                logger.info(f"Created {len(tags)} tags")
                return tags
                
        except Exception as e:
            logger.error(f"Failed to create tags: {e}")
            db.session.rollback()
            raise
    
    def create_posts(self, users, categories, tags, count=100):
        """Create sample posts"""
        try:
            with self.app.app_context():
                logger.info(f"Creating {count} posts...")
                
                # Filter users who can create posts
                authors = [u for u in users if any(role.name in ['admin', 'editor', 'author'] for role in u.roles)]
                
                posts = []
                for i in range(count):
                    author = random.choice(authors)
                    category = random.choice(categories)
                    
                    # Generate post content
                    title = fake.sentence(nb_words=6).rstrip('.')
                    content = '\n\n'.join([fake.paragraph(nb_sentences=5) for _ in range(random.randint(3, 8))])
                    
                    post = Post(
                        title=title,
                        slug=title.lower().replace(' ', '-').replace(',', '').replace('.', ''),
                        content=content,
                        summary=fake.text(max_nb_chars=200),
                        author_id=author.id,
                        category_id=category.id,
                        is_published=random.choice([True, True, True, False]),  # 75% published
                        featured_image_url=fake.image_url() if random.choice([True, False]) else None,
                        created_at=fake.date_time_between(start_date='-6m', end_date='now'),
                        view_count=random.randint(0, 1000),
                        likes_count=random.randint(0, 100)
                    )
                    
                    # Assign random tags (1-5 tags per post)
                    post_tags = random.sample(tags, random.randint(1, min(5, len(tags))))
                    post.tags = post_tags
                    
                    posts.append(post)
                    db.session.add(post)
                
                db.session.commit()
                logger.info(f"Created {len(posts)} posts")
                return posts
                
        except Exception as e:
            logger.error(f"Failed to create posts: {e}")
            db.session.rollback()
            raise
    
    def create_comments(self, users, posts, count=500):
        """Create sample comments"""
        try:
            with self.app.app_context():
                logger.info(f"Creating {count} comments...")
                
                # Filter published posts
                published_posts = [p for p in posts if p.is_published]
                active_users = [u for u in users if u.is_active]
                
                comments = []
                for i in range(count):
                    user = random.choice(active_users)
                    post = random.choice(published_posts)
                    
                    comment = Comment(
                        content=fake.text(max_nb_chars=300),
                        author_id=user.id,
                        post_id=post.id,
                        is_approved=random.choice([True, True, True, False]),  # 75% approved
                        created_at=fake.date_time_between(start_date=post.created_at, end_date='now')
                    )
                    
                    comments.append(comment)
                    db.session.add(comment)
                
                # Create some nested comments (replies)
                for i in range(count // 10):  # 10% of comments are replies
                    parent_comment = random.choice(comments)
                    user = random.choice(active_users)
                    
                    reply = Comment(
                        content=fake.text(max_nb_chars=200),
                        author_id=user.id,
                        post_id=parent_comment.post_id,
                        parent_id=parent_comment.id,
                        is_approved=random.choice([True, True, True, False]),
                        created_at=fake.date_time_between(start_date=parent_comment.created_at, end_date='now')
                    )
                    
                    comments.append(reply)
                    db.session.add(reply)
                
                db.session.commit()
                logger.info(f"Created {len(comments)} comments")
                return comments
                
        except Exception as e:
            logger.error(f"Failed to create comments: {e}")
            db.session.rollback()
            raise
    
    def seed_all_data(self, users_count=50, posts_count=100, comments_count=500):
        """Seed all sample data"""
        try:
            logger.info("Starting complete data seeding...")
            
            # Create permissions and roles
            permissions = self.create_permissions()
            roles = self.create_roles(permissions)
            
            # Create users
            users = self.create_users(roles, users_count)
            
            # Create categories and tags
            categories = self.create_categories()
            tags = self.create_tags()
            
            # Create posts
            posts = self.create_posts(users, categories, tags, posts_count)
            
            # Create comments
            comments = self.create_comments(users, posts, comments_count)
            
            logger.info("Data seeding completed successfully!")
            logger.info(f"Created: {len(users)} users, {len(posts)} posts, {len(comments)} comments")
            
        except Exception as e:
            logger.error(f"Data seeding failed: {e}")
            raise

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(description='Sample data generation for development')
    parser.add_argument('--env', default='development',
                       choices=['development', 'staging'],
                       help='Environment to use (production not allowed)')
    parser.add_argument('--clear', action='store_true',
                       help='Clear existing data before seeding')
    parser.add_argument('--users', type=int, default=50,
                       help='Number of users to create')
    parser.add_argument('--posts', type=int, default=100,
                       help='Number of posts to create')
    parser.add_argument('--comments', type=int, default=500,
                       help='Number of comments to create')
    parser.add_argument('--component', choices=['permissions', 'roles', 'users', 'categories', 'tags', 'posts', 'comments'],
                       help='Seed only specific component')
    
    args = parser.parse_args()
    
    # Prevent seeding production data
    if args.env == 'production':
        logger.error("Data seeding is not allowed in production environment")
        sys.exit(1)
    
    # Initialize seeder
    seeder = DataSeeder(args.env)
    
    try:
        if args.clear:
            confirm = input(f"This will clear all existing data in {args.env} environment. Continue? (yes/no): ")
            if confirm.lower() != 'yes':
                logger.info("Operation cancelled")
                sys.exit(0)
            seeder.clear_existing_data()
        
        if args.component:
            # Seed specific component
            logger.info(f"Seeding component: {args.component}")
            # Add specific component seeding logic here
        else:
            # Seed all data
            seeder.seed_all_data(args.users, args.posts, args.comments)
        
        logger.info("Seeding operation completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()