#!/bin/bash
# File: scripts/run_tests.sh
# Test execution script with various options

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default values
VERBOSE=false
COVERAGE=false
QUICK=false
INTEGRATION=false
UNIT=false
SPECIFIC_TEST=""
PARALLEL=false
BROWSER_TESTS=false
LINTING=false
CLEAN=false

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -v, --verbose      Enable verbose output"
    echo "  -c, --coverage     Run with coverage report"
    echo "  -q, --quick        Run only quick unit tests"
    echo "  -i, --integration  Run integration tests"
    echo "  -u, --unit         Run unit tests only"
    echo "  -t, --test TEST    Run specific test file or function"
    echo "  -p, --parallel     Run tests in parallel"
    echo "  -b, --browser      Run browser/E2E tests"
    echo "  -l, --lint         Run linting and code quality checks"
    echo "  --clean            Clean test artifacts before running"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --quick                    # Quick unit tests"
    echo "  $0 --coverage --unit          # Unit tests with coverage"
    echo "  $0 --integration --verbose    # Integration tests with verbose output"
    echo "  $0 --test tests/test_auth.py  # Run specific test file"
    echo "  $0 --lint --unit              # Linting + unit tests"
}

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

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -q|--quick)
            QUICK=true
            shift
            ;;
        -i|--integration)
            INTEGRATION=true
            shift
            ;;
        -u|--unit)
            UNIT=true
            shift
            ;;
        -t|--test)
            SPECIFIC_TEST="$2"
            shift 2
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -b|--browser)
            BROWSER_TESTS=true
            shift
            ;;
        -l|--lint)
            LINTING=true
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Check if virtual environment is activated
check_virtualenv() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_warning "Virtual environment not activated"
        if [ -f "venv/bin/activate" ]; then
            print_status "Activating virtual environment..."
            source venv/bin/activate
        else
            print_error "Virtual environment not found. Run setup_dev.sh first."
            exit 1
        fi
    fi
}

# Clean test artifacts
clean_artifacts() {
    if [ "$CLEAN" = true ]; then
        print_status "Cleaning test artifacts..."
        
        # Remove coverage files
        rm -rf .coverage htmlcov/ .pytest_cache/
        
        # Remove compiled Python files
        find . -type f -name "*.pyc" -delete
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        
        # Remove test databases
        rm -f test.db test_*.db
        
        # Clean temporary files
        rm -rf tmp/test_* /tmp/test_uploads_*
        
        print_success "Test artifacts cleaned"
    fi
}

# Setup test environment
setup_test_env() {
    print_status "Setting up test environment..."
    
    # Set test environment variables
    export FLASK_ENV=testing
    export TESTING=True
    
    # Create test directories if they don't exist
    mkdir -p logs tmp/test uploads/test
    
    # Setup test database
    if command -v createdb &> /dev/null; then
        createdb app_test 2>/dev/null || true
    fi
    
    print_success "Test environment ready"
}

# Run linting and code quality checks
run_linting() {
    if [ "$LINTING" = true ]; then
        print_status "Running linting and code quality checks..."
        
        # Black code formatting check
        if command -v black &> /dev/null; then
            print_status "Checking code formatting with Black..."
            black --check --diff app/ tests/ || {
                print_error "Code formatting issues found. Run 'black app/ tests/' to fix."
                return 1
            }
            print_success "Code formatting check passed"
        fi
        
        # Flake8 linting
        if command -v flake8 &> /dev/null; then
            print_status "Running Flake8 linting..."
            flake8 app/ tests/ || {
                print_error "Linting issues found"
                return 1
            }
            print_success "Linting check passed"
        fi
        
        # isort import sorting check
        if command -v isort &> /dev/null; then
            print_status "Checking import sorting with isort..."
            isort --check-only --diff app/ tests/ || {
                print_error "Import sorting issues found. Run 'isort app/ tests/' to fix."
                return 1
            }
            print_success "Import sorting check passed"
        fi
        
        # mypy type checking
        if command -v mypy &> /dev/null; then
            print_status "Running type checking with mypy..."
            mypy app/ || {
                print_warning "Type checking issues found"
            }
        fi
        
        # Safety dependency check
        if command -v safety &> /dev/null; then
            print_status "Checking dependencies for security issues..."
            safety check || {
                print_warning "Security issues found in dependencies"
            }
        fi
        
        print_success "Linting and code quality checks completed"
    fi
}

