#!/bin/bash
# File: scripts/setup_dev.sh
# Development environment setup script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on supported OS
check_os() {
    print_status "Checking operating system..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    print_success "Operating system: $OS"
}

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Python 3.8+
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d" " -f2)
        print_success "Python found: $PYTHON_VERSION"
    else
        print_error "Python 3.8+ is required but not installed"
        exit 1
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
    else
        print_error "pip3 is required but not installed"
        exit 1
    fi
    
    # Check Node.js (for frontend)
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js found: $NODE_VERSION"
    else
        print_warning "Node.js not found - frontend development may be limited"
    fi
    
    # Check Docker
    if command -v docker &> /dev/null; then
        print_success "Docker found"
    else
        print_warning "Docker not found - containerized services will not be available"
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose found"
    else
        print_warning "Docker Compose not found"
    fi
}

# Create project directories
create_directories() {
    print_status "Creating project directories..."
    
    directories=(
        "logs"
        "uploads/dev"
        "uploads/test"
        "tmp"
        "data"
        "backups"
        "frontend/build"
        "docs"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        else
            print_status "Directory already exists: $dir"
        fi
    done
}

# Create virtual environment
setup_virtualenv() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
    print_success "pip upgraded"
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements/development.txt" ]; then
        pip install -r requirements/development.txt
        print_success "Development dependencies installed"
    else
        print_warning "requirements/development.txt not found"
    fi
    
    if [ -f "requirements/base.txt" ]; then
        pip install -r requirements/base.txt
        print_success "Base dependencies installed"
    else
        print_warning "requirements/base.txt not found"
    fi
}

# Install pre-commit hooks
setup_precommit() {
    print_status "Setting up pre-commit hooks..."
    
    if command -v pre-commit &> /dev/null; then
        if [ -f ".pre-commit-config.yaml" ]; then
            pre-commit install
            print_success "Pre-commit hooks installed"
        else
            print_warning ".pre-commit-config.yaml not found"
        fi
    else
        print_warning "pre-commit not installed - skipping hooks setup"
    fi
}

# Setup environment variables
setup_environment() {
    print_status "Setting up environment variables..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Environment file created from example"
            print_warning "Please edit .env file with your specific configuration"
        else
            # Create basic .env file
            cat > .env << EOF
# Environment
FLASK_ENV=development
FLASK_DEBUG=True

# Database
DEV_DATABASE_URL=postgresql://dev_user:dev_password@localhost:5432/app_dev

# Redis
DEV_REDIS_URL=redis://localhost:6379/0

# Security
DEV_SECRET_KEY=dev-secret-key-change-me
DEV_JWT_SECRET=jwt-dev-secret-change-me

# External APIs
EXTERNAL_API_KEY=your-api-key-here
EOF
            print_success "Basic environment file created"
            print_warning "Please edit .env file with your specific configuration"
        fi
    else
        print_status "Environment file already exists"
    fi
}

# Setup database
setup_database() {
    print_status "Setting up development database..."
    
    # Check if PostgreSQL is available
    if command -v psql &> /dev/null; then
        print_status "PostgreSQL found - setting up database"
        
        # Create database if it doesn't exist
        createdb app_dev 2>/dev/null || print_status "Database app_dev may already exist"
        createdb app_test 2>/dev/null || print_status "Database app_test may already exist"
        
        print_success "Databases setup completed"
    else
        print_warning "PostgreSQL not found - using SQLite for development"
    fi
}

# Setup Redis
setup_redis() {
    print_status "Checking Redis setup..."
    
    if command -v redis-server &> /dev/null; then
        print_success "Redis found - starting service if not running"
        
        # Check if Redis is running
        if ! pgrep -x "redis-server" > /dev/null; then
            if [[ "$OS" == "macos" ]]; then
                brew services start redis 2>/dev/null || print_warning "Could not start Redis service"
            elif [[ "$OS" == "linux" ]]; then
                sudo systemctl start redis 2>/dev/null || print_warning "Could not start Redis service"
            fi
        else
            print_success "Redis is already running"
        fi
    else
        print_warning "Redis not found - some features may not work"
    fi
}

# Initialize database schema
init_database() {
    print_status "Initializing database schema..."
    
    source venv/bin/activate
    
    if [ -f "app.py" ] || [ -f "manage.py" ]; then
        # Try to run database migrations
        if command -v flask &> /dev/null; then
            export FLASK_APP=app.py
            flask db upgrade 2>/dev/null || print_warning "Database migration failed - may need manual setup"
            print_success "Database schema initialized"
        else
            print_warning "Flask CLI not found - database needs manual initialization"
        fi
    else
        print_warning "Main application file not found - skipping database initialization"
    fi
}

# Install frontend dependencies
setup_frontend() {
    print_status "Setting up frontend dependencies..."
    
    if [ -d "frontend" ]; then
        cd frontend
        
        if command -v npm &> /dev/null; then
            npm install
            print_success "Frontend dependencies installed"
        elif command -v yarn &> /dev/null; then
            yarn install
            print_success "Frontend dependencies installed with Yarn"
        else
            print_warning "Neither npm nor yarn found - frontend setup skipped"
        fi
        
        cd ..
    else
        print_status "No frontend directory found - skipping frontend setup"
    fi
}

# Run tests to verify setup
verify_setup() {
    print_status "Verifying setup by running tests..."
    
    source venv/bin/activate
    
    if [ -f "scripts/run_tests.sh" ]; then
        bash scripts/run_tests.sh --quick
        if [ $? -eq 0 ]; then
            print_success "Setup verification passed"
        else
            print_warning "Some tests failed - setup may need adjustment"
        fi
    else
        print_status "Test script not found - skipping verification"
    fi
}

# Main setup function
main() {
    print_status "Starting development environment setup..."
    print_status "================================================"
    
    check_os
    check_dependencies
    create_directories
    setup_virtualenv
    install_python_deps
    setup_precommit
    setup_environment
    setup_database
    setup_redis
    init_database
    setup_frontend
    verify_setup
    
    print_status "================================================"
    print_success "Development environment setup completed!"
    print_status ""
    print_status "Next steps:"
    print_status "1. Review and edit .env file with your configuration"
    print_status "2. Activate virtual environment: source venv/bin/activate"
    print_status "3. Start development server: flask run"
    print_status "4. Run tests: bash scripts/run_tests.sh"
    print_status ""
    print_status "For more information, see README.md"
}

# Run main function
main "$@"