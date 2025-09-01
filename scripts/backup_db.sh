#!/bin/bash
# File: scripts/backup_db.sh
# Database backup and restore script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default values
ENVIRONMENT="development"
OUTPUT_FILE=""
RESTORE_FILE=""
COMPRESS=true
ENCRYPT=false
REMOTE_BACKUP=false
S3_BUCKET=""
RETENTION_DAYS=30
TABLES=""
EXCLUDE_TABLES=""
SCHEMA_ONLY=false
DATA_ONLY=false

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --env ENV              Environment (development|staging|production) [default: development]"
    echo "  -o, --output FILE          Output backup file path"
    echo "  -r, --restore FILE         Restore from backup file"
    echo "  -c, --compress             Compress backup file [default: true]"
    echo "  -E, --encrypt              Encrypt backup file"
    echo "  -s, --s3-backup            Upload backup to S3"
    echo "  -b, --bucket BUCKET        S3 bucket name"
    echo "  -R, --retention DAYS       Retention period in days [default: 30]"
    echo "  -t, --tables TABLES        Comma-separated list of tables to backup"
    echo "  -x, --exclude TABLES       Comma-separated list of tables to exclude"
    echo "  --schema-only              Backup schema only (no data)"
    echo "  --data-only                Backup data only (no schema)"
    echo "  -h, --help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --env production --output backup.sql --compress"
    echo "  $0 --restore backup.sql --env staging"
    echo "  $0 --env production --s3-backup --bucket myapp-backups"
    echo "  $0 --env development --tables users,orders"
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
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -r|--restore)
            RESTORE_FILE="$2"
            shift 2
            ;;
        -c|--compress)
            COMPRESS=true
            shift
            ;;
        -E|--encrypt)
            ENCRYPT=true
            shift
            ;;
        -s|--s3-backup)
            REMOTE_BACKUP=true
            shift
            ;;
        -b|--bucket)
            S3_BUCKET="$2"
            shift 2
            ;;
        -R|--retention)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        -t|--tables)
            TABLES="$2"
            shift 2
            ;;
        -x|--exclude)
            EXCLUDE_TABLES="$2"
            shift 2
            ;;
        --schema-only)
            SCHEMA_ONLY=true
            shift
            ;;
        --data-only)
            DATA_ONLY=true
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

# Load environment configuration
load_environment() {
    print_status "Loading environment configuration: $ENVIRONMENT"
    
    case $ENVIRONMENT in
        development)
            DB_HOST=${DEV_DB_HOST:-localhost}
            DB_PORT=${DEV_DB_PORT:-5432}
            DB_NAME=${DEV_DB_NAME:-app_dev}
            DB_USER=${DEV_DB_USER:-dev_user}
            DB_PASSWORD=${DEV_DB_PASSWORD:-dev_password}
            ;;
        staging)
            DB_HOST=${STAGING_DB_HOST:-staging-db.example.com}
            DB_PORT=${STAGING_DB_PORT:-5432}
            DB_NAME=${STAGING_DB_NAME:-app_staging}
            DB_USER=${STAGING_DB_USER}
            DB_PASSWORD=${STAGING_DB_PASSWORD}
            ;;
        production)
            DB_HOST=${PROD_DB_HOST}
            DB_PORT=${PROD_DB_PORT:-5432}
            DB_NAME=${PROD_DB_NAME}
            DB_USER=${PROD_DB_USER}
            DB_PASSWORD=${PROD_DB_PASSWORD}
            ;;
        *)
            print_error "Invalid environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
    
    # Validate required variables
    if [[ -z "$DB_HOST" || -z "$DB_NAME" || -z "$DB_USER" ]]; then
        print_error "Missing database configuration for environment: $ENVIRONMENT"
        exit 1
    fi
    
    print_success "Environment configuration loaded"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check PostgreSQL client
    if ! command -v pg_dump &> /dev/null; then
        print_error "pg_dump not found. Install PostgreSQL client tools."
        exit 1
    fi
    
    if ! command -v psql &> /dev/null; then
        print_error "psql not found. Install PostgreSQL client tools."
        exit 1
    fi
    
    # Check compression tools
    if [[ "$COMPRESS" == true ]]; then
        if ! command -v gzip &> /dev/null; then
            print_error "gzip not found but compression is enabled"
            exit 1
        fi
    fi
    
    # Check encryption tools
    if [[ "$ENCRYPT" == true ]]; then
        if ! command -v gpg &> /dev/null; then
            print_error "gpg not found but encryption is enabled"
            exit 1
        fi
    fi
    
    # Check AWS CLI for S3 backup
    if [[ "$REMOTE_BACKUP" == true ]]; then
        if ! command -v aws &> /dev/null; then
            print_error "aws CLI not found but S3 backup is enabled"
            exit 1
        fi
        
        if [[ -z "$S3_BUCKET" ]]; then
            print_error "S3 bucket must be specified for remote backup"
            exit 1
        fi
    fi
    
    print_success "Prerequisites check passed"
}

