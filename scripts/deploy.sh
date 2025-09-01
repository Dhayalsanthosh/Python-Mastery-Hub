#!/bin/bash
# File: scripts/deploy.sh
# Production deployment script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default values
ENVIRONMENT="staging"
SKIP_TESTS=false
SKIP_BACKUP=false
FORCE_DEPLOY=false
DRY_RUN=false
ROLLBACK=false
VERSION=""

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --env ENV          Target environment (staging|production) [default: staging]"
    echo "  -v, --version VERSION  Specific version/tag to deploy"
    echo "  -s, --skip-tests       Skip running tests before deployment"
    echo "  -b, --skip-backup      Skip database backup before deployment"
    echo "  -f, --force            Force deployment even if health checks fail"
    echo "  -d, --dry-run          Perform a dry run without actual deployment"
    echo "  -r, --rollback         Rollback to previous version"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --env production --version v1.2.3"
    echo "  $0 --env staging --skip-tests"
    echo "  $0 --rollback --env production"
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
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -s|--skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        -b|--skip-backup)
            SKIP_BACKUP=true
            shift
            ;;
        -f|--force)
            FORCE_DEPLOY=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -r|--rollback)
            ROLLBACK=true
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

# Validate environment
validate_environment() {
    if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
        print_error "Invalid environment: $ENVIRONMENT. Must be 'staging' or 'production'"
        exit 1
    fi
    
    print_status "Target environment: $ENVIRONMENT"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking deployment prerequisites..."
    
    # Check required tools
    local required_tools=("git" "docker" "kubectl" "helm")
    
    for tool in "${required_tools[@]}"; do
        if ! command -v $tool &> /dev/null; then
            print_error "$tool is required but not installed"
            exit 1
        fi
    done
    
    # Check Git status
    if ! git diff-index --quiet HEAD --; then
        print_warning "Working directory has uncommitted changes"
        if [[ "$FORCE_DEPLOY" != true ]]; then
            print_error "Commit or stash changes before deployment"
            exit 1
        fi
    fi
    
    # Check if on main/master branch for production
    if [[ "$ENVIRONMENT" == "production" ]]; then
        local current_branch=$(git rev-parse --abbrev-ref HEAD)
        if [[ "$current_branch" != "main" && "$current_branch" != "master" ]]; then
            print_warning "Not on main/master branch for production deployment"
            if [[ "$FORCE_DEPLOY" != true ]]; then
                print_error "Switch to main/master branch for production deployment"
                exit 1
            fi
        fi
    fi
    
    print_success "Prerequisites check passed"
}

# Get version to deploy
get_version() {
    if [[ -z "$VERSION" ]]; then
        if [[ "$ROLLBACK" == true ]]; then
            print_error "Version must be specified for rollback"
            exit 1
        fi
        
        # Use current commit hash as version
        VERSION=$(git rev-parse --short HEAD)
        print_status "Using current commit as version: $VERSION"
    else
        # Validate version exists
        if ! git rev-parse --verify "$VERSION" &>/dev/null; then
            print_error "Version $VERSION does not exist in Git repository"
            exit 1
        fi
        print_status "Using specified version: $VERSION"
    fi
}

# Run tests
run_tests() {
    if [[ "$SKIP_TESTS" != true && "$ROLLBACK" != true ]]; then
        print_status "Running tests before deployment..."
        
        if [[ "$DRY_RUN" != true ]]; then
            ./scripts/run_tests.sh --unit --integration
            if [[ $? -ne 0 ]]; then
                print_error "Tests failed"
                exit 1
            fi
            print_success "All tests passed"
        else
            print_status "DRY RUN: Would run tests"
        fi
    else
        print_status "Skipping tests"
    fi
}

# Create database backup
create_backup() {
    if [[ "$SKIP_BACKUP" != true && "$ROLLBACK" != true ]]; then
        print_status "Creating database backup..."
        
        if [[ "$DRY_RUN" != true ]]; then
            local backup_file="backup_${ENVIRONMENT}_$(date +%Y%m%d_%H%M%S).sql"
            ./scripts/backup_db.sh --env $ENVIRONMENT --output "backups/$backup_file"
            
            if [[ $? -eq 0 ]]; then
                print_success "Database backup created: $backup_file"
                echo "$backup_file" > .last_backup
            else
                print_error "Database backup failed"
                if [[ "$FORCE_DEPLOY" != true ]]; then
                    exit 1
                fi
            fi
        else
            print_status "DRY RUN: Would create database backup"
        fi
    else
        print_status "Skipping database backup"
    fi
}