# Build pytest command
build_pytest_cmd() {
    local cmd="pytest"
    
    # Add verbose flag
    if [ "$VERBOSE" = true ]; then
        cmd="$cmd -v"
    fi
    
    # Add coverage
    if [ "$COVERAGE" = true ]; then
        cmd="$cmd --cov=app --cov-report=html --cov-report=term-missing"
    fi
    
    # Add parallel execution
    if [ "$PARALLEL" = true ]; then
        if command -v pytest-xdist &> /dev/null; then
            cmd="$cmd -n auto"
        else
            print_warning "pytest-xdist not installed, running sequentially"
        fi
    fi
    
    # Add test selection
    if [ "$QUICK" = true ]; then
        cmd="$cmd -m 'not slow and not integration'"
    elif [ "$UNIT" = true ]; then
        cmd="$cmd tests/unit/"
    elif [ "$INTEGRATION" = true ]; then
        cmd="$cmd tests/integration/"
    elif [ -n "$SPECIFIC_TEST" ]; then
        cmd="$cmd $SPECIFIC_TEST"
    fi
    
    echo "$cmd"
}

# Run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    
    local pytest_cmd=$(build_pytest_cmd)
    
    if [ "$UNIT" = true ] || [ "$QUICK" = true ] || [ -z "$INTEGRATION$BROWSER_TESTS" ]; then
        print_status "Executing: $pytest_cmd"
        eval $pytest_cmd
        
        if [ $? -eq 0 ]; then
            print_success "Unit tests passed"
        else
            print_error "Unit tests failed"
            return 1
        fi
    fi
}

# Run integration tests
run_integration_tests() {
    if [ "$INTEGRATION" = true ]; then
        print_status "Running integration tests..."
        
        # Start test services if needed
        if [ -f "docker-compose.test.yml" ]; then
            print_status "Starting test services..."
            docker-compose -f docker-compose.test.yml up -d
            sleep 10  # Wait for services to be ready
        fi
        
        local pytest_cmd="pytest tests/integration/"
        
        if [ "$VERBOSE" = true ]; then
            pytest_cmd="$pytest_cmd -v"
        fi
        
        if [ "$COVERAGE" = true ]; then
            pytest_cmd="$pytest_cmd --cov=app --cov-append"
        fi
        
        print_status "Executing: $pytest_cmd"
        eval $pytest_cmd
        
        local result=$?
        
        # Stop test services
        if [ -f "docker-compose.test.yml" ]; then
            print_status "Stopping test services..."
            docker-compose -f docker-compose.test.yml down
        fi
        
        if [ $result -eq 0 ]; then
            print_success "Integration tests passed"
        else
            print_error "Integration tests failed"
            return 1
        fi
    fi
}

# Run browser/E2E tests
run_browser_tests() {
    if [ "$BROWSER_TESTS" = true ]; then
        print_status "Running browser/E2E tests..."
        
        # Check if Selenium tests exist
        if [ -d "tests/e2e" ] || [ -d "tests/browser" ]; then
            # Start application for E2E tests
            print_status "Starting application for E2E tests..."
            
            # Export test configuration
            export FLASK_ENV=testing
            export TESTING=True
            
            # Start app in background
            python app.py &
            APP_PID=$!
            sleep 5  # Wait for app to start
            
            # Run browser tests
            pytest tests/e2e/ tests/browser/ -v
            local result=$?
            
            # Stop application
            kill $APP_PID 2>/dev/null || true
            
            if [ $result -eq 0 ]; then
                print_success "Browser tests passed"
            else
                print_error "Browser tests failed"
                return 1
            fi
        else
            print_warning "No browser tests found"
        fi
    fi
}

# Generate test report
generate_report() {
    if [ "$COVERAGE" = true ]; then
        print_status "Generating coverage report..."
        
        if [ -f ".coverage" ]; then
            coverage html
            coverage report
            print_success "Coverage report generated in htmlcov/"
        fi
    fi
}

# Run performance tests
run_performance_tests() {
    if [ -d "tests/performance" ]; then
        print_status "Running performance tests..."
        
        if command -v locust &> /dev/null; then
            # Run basic load test
            locust -f tests/performance/locustfile.py --headless -u 10 -r 2 -t 30s --host http://localhost:5000
        else
            print_warning "Locust not installed, skipping performance tests"
        fi
    fi
}

# Main test execution
main() {
    print_status "Starting test execution..."
    print_status "========================================"
    
    check_virtualenv
    clean_artifacts
    setup_test_env
    
    # Run linting first if requested
    if [ "$LINTING" = true ]; then
        run_linting || exit 1
    fi
    
    # Run tests based on options
    local test_failed=false
    
    run_unit_tests || test_failed=true
    run_integration_tests || test_failed=true
    run_browser_tests || test_failed=true
    
    # Generate reports
    generate_report
    
    print_status "========================================"
    
    if [ "$test_failed" = true ]; then
        print_error "Some tests failed"
        exit 1
    else
        print_success "All tests passed!"
        
        # Show summary
        if [ "$COVERAGE" = true ]; then
            print_status "Coverage summary:"
            coverage report --show-missing | tail -1
        fi
        
        print_status "Test execution completed successfully"
    fi
}

# Trap to ensure cleanup on script exit
trap 'kill $(jobs -p) 2>/dev/null || true' EXIT

# Run main function
main "$@"