# Test database connection
test_connection() {
    print_status "Testing database connection..."
    
    export PGPASSWORD="$DB_PASSWORD"
    
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" &>/dev/null; then
        print_success "Database connection successful"
    else
        print_error "Failed to connect to database"
        exit 1
    fi
}

# Create backup directory
create_backup_dir() {
    local backup_dir="backups"
    
    if [[ ! -d "$backup_dir" ]]; then
        mkdir -p "$backup_dir"
        print_success "Created backup directory: $backup_dir"
    fi
}

# Generate backup filename
generate_backup_filename() {
    if [[ -z "$OUTPUT_FILE" ]]; then
        local timestamp=$(date +%Y%m%d_%H%M%S)
        OUTPUT_FILE="backups/${DB_NAME}_${ENVIRONMENT}_${timestamp}.sql"
        
        if [[ "$COMPRESS" == true ]]; then
            OUTPUT_FILE="${OUTPUT_FILE}.gz"
        fi
        
        if [[ "$ENCRYPT" == true ]]; then
            OUTPUT_FILE="${OUTPUT_FILE}.gpg"
        fi
    fi
    
    print_status "Backup file: $OUTPUT_FILE"
}

# Build pg_dump command
build_dump_command() {
    local cmd="pg_dump"
    cmd="$cmd -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
    cmd="$cmd --verbose --no-password"
    
    # Schema or data only options
    if [[ "$SCHEMA_ONLY" == true ]]; then
        cmd="$cmd --schema-only"
    elif [[ "$DATA_ONLY" == true ]]; then
        cmd="$cmd --data-only"
    fi
    
    # Table selection
    if [[ -n "$TABLES" ]]; then
        IFS=',' read -ra TABLE_ARRAY <<< "$TABLES"
        for table in "${TABLE_ARRAY[@]}"; do
            cmd="$cmd --table=$table"
        done
    fi
    
    # Exclude tables
    if [[ -n "$EXCLUDE_TABLES" ]]; then
        IFS=',' read -ra EXCLUDE_ARRAY <<< "$EXCLUDE_TABLES"
        for table in "${EXCLUDE_ARRAY[@]}"; do
            cmd="$cmd --exclude-table=$table"
        done
    fi
    
    echo "$cmd"
}

# Create database backup
create_backup() {
    print_status "Creating database backup..."
    
    export PGPASSWORD="$DB_PASSWORD"
    
    create_backup_dir
    generate_backup_filename
    
    local dump_cmd=$(build_dump_command)
    local output_cmd=""
    
    # Build output pipeline
    if [[ "$COMPRESS" == true && "$ENCRYPT" == true ]]; then
        output_cmd="| gzip | gpg --symmetric --cipher-algo AES256 --output $OUTPUT_FILE"
    elif [[ "$COMPRESS" == true ]]; then
        output_cmd="| gzip > $OUTPUT_FILE"
    elif [[ "$ENCRYPT" == true ]]; then
        output_cmd="| gpg --symmetric --cipher-algo AES256 --output $OUTPUT_FILE"
    else
        output_cmd="> $OUTPUT_FILE"
    fi
    
    # Execute backup
    print_status "Executing: $dump_cmd $output_cmd"
    eval "$dump_cmd $output_cmd"
    
    if [[ $? -eq 0 ]]; then
        local file_size=$(du -h "$OUTPUT_FILE" | cut -f1)
        print_success "Backup created successfully: $OUTPUT_FILE ($file_size)"
        
        # Create metadata file
        create_backup_metadata
        
        # Upload to S3 if requested
        if [[ "$REMOTE_BACKUP" == true ]]; then
            upload_to_s3
        fi
        
        # Clean old backups
        cleanup_old_backups
        
    else
        print_error "Backup creation failed"
        exit 1
    fi
}