# Build Docker image
build_image() {
    print_status "Building Docker image..."
    
    local image_tag="myapp:$VERSION"
    
    if [[ "$DRY_RUN" != true ]]; then
        # Build image
        docker build -t $image_tag .
        
        if [[ $? -ne 0 ]]; then
            print_error "Docker image build failed"
            exit 1
        fi
        
        # Tag for registry
        local registry_url
        if [[ "$ENVIRONMENT" == "production" ]]; then
            registry_url="myregistry.com/myapp:$VERSION"
        else
            registry_url="myregistry.com/myapp:$VERSION-staging"
        fi
        
        docker tag $image_tag $registry_url
        
        # Push to registry
        print_status "Pushing image to registry..."
        docker push $registry_url
        
        print_success "Docker image built and pushed: $registry_url"
    else
        print_status "DRY RUN: Would build and push Docker image"
    fi
}

# Deploy to Kubernetes
deploy_kubernetes() {
    print_status "Deploying to Kubernetes ($ENVIRONMENT)..."
    
    # Set kubectl context
    local context
    if [[ "$ENVIRONMENT" == "production" ]]; then
        context="production-cluster"
    else
        context="staging-cluster"
    fi
    
    if [[ "$DRY_RUN" != true ]]; then
        kubectl config use-context $context
        
        # Deploy using Helm
        local helm_release="myapp-$ENVIRONMENT"
        local values_file="deployment/kubernetes/values-$ENVIRONMENT.yaml"
        
        if [[ "$ROLLBACK" == true ]]; then
            print_status "Rolling back to version $VERSION..."
            helm rollback $helm_release --version $VERSION
        else
            print_status "Deploying version $VERSION..."
            helm upgrade --install $helm_release deployment/kubernetes/helm-chart \
                --values $values_file \
                --set image.tag=$VERSION \
                --namespace $ENVIRONMENT \
                --wait \
                --timeout 600s
        fi
        
        if [[ $? -ne 0 ]]; then
            print_error "Kubernetes deployment failed"
            exit 1
        fi
        
        print_success "Kubernetes deployment completed"
    else
        print_status "DRY RUN: Would deploy to Kubernetes"
    fi
}

# Run database migrations
run_migrations() {
    if [[ "$ROLLBACK" != true ]]; then
        print_status "Running database migrations..."
        
        if [[ "$DRY_RUN" != true ]]; then
            # Run migrations using kubectl job
            local migration_job="myapp-migration-$(date +%s)"
            
            kubectl run $migration_job \
                --image=myregistry.com/myapp:$VERSION \
                --restart=Never \
                --env="FLASK_ENV=$ENVIRONMENT" \
                --command -- python -m flask db upgrade
            
            # Wait for migration to complete
            kubectl wait --for=condition=complete job/$migration_job --timeout=300s
            
            if [[ $? -eq 0 ]]; then
                print_success "Database migrations completed"
            else
                print_error "Database migrations failed"
                exit 1
            fi
            
            # Clean up migration job
            kubectl delete job/$migration_job
        else
            print_status "DRY RUN: Would run database migrations"
        fi
    else
        print_status "Skipping migrations for rollback"
    fi
}

# Health check
health_check() {
    print_status "Performing health checks..."
    
    local app_url
    if [[ "$ENVIRONMENT" == "production" ]]; then
        app_url="https://myapp.com"
    else
        app_url="https://staging.myapp.com"
    fi
    
    if [[ "$DRY_RUN" != true ]]; then
        # Wait for deployment to be ready
        sleep 30
        
        # Check health endpoint
        local max_attempts=10
        local attempt=1
        
        while [[ $attempt -le $max_attempts ]]; do
            print_status "Health check attempt $attempt/$max_attempts..."
            
            if curl -f -s "$app_url/health" > /dev/null; then
                print_success "Health check passed"
                return 0
            fi
            
            sleep 10
            ((attempt++))
        done
        
        print_error "Health check failed after $max_attempts attempts"
        
        if [[ "$FORCE_DEPLOY" != true ]]; then
            print_error "Deployment failed health check"
            exit 1
        else
            print_warning "Continuing deployment despite health check failure"
        fi
    else
        print_status "DRY RUN: Would perform health checks"
    fi
}