# Create backup metadata
create_backup_metadata() {
    local metadata_file="${OUTPUT_FILE}.meta"
    
    cat > "$metadata_file" << EOF
{
    "backup_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "environment": "$ENVIRONMENT",
    "database_name": "$DB_NAME",
    "database_host": "$DB_HOST",
    "backup_type": "$([[ $SCHEMA_ONLY == true ]] && echo 'schema' || [[ $DATA_ONLY == true ]] && echo 'data' || echo 'full')",
    "compressed": $COMPRESS,
    "encrypted": $ENCRYPT,
    "tables": "${TABLES:-all}",
    "excluded_tables": "${EXCLUDE_TABLES:-none}",
    "file_size": "$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE")",
    "checksum": "$(sha256sum "$OUTPUT_FILE" | cut -d' ' -f1)"
}
EOF
    
    print_success "Backup metadata created: $metadata_file"
}

# Upload backup to S3
upload_to_s3() {
    print_status "Uploading backup to S3..."
    
    local s3_path="s3://$S3_BUCKET/$(basename "$OUTPUT_FILE")"
    local metadata_path="s3://$S3_BUCKET/$(basename "${OUTPUT_FILE}.meta")"
    
    # Upload backup file
    aws s3 cp "$OUTPUT_FILE" "$s3_path"
    if [[ $? -eq 0 ]]; then
        print_success "Backup uploaded to: $s3_path"
    else
        print_error "Failed to upload backup to S3"
        return 1
    fi
    
    # Upload metadata file
    aws s3 cp "${OUTPUT_FILE}.meta" "$metadata_path"
    if [[ $? -eq 0 ]]; then
        print_success "Metadata uploaded to: $metadata_path"
    else
        print_warning "Failed to upload metadata to S3"
    fi
}

# Restore database from backup
restore_backup() {
    print_status "Restoring database from backup: $RESTORE_FILE"
    
    if [[ ! -f "$RESTORE_FILE" ]]; then
        print_error "Backup file not found: $RESTORE_FILE"
        exit 1
    fi
    
    export PGPASSWORD="$DB_PASSWORD"
    
    # Confirm restore operation
    print_warning "This will overwrite the existing database: $DB_NAME"
    read -p "Are you sure you want to continue? (yes/no): " confirm
    
    if [[ "$confirm" != "yes" ]]; then
        print_status "Restore operation cancelled"
        exit 0
    fi
    
    # Determine file type and build restore command
    local restore_cmd=""
    
    if [[ "$RESTORE_FILE" == *.gpg ]]; then
        if [[ "$RESTORE_FILE" == *.sql.gz.gpg ]]; then
            restore_cmd="gpg --decrypt $RESTORE_FILE | gunzip | psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
        else
            restore_cmd="gpg --decrypt $RESTORE_FILE | psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
        fi
    elif [[ "$RESTORE_FILE" == *.gz ]]; then
        restore_cmd="gunzip -c $RESTORE_FILE | psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
    else
        restore_cmd="psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME < $RESTORE_FILE"
    fi
    
    # Execute restore
    print_status "Executing restore..."
    eval "$restore_cmd"
    
    if [[ $? -eq 0 ]]; then
        print_success "Database restore completed successfully"
    else
        print_error "Database restore failed"
        exit 1
    fi
}

# Clean up old backups
cleanup_old_backups() {
    print_status "Cleaning up old backups (retention: $RETENTION_DAYS days)..."
    
    # Local cleanup
    find backups/ -name "${DB_NAME}_${ENVIRONMENT}_*.sql*" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    find backups/ -name "${DB_NAME}_${ENVIRONMENT}_*.meta" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    
    # S3 cleanup if remote backup is enabled
    if [[ "$REMOTE_BACKUP" == true ]]; then
        local cutoff_date=$(date -d "$RETENTION_DAYS days ago" +%Y-%m-%d)
        aws s3 ls "s3://$S3_BUCKET/" | while read -r line; do
            local file_date=$(echo "$line" | awk '{print $1}')
            local file_name=$(echo "$line" | awk '{print $4}')
            
            if [[ "$file_date" < "$cutoff_date" && "$file_name" == *"${DB_NAME}_${ENVIRONMENT}"* ]]; then
                aws s3 rm "s3://$S3_BUCKET/$file_name"
                print_status "Removed old S3 backup: $file_name"
            fi
        done
    fi
    
    print_success "Old backups cleaned up"
}

# Main function
main() {
    print_status "Database backup/restore utility"
    print_status "==============================="
    
    load_environment
    check_prerequisites
    test_connection
    
    if [[ -n "$RESTORE_FILE" ]]; then
        restore_backup
    else
        create_backup
    fi
    
    print_status "==============================="
    print_success "Operation completed successfully"
}

# Run main function
main "$@"