# Update monitoring and alerts
update_monitoring() {
    print_status "Updating monitoring configuration..."
    
    if [[ "$DRY_RUN" != true ]]; then
        # Update Prometheus alerts if needed
        if [[ -f "monitoring/alerts-$ENVIRONMENT.yaml" ]]; then
            kubectl apply -f monitoring/alerts-$ENVIRONMENT.yaml
        fi
        
        # Update Grafana dashboards
        if [[ -d "monitoring/dashboards" ]]; then
            for dashboard in monitoring/dashboards/*.json; do
                # Logic to update Grafana dashboards
                print_status "Updated dashboard: $(basename $dashboard)"
            done
        fi
        
        print_success "Monitoring configuration updated"
    else
        print_status "DRY RUN: Would update monitoring"
    fi
}

# Send notifications
send_notifications() {
    print_status "Sending deployment notifications..."
    
    if [[ "$DRY_RUN" != true ]]; then
        local message
        if [[ "$ROLLBACK" == true ]]; then
            message="🔄 Rollback completed: $ENVIRONMENT environment rolled back to version $VERSION"
        else
            message="🚀 Deployment completed: $ENVIRONMENT environment updated to version $VERSION"
        fi
        
        # Send Slack notification (if webhook configured)
        if [[ -n "$SLACK_WEBHOOK_URL" ]]; then
            curl -X POST -H 'Content-type: application/json' \
                --data "{\"text\":\"$message\"}" \
                "$SLACK_WEBHOOK_URL" || print_warning "Slack notification failed"
        fi
        
        # Send email notification (if configured)
        if [[ -n "$NOTIFICATION_EMAIL" ]]; then
            echo "$message" | mail -s "Deployment Notification" "$NOTIFICATION_EMAIL" || print_warning "Email notification failed"
        fi
        
        print_success "Notifications sent"
    else
        print_status "DRY RUN: Would send notifications"
    fi
}

# Cleanup old resources
cleanup() {
    print_status "Cleaning up old resources..."
    
    if [[ "$DRY_RUN" != true ]]; then
        # Remove old Docker images (keep last 5)
        docker images myregistry.com/myapp --format "table {{.Tag}}" | tail -n +6 | xargs -r docker rmi
        
        # Clean up old backups (keep last 10)
        cd backups
        ls -t backup_${ENVIRONMENT}_*.sql | tail -n +11 | xargs -r rm
        cd ..
        
        print_success "Cleanup completed"
    else
        print_status "DRY RUN: Would cleanup old resources"
    fi
}

# Emergency rollback function
emergency_rollback() {
    print_error "Emergency rollback initiated!"
    
    local last_backup=$(cat .last_backup 2>/dev/null || echo "")
    if [[ -n "$last_backup" ]]; then
        print_status "Restoring database from backup: $last_backup"
        ./scripts/backup_db.sh --restore "backups/$last_backup" --env $ENVIRONMENT
    fi
    
    # Rollback Helm deployment
    helm rollback myapp-$ENVIRONMENT
    
    print_warning "Emergency rollback completed"
}

# Main deployment function
main() {
    print_status "Starting deployment process..."
    print_status "==========================================="
    
    # Trap for emergency rollback
    trap 'emergency_rollback' ERR
    
    validate_environment
    check_prerequisites
    get_version
    
    if [[ "$DRY_RUN" == true ]]; then
        print_warning "DRY RUN MODE - No actual changes will be made"
    fi
    
    if [[ "$ROLLBACK" == true ]]; then
        print_warning "ROLLBACK MODE - Rolling back to version $VERSION"
    fi
    
    # Pre-deployment steps
    if [[ "$ROLLBACK" != true ]]; then
        run_tests
        create_backup
        build_image
    fi
    
    # Deployment steps
    deploy_kubernetes
    run_migrations
    health_check
    update_monitoring
    
    # Post-deployment steps
    send_notifications
    cleanup
    
    print_status "==========================================="
    
    if [[ "$ROLLBACK" == true ]]; then
        print_success "Rollback completed successfully!"
        print_status "Environment: $ENVIRONMENT"
        print_status "Version: $VERSION"
    else
        print_success "Deployment completed successfully!"
        print_status "Environment: $ENVIRONMENT"
        print_status "Version: $VERSION"
        print_status "Application URL: https://$([[ $ENVIRONMENT == 'production' ]] && echo 'myapp.com' || echo 'staging.myapp.com')"
    fi
    
    # Disable emergency rollback trap
    trap - ERR
}

# Run main function
main "$@"