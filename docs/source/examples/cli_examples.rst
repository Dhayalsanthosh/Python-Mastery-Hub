.. File: docs/source/examples/cli_examples.rst

CLI Examples
============

The Python Mastery Hub Command Line Interface (CLI) provides powerful tools for 
automation, bulk operations, and system administration. These examples demonstrate 
practical usage scenarios for educators, administrators, and developers.

.. note::
   **Prerequisites**: Ensure you have Python Mastery Hub installed and configured. 
   See :doc:`../tutorials/getting_started` for installation instructions.

Quick Reference
---------------

Essential CLI commands for daily operations:

.. code-block:: bash

   # Server management
   pmh web start --port 8000 --workers 4
   pmh web status
   pmh web restart
   
   # Database operations
   pmh db migrate
   pmh db backup --output backup.sql
   pmh db status
   
   # User management
   pmh users create --username john --email john@example.com
   pmh users list --role instructor
   pmh users update john --role admin
   
   # Content management
   pmh courses list
   pmh courses import course-directory/
   pmh courses publish python-basics

User Management Examples
-----------------------

Bulk User Creation
~~~~~~~~~~~~~~~~~

**Use Case**: Creating multiple user accounts from a CSV file for a new semester.

**CSV Format** (``students.csv``):

.. code-block:: text

   username,email,first_name,last_name,role,course_codes
   john.doe,john.doe@university.edu,John,Doe,student,"CS101,CS102"
   jane.smith,jane.smith@university.edu,Jane,Smith,student,"CS101"
   prof.wilson,wilson@university.edu,Robert,Wilson,instructor,"CS101,CS102"

**Bash Script** (``bulk-create-users.sh``):

.. code-block:: bash

   #!/bin/bash
   # File: scripts/bulk-create-users.sh
   
   set -e
   
   CSV_FILE="$1"
   LOG_FILE="user-creation-$(date +%Y%m%d_%H%M%S).log"
   
   if [ -z "$CSV_FILE" ]; then
       echo "Usage: $0 <csv_file>"
       exit 1
   fi
   
   echo "Starting bulk user creation from $CSV_FILE" | tee -a "$LOG_FILE"
   echo "=========================================" | tee -a "$LOG_FILE"
   
   # Skip header line and process each user
   tail -n +2 "$CSV_FILE" | while IFS=',' read -r username email first_name last_name role course_codes; do
       # Remove quotes from course_codes
       course_codes=$(echo "$course_codes" | tr -d '"')
       
       echo "Creating user: $username ($email)" | tee -a "$LOG_FILE"
       
       # Create user account
       if pmh users create \
           --username "$username" \
           --email "$email" \
           --first-name "$first_name" \
           --last-name "$last_name" \
           --role "$role" \
           --send-welcome-email 2>> "$LOG_FILE"; then
           
           echo "✅ User $username created successfully" | tee -a "$LOG_FILE"
           
           # Enroll in courses if specified
           if [ -n "$course_codes" ]; then
               IFS=',' read -ra COURSES <<< "$course_codes"
               for course_code in "${COURSES[@]}"; do
                   course_code=$(echo "$course_code" | xargs)  # Trim whitespace
                   echo "  Enrolling $username in $course_code..." | tee -a "$LOG_FILE"
                   
                   if pmh courses enroll --username "$username" --course-code "$course_code" 2>> "$LOG_FILE"; then
                       echo "  ✅ Enrolled in $course_code" | tee -a "$LOG_FILE"
                   else
                       echo "  ❌ Failed to enroll in $course_code" | tee -a "$LOG_FILE"
                   fi
               done
           fi
       else
           echo "❌ Failed to create user $username" | tee -a "$LOG_FILE"
       fi
       
       echo "" | tee -a "$LOG_FILE"
   done
   
   echo "Bulk user creation completed. Check $LOG_FILE for details."

**Usage**:

.. code-block:: bash

   chmod +x bulk-create-users.sh
   ./bulk-create-users.sh students.csv

Password Reset Automation
~~~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Reset passwords for multiple users and send secure reset links.

.. code-block:: bash

   #!/bin/bash
   # File: scripts/mass-password-reset.sh
   
   USERS_FILE="$1"
   
   if [ -z "$USERS_FILE" ]; then
       echo "Usage: $0 <users_file>"
       echo "File should contain one username per line"
       exit 1
   fi
   
   echo "Processing password resets..."
   
   while read -r username; do
       # Skip empty lines and comments
       [[ -z "$username" || "$username" =~ ^# ]] && continue
       
       echo "Resetting password for: $username"
       
       if pmh users reset-password "$username" --send-email; then
           echo "✅ Password reset sent to $username"
       else
           echo "❌ Failed to reset password for $username"
       fi
   done < "$USERS_FILE"
   
   echo "Password reset process completed."

**Sample users file** (``reset-users.txt``):

.. code-block:: text

   # Users who forgot their passwords
   john.doe
   jane.smith
   student123
   
   # Commented users are skipped
   # old.account

User Activity Report
~~~~~~~~~~~~~~~~~~~

**Use Case**: Generate a comprehensive report of user activity and engagement.

.. code-block:: bash

   #!/bin/bash
   # File: scripts/user-activity-report.sh
   
   DAYS_BACK=${1:-30}
   OUTPUT_DIR="reports/$(date +%Y%m%d)"
   
   mkdir -p "$OUTPUT_DIR"
   
   echo "Generating user activity report for last $DAYS_BACK days..."
   
   # Generate overall activity summary
   pmh analytics users \
       --days "$DAYS_BACK" \
       --format csv \
       --output "$OUTPUT_DIR/user-activity-summary.csv"
   
   # Generate detailed reports by role
   for role in student instructor admin; do
       echo "Generating $role activity report..."
       
       pmh users list \
           --role "$role" \
           --active-since "$DAYS_BACK days ago" \
           --format csv \
           --output "$OUTPUT_DIR/$role-activity.csv"
   done
   
   # Generate course enrollment statistics
   pmh courses analytics \
       --enrollment-stats \
       --days "$DAYS_BACK" \
       --format json \
       --output "$OUTPUT_DIR/enrollment-stats.json"
   
   # Create summary report
   cat > "$OUTPUT_DIR/README.md" << EOF
   # User Activity Report - $(date)
   
   This report covers user activity for the last $DAYS_BACK days.
   
   ## Files Generated:
   - \`user-activity-summary.csv\`: Overall user activity metrics
   - \`student-activity.csv\`: Student-specific activity data
   - \`instructor-activity.csv\`: Instructor activity data
   - \`admin-activity.csv\`: Administrator activity data
   - \`enrollment-stats.json\`: Course enrollment statistics
   
   ## Usage:
   Import CSV files into Excel or Google Sheets for analysis.
   Use JSON files for programmatic processing.
   EOF
   
   echo "Report generated in: $OUTPUT_DIR"

Content Management Examples
--------------------------

Course Import and Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Import multiple courses from a structured directory and validate content.

**Directory Structure**:

.. code-block:: text

   courses/
   ├── python-basics/
   │   ├── course.yaml
   │   ├── module-1/
   │   │   ├── lesson-1.md
   │   │   ├── lesson-2.md
   │   │   └── exercises/
   │   │       ├── exercise-1.py
   │   │       └── exercise-2.py
   │   └── module-2/
   └── advanced-python/
       ├── course.yaml
       └── modules/

**Import Script**:

.. code-block:: bash

   #!/bin/bash
   # File: scripts/import-courses.sh
   
   COURSES_DIR="$1"
   VALIDATION_LOG="course-validation-$(date +%Y%m%d_%H%M%S).log"
   
   if [ -z "$COURSES_DIR" ]; then
       echo "Usage: $0 <courses_directory>"
       exit 1
   fi
   
   echo "Starting course import from $COURSES_DIR" | tee "$VALIDATION_LOG"
   echo "============================================" | tee -a "$VALIDATION_LOG"
   
   # Find all course directories (containing course.yaml)
   find "$COURSES_DIR" -name "course.yaml" -type f | while read -r course_file; do
       course_dir=$(dirname "$course_file")
       course_name=$(basename "$course_dir")
       
       echo "Processing course: $course_name" | tee -a "$VALIDATION_LOG"
       echo "Course directory: $course_dir" | tee -a "$VALIDATION_LOG"
       
       # Validate course structure
       echo "  Validating course structure..." | tee -a "$VALIDATION_LOG"
       if pmh courses validate "$course_dir" 2>&1 | tee -a "$VALIDATION_LOG"; then
           echo "  ✅ Course structure is valid" | tee -a "$VALIDATION_LOG"
           
           # Import the course
           echo "  Importing course..." | tee -a "$VALIDATION_LOG"
           if pmh courses import "$course_dir" --format directory 2>&1 | tee -a "$VALIDATION_LOG"; then
               echo "  ✅ Course imported successfully" | tee -a "$VALIDATION_LOG"
               
               # Optionally publish the course
               if [ "$AUTO_PUBLISH" = "true" ]; then
                   echo "  Publishing course..." | tee -a "$VALIDATION_LOG"
                   if pmh courses publish "$course_name" 2>&1 | tee -a "$VALIDATION_LOG"; then
                       echo "  ✅ Course published" | tee -a "$VALIDATION_LOG"
                   else
                       echo "  ❌ Failed to publish course" | tee -a "$VALIDATION_LOG"
                   fi
               fi
           else
               echo "  ❌ Failed to import course" | tee -a "$VALIDATION_LOG"
           fi
       else
           echo "  ❌ Course validation failed" | tee -a "$VALIDATION_LOG"
       fi
       
       echo "" | tee -a "$VALIDATION_LOG"
   done
   
   echo "Course import process completed. Check $VALIDATION_LOG for details."

**Usage**:

.. code-block:: bash

   # Import courses without auto-publishing
   ./import-courses.sh ./courses
   
   # Import and auto-publish valid courses
   AUTO_PUBLISH=true ./import-courses.sh ./courses

Exercise Testing Automation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Automatically test all exercises in a course to ensure they work correctly.

.. code-block:: bash

   #!/bin/bash
   # File: scripts/test-exercises.sh
   
   COURSE_ID="$1"
   TEST_RESULTS_DIR="test-results/$(date +%Y%m%d_%H%M%S)"
   
   if [ -z "$COURSE_ID" ]; then
       echo "Usage: $0 <course_id>"
       exit 1
   fi
   
   mkdir -p "$TEST_RESULTS_DIR"
   
   echo "Testing all exercises in course: $COURSE_ID"
   echo "============================================"
   
   # Get list of all exercises in the course
   pmh exercises list --course-id "$COURSE_ID" --format json > "$TEST_RESULTS_DIR/exercises.json"
   
   # Parse exercises and test each one
   python3 << EOF
   import json
   import subprocess
   import sys
   
   with open('$TEST_RESULTS_DIR/exercises.json', 'r') as f:
       exercises = json.load(f)
   
   total_exercises = len(exercises['data'])
   passed_tests = 0
   failed_tests = 0
   
   print(f"Found {total_exercises} exercises to test")
   print()
   
   for exercise in exercises['data']:
       exercise_id = exercise['id']
       exercise_title = exercise['title']
       
       print(f"Testing: {exercise_title} (ID: {exercise_id})")
       
       # Run the exercise test
       result = subprocess.run([
           'pmh', 'exercises', 'test', str(exercise_id), '--auto-grade'
       ], capture_output=True, text=True)
       
       if result.returncode == 0:
           print(f"  ✅ PASSED")
           passed_tests += 1
       else:
           print(f"  ❌ FAILED: {result.stderr.strip()}")
           failed_tests += 1
           
           # Save failure details
           with open(f'$TEST_RESULTS_DIR/failed_{exercise_id}.log', 'w') as f:
               f.write(f"Exercise: {exercise_title}\n")
               f.write(f"ID: {exercise_id}\n")
               f.write(f"Error Output:\n{result.stderr}\n")
               f.write(f"Standard Output:\n{result.stdout}\n")
       
       print()
   
   print("="*50)
   print(f"Test Summary:")
   print(f"  Total Exercises: {total_exercises}")
   print(f"  Passed: {passed_tests}")
   print(f"  Failed: {failed_tests}")
   print(f"  Success Rate: {(passed_tests/total_exercises)*100:.1f}%")
   
   if failed_tests > 0:
       print(f"  Check $TEST_RESULTS_DIR/ for failure details")
       sys.exit(1)
   else:
       print("  🎉 All exercises passed!")
   EOF

Database Management Examples
---------------------------

Automated Backup System
~~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Set up automated daily backups with rotation and cloud storage.

.. code-block:: bash

   #!/bin/bash
   # File: scripts/automated-backup.sh
   
   # Configuration
   BACKUP_DIR="/backup/pmh"
   RETENTION_DAYS=30
   S3_BUCKET="pmh-backups"
   NOTIFICATION_EMAIL="admin@school.edu"
   
   # Create backup directory
   mkdir -p "$BACKUP_DIR"
   
   # Generate backup filename
   TIMESTAMP=$(date +%Y%m%d_%H%M%S)
   BACKUP_FILE="$BACKUP_DIR/pmh_backup_$TIMESTAMP.sql"
   LOG_FILE="$BACKUP_DIR/backup_$TIMESTAMP.log"
   
   echo "Starting automated backup at $(date)" | tee "$LOG_FILE"
   echo "========================================" | tee -a "$LOG_FILE"
   
   # Create database backup
   echo "Creating database backup..." | tee -a "$LOG_FILE"
   if pmh db backup --output "$BACKUP_FILE" --compress 2>&1 | tee -a "$LOG_FILE"; then
       echo "✅ Database backup created: $BACKUP_FILE.gz" | tee -a "$LOG_FILE"
       
       # Upload to cloud storage
       if command -v aws &> /dev/null; then
           echo "Uploading to S3..." | tee -a "$LOG_FILE"
           if aws s3 cp "$BACKUP_FILE.gz" "s3://$S3_BUCKET/database/" 2>&1 | tee -a "$LOG_FILE"; then
               echo "✅ Backup uploaded to S3" | tee -a "$LOG_FILE"
           else
               echo "❌ Failed to upload to S3" | tee -a "$LOG_FILE"
           fi
       fi
       
       # Backup user uploads
       echo "Backing up user uploads..." | tee -a "$LOG_FILE"
       UPLOADS_BACKUP="$BACKUP_DIR/uploads_$TIMESTAMP.tar.gz"
       if pmh files backup --output "$UPLOADS_BACKUP" 2>&1 | tee -a "$LOG_FILE"; then
           echo "✅ User uploads backed up" | tee -a "$LOG_FILE"
           
           # Upload uploads backup
           if command -v aws &> /dev/null; then
               aws s3 cp "$UPLOADS_BACKUP" "s3://$S3_BUCKET/uploads/" 2>&1 | tee -a "$LOG_FILE"
           fi
       else
           echo "❌ Failed to backup user uploads" | tee -a "$LOG_FILE"
       fi
       
       # Clean up old backups
       echo "Cleaning up old backups..." | tee -a "$LOG_FILE"
       find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
       find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
       find "$BACKUP_DIR" -name "*.log" -mtime +$RETENTION_DAYS -delete
       
       echo "✅ Backup completed successfully at $(date)" | tee -a "$LOG_FILE"
       
       # Send success notification
       if command -v mail &> /dev/null; then
           echo "Backup completed successfully" | mail -s "PMH Backup Success - $TIMESTAMP" "$NOTIFICATION_EMAIL"
       fi
       
   else
       echo "❌ Database backup failed" | tee -a "$LOG_FILE"
       
       # Send failure notification
       if command -v mail &> /dev/null; then
           cat "$LOG_FILE" | mail -s "PMH Backup FAILED - $TIMESTAMP" "$NOTIFICATION_EMAIL"
       fi
       
       exit 1
   fi

**Crontab entry** for daily backups at 3 AM:

.. code-block:: bash

   # Add to crontab with: crontab -e
   0 3 * * * /home/pmhuser/scripts/automated-backup.sh

Database Migration with Rollback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Safely run database migrations with automatic rollback on failure.

.. code-block:: bash

   #!/bin/bash
   # File: scripts/safe-migrate.sh
   
   set -e
   
   # Configuration
   BACKUP_DIR="/backup/pre-migration"
   LOG_FILE="migration-$(date +%Y%m%d_%H%M%S).log"
   
   mkdir -p "$BACKUP_DIR"
   
   echo "Starting safe database migration at $(date)" | tee "$LOG_FILE"
   echo "=============================================" | tee -a "$LOG_FILE"
   
   # Create pre-migration backup
   echo "Creating pre-migration backup..." | tee -a "$LOG_FILE"
   BACKUP_FILE="$BACKUP_DIR/pre_migration_$(date +%Y%m%d_%H%M%S).sql"
   
   if pmh db backup --output "$BACKUP_FILE" 2>&1 | tee -a "$LOG_FILE"; then
       echo "✅ Pre-migration backup created: $BACKUP_FILE" | tee -a "$LOG_FILE"
   else
       echo "❌ Failed to create backup. Aborting migration." | tee -a "$LOG_FILE"
       exit 1
   fi
   
   # Check current migration status
   echo "Checking current migration status..." | tee -a "$LOG_FILE"
   pmh db migrate --status 2>&1 | tee -a "$LOG_FILE"
   
   # Run migrations
   echo "Running database migrations..." | tee -a "$LOG_FILE"
   if pmh db migrate 2>&1 | tee -a "$LOG_FILE"; then
       echo "✅ Migrations completed successfully" | tee -a "$LOG_FILE"
       
       # Test application health after migration
       echo "Testing application health..." | tee -a "$LOG_FILE"
       if pmh web health-check 2>&1 | tee -a "$LOG_FILE"; then
           echo "✅ Application health check passed" | tee -a "$LOG_FILE"
           echo "Migration completed successfully!" | tee -a "$LOG_FILE"
       else
           echo "❌ Application health check failed after migration" | tee -a "$LOG_FILE"
           echo "Rolling back to pre-migration state..." | tee -a "$LOG_FILE"
           
           # Restore from backup
           if pmh db restore "$BACKUP_FILE" 2>&1 | tee -a "$LOG_FILE"; then
               echo "✅ Database restored from backup" | tee -a "$LOG_FILE"
           else
               echo "❌ CRITICAL: Failed to restore database!" | tee -a "$LOG_FILE"
               exit 1
           fi
       fi
   else
       echo "❌ Migration failed. Rolling back..." | tee -a "$LOG_FILE"
       
       # Restore from backup
       if pmh db restore "$BACKUP_FILE" 2>&1 | tee -a "$LOG_FILE"; then
           echo "✅ Database restored from backup" | tee -a "$LOG_FILE"
       else
           echo "❌ CRITICAL: Failed to restore database!" | tee -a "$LOG_FILE"
           exit 1
       fi
   fi

System Monitoring Examples
-------------------------

Health Check and Alerting
~~~~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Monitor system health and send alerts when issues are detected.

.. code-block:: bash

   #!/bin/bash
   # File: scripts/health-monitor.sh
   
   # Configuration
   ALERT_EMAIL="admin@school.edu"
   SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
   LOG_FILE="/var/log/pmh/health-monitor.log"
   
   # Ensure log directory exists
   sudo mkdir -p "$(dirname "$LOG_FILE")"
   
   # Function to send alerts
   send_alert() {
       local severity="$1"
       local message="$2"
       local timestamp="$(date)"
       
       echo "[$timestamp] $severity: $message" | sudo tee -a "$LOG_FILE"
       
       # Send email alert
       if command -v mail &> /dev/null; then
           echo "$message" | mail -s "PMH Alert: $severity" "$ALERT_EMAIL"
       fi
       
       # Send Slack notification
       if [ -n "$SLACK_WEBHOOK_URL" ] && command -v curl &> /dev/null; then
           curl -X POST -H 'Content-type: application/json' \
               --data "{\"text\":\"🚨 PMH $severity: $message\"}" \
               "$SLACK_WEBHOOK_URL"
       fi
   }
   
   # Check web server health
   echo "Checking web server health..."
   if ! pmh web status >/dev/null 2>&1; then
       send_alert "CRITICAL" "Web server is not running"
       exit 1
   fi
   
   # Check database connectivity
   echo "Checking database connectivity..."
   if ! pmh db status >/dev/null 2>&1; then
       send_alert "CRITICAL" "Database is not accessible"
       exit 1
   fi
   
   # Check API endpoints
   echo "Checking API endpoints..."
   if ! curl -f http://localhost:8000/health >/dev/null 2>&1; then
       send_alert "CRITICAL" "API health endpoint is not responding"
       exit 1
   fi
   
   # Check disk space
   echo "Checking disk space..."
   DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
   if [ "$DISK_USAGE" -gt 85 ]; then
       send_alert "WARNING" "Disk usage is high: ${DISK_USAGE}%"
   fi
   
   # Check memory usage
   echo "Checking memory usage..."
   MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
   if [ "$MEMORY_USAGE" -gt 90 ]; then
       send_alert "WARNING" "Memory usage is high: ${MEMORY_USAGE}%"
   fi
   
   # Check active user count
   echo "Checking active users..."
   ACTIVE_USERS=$(pmh analytics active-users --format json | jq '.count')
   if [ "$ACTIVE_USERS" -gt 1000 ]; then
       send_alert "INFO" "High user activity: $ACTIVE_USERS active users"
   fi
   
   echo "Health check completed successfully"

**Crontab entry** for monitoring every 5 minutes:

.. code-block:: bash

   # Add to crontab
   */5 * * * * /home/pmhuser/scripts/health-monitor.sh

Performance Monitoring
~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Collect and analyze performance metrics over time.

.. code-block:: bash

   #!/bin/bash
   # File: scripts/performance-monitor.sh
   
   METRICS_DIR="/var/log/pmh/metrics"
   TIMESTAMP=$(date +%Y%m%d_%H%M%S)
   
   mkdir -p "$METRICS_DIR"
   
   # Collect system metrics
   {
       echo "timestamp,cpu_percent,memory_percent,disk_percent,load_avg"
       echo "$TIMESTAMP,$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1),$(free | awk 'NR==2{printf "%.1f", $3*100/$2}'),$(df / | awk 'NR==2 {print $5}' | sed 's/%//'),$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')"
   } >> "$METRICS_DIR/system_metrics.csv"
   
   # Collect application metrics
   pmh analytics metrics \
       --format json \
       --output "$METRICS_DIR/app_metrics_$TIMESTAMP.json"
   
   # Collect database performance
   pmh db analyze \
       --slow-queries \
       --format json \
       --output "$METRICS_DIR/db_performance_$TIMESTAMP.json"
   
   # Generate daily summary (if it's midnight)
   if [ "$(date +%H%M)" = "0000" ]; then
       echo "Generating daily performance summary..."
       
       python3 << EOF
   import pandas as pd
   import json
   import glob
   from datetime import datetime, timedelta
   
   # Load system metrics
   df = pd.read_csv('$METRICS_DIR/system_metrics.csv')
   df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d_%H%M%S')
   
   # Filter last 24 hours
   yesterday = datetime.now() - timedelta(hours=24)
   recent_data = df[df['timestamp'] > yesterday]
   
   # Calculate summary statistics
   summary = {
       'date': datetime.now().strftime('%Y-%m-%d'),
       'avg_cpu': recent_data['cpu_percent'].mean(),
       'max_cpu': recent_data['cpu_percent'].max(),
       'avg_memory': recent_data['memory_percent'].mean(),
       'max_memory': recent_data['memory_percent'].max(),
       'avg_disk': recent_data['disk_percent'].mean(),
       'avg_load': recent_data['load_avg'].mean(),
       'max_load': recent_data['load_avg'].max()
   }
   
   # Save daily summary
   with open('$METRICS_DIR/daily_summary.json', 'w') as f:
       json.dump(summary, f, indent=2)
   
   print(f"Daily summary generated for {summary['date']}")
   EOF
   fi

Analytics and Reporting Examples
-------------------------------

Student Progress Report
~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Generate comprehensive progress reports for instructors and administrators.

.. code-block:: bash

   #!/bin/bash
   # File: scripts/progress-report.sh
   
   COURSE_ID="$1"
   REPORT_TYPE="${2:-weekly}"  # daily, weekly, monthly
   OUTPUT_DIR="reports/$(date +%Y%m%d)"
   
   if [ -z "$COURSE_ID" ]; then
       echo "Usage: $0 <course_id> [report_type]"
       echo "Report types: daily, weekly, monthly"
       exit 1
   fi
   
   mkdir -p "$OUTPUT_DIR"
   
   echo "Generating $REPORT_TYPE progress report for course $COURSE_ID"
   echo "============================================================="
   
   # Get course information
   pmh courses info "$COURSE_ID" --format json > "$OUTPUT_DIR/course_info.json"
   COURSE_NAME=$(jq -r '.title' "$OUTPUT_DIR/course_info.json")
   
   # Generate enrollment statistics
   pmh courses analytics "$COURSE_ID" \
       --enrollment-stats \
       --format csv \
       --output "$OUTPUT_DIR/enrollment_stats.csv"
   
   # Generate individual student progress
   pmh courses progress "$COURSE_ID" \
       --detailed \
       --format csv \
       --output "$OUTPUT_DIR/student_progress.csv"
   
   # Generate exercise completion rates
   pmh exercises analytics \
       --course-id "$COURSE_ID" \
       --completion-rates \
       --format json \
       --output "$OUTPUT_DIR/exercise_completion.json"
   
   # Generate comprehensive HTML report
   python3 << EOF
   import pandas as pd
   import json
   import matplotlib.pyplot as plt
   import seaborn as sns
   from datetime import datetime
   import base64
   from io import BytesIO
   
   # Load data
   with open('$OUTPUT_DIR/course_info.json') as f:
       course_info = json.load(f)
   
   enrollment_df = pd.read_csv('$OUTPUT_DIR/enrollment_stats.csv')
   progress_df = pd.read_csv('$OUTPUT_DIR/student_progress.csv')
   
   with open('$OUTPUT_DIR/exercise_completion.json') as f:
       exercise_data = json.load(f)
   
   # Create visualizations
   plt.style.use('seaborn-v0_8')
   
   # Progress distribution chart
   fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
   
   # Histogram of progress percentages
   ax1.hist(progress_df['progress_percentage'], bins=20, alpha=0.7, color='skyblue')
   ax1.set_title('Distribution of Student Progress')
   ax1.set_xlabel('Progress Percentage')
   ax1.set_ylabel('Number of Students')
   
   # Exercise completion rates
   exercises = [ex['title'] for ex in exercise_data['exercises']]
   completion_rates = [ex['completion_rate'] for ex in exercise_data['exercises']]
   
   ax2.barh(exercises[:10], completion_rates[:10])  # Top 10 exercises
   ax2.set_title('Exercise Completion Rates')
   ax2.set_xlabel('Completion Rate (%)')
   
   plt.tight_layout()
   
   # Save chart as base64 for embedding in HTML
   buffer = BytesIO()
   plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
   buffer.seek(0)
   chart_data = base64.b64encode(buffer.getvalue()).decode()
   plt.close()
   
   # Generate HTML report
   html_report = f"""
   <!DOCTYPE html>
   <html>
   <head>
       <title>{course_info['title']} - Progress Report</title>
       <style>
           body {{ font-family: Arial, sans-serif; margin: 40px; }}
           .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
           .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #e9e9e9; border-radius: 5px; }}
           .chart {{ text-align: center; margin: 20px 0; }}
           table {{ border-collapse: collapse; width: 100%; }}
           th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
           th {{ background-color: #f2f2f2; }}
       </style>
   </head>
   <body>
       <div class="header">
           <h1>{course_info['title']} - Progress Report</h1>
           <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
           <p>Report Type: {REPORT_TYPE.title()}</p>
       </div>
       
       <h2>Key Metrics</h2>
       <div class="metric">
           <strong>Total Enrolled:</strong> {len(progress_df)}
       </div>
       <div class="metric">
           <strong>Average Progress:</strong> {progress_df['progress_percentage'].mean():.1f}%
       </div>
       <div class="metric">
           <strong>Completion Rate:</strong> {(progress_df['progress_percentage'] == 100).sum()}/{len(progress_df)}
       </div>
       <div class="metric">
           <strong>Active Students:</strong> {(progress_df['last_activity'] > datetime.now().strftime('%Y-%m-%d')).sum() if 'last_activity' in progress_df.columns else 'N/A'}
       </div>
       
       <h2>Progress Visualization</h2>
       <div class="chart">
           <img src="data:image/png;base64,{chart_data}" alt="Progress Charts">
       </div>
       
       <h2>Student Progress Details</h2>
       <table>
           <tr>
               <th>Student</th>
               <th>Progress</th>
               <th>Lessons Completed</th>
               <th>Exercises Completed</th>
               <th>Last Activity</th>
           </tr>
   """
   
   # Add student rows
   for _, student in progress_df.iterrows():
       html_report += f"""
           <tr>
               <td>{student.get('student_name', 'N/A')}</td>
               <td>{student['progress_percentage']:.1f}%</td>
               <td>{student.get('lessons_completed', 0)}</td>
               <td>{student.get('exercises_completed', 0)}</td>
               <td>{student.get('last_activity', 'N/A')}</td>
           </tr>
       """
   
   html_report += """
       </table>
   </body>
   </html>
   """
   
   # Save HTML report
   with open('$OUTPUT_DIR/progress_report.html', 'w') as f:
       f.write(html_report)
   
   print(f"HTML report generated: $OUTPUT_DIR/progress_report.html")
   EOF
   
   echo "Report generation completed!"
   echo "Files generated:"
   echo "  - $OUTPUT_DIR/progress_report.html (Main report)"
   echo "  - $OUTPUT_DIR/student_progress.csv (Raw data)"
   echo "  - $OUTPUT_DIR/enrollment_stats.csv (Enrollment data)"
   echo "  - $OUTPUT_DIR/exercise_completion.json (Exercise data)"

Automated Maintenance Tasks
--------------------------

Log Rotation and Cleanup
~~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Manage log files and clean up old data to maintain system performance.

.. code-block:: bash

   #!/bin/bash
   # File: scripts/maintenance-cleanup.sh
   
   set -e
   
   # Configuration
   LOG_RETENTION_DAYS=30
   BACKUP_RETENTION_DAYS=90
   TEMP_RETENTION_HOURS=24
   
   echo "Starting system maintenance cleanup..."
   echo "======================================"
   
   # Rotate and compress log files
   echo "Rotating log files..."
   if [ -f /var/log/pmh/app.log ]; then
       # Rotate main application log
       mv /var/log/pmh/app.log /var/log/pmh/app.log.$(date +%Y%m%d_%H%M%S)
       touch /var/log/pmh/app.log
       chown pmhuser:pmhuser /var/log/pmh/app.log
       
       # Compress old logs
       find /var/log/pmh -name "app.log.*" -type f ! -name "*.gz" -exec gzip {} \;
   fi
   
   # Clean up old log files
   echo "Cleaning up old log files..."
   find /var/log/pmh -name "*.log.*.gz" -mtime +$LOG_RETENTION_DAYS -delete
   find /var/log/pmh -name "*.log" -mtime +$LOG_RETENTION_DAYS -delete
   
   # Clean up old backup files
   echo "Cleaning up old backup files..."
   find /backup -name "*.sql.gz" -mtime +$BACKUP_RETENTION_DAYS -delete
   find /backup -name "*.tar.gz" -mtime +$BACKUP_RETENTION_DAYS -delete
   
   # Clean up temporary files
   echo "Cleaning up temporary files..."
   find /tmp -name "pmh_*" -type f -mtime +1 -delete
   find /tmp -name "*.tmp" -type f -mmin +$((TEMP_RETENTION_HOURS * 60)) -delete
   
   # Clean up old session data
   echo "Cleaning up old session data..."
   pmh sessions cleanup --older-than "7 days"
   
   # Clean up old activity logs
   echo "Cleaning up old activity logs..."
   pmh db cleanup --table user_activity_log --older-than "90 days"
   
   # Update database statistics
   echo "Updating database statistics..."
   pmh db analyze --update-stats
   
   # Clean up unused uploaded files
   echo "Cleaning up orphaned uploaded files..."
   pmh files cleanup --orphaned --dry-run > /tmp/orphaned_files.txt
   
   if [ -s /tmp/orphaned_files.txt ]; then
       echo "Found orphaned files:"
       cat /tmp/orphaned_files.txt
       
       # Uncomment the next line to actually delete orphaned files
       # pmh files cleanup --orphaned --force
   else
       echo "No orphaned files found"
   fi
   
   # Generate maintenance report
   cat > "/var/log/pmh/maintenance_$(date +%Y%m%d_%H%M%S).log" << EOF
   Maintenance Cleanup Report
   Generated: $(date)
   
   Actions Performed:
   - Rotated and compressed log files
   - Cleaned up logs older than $LOG_RETENTION_DAYS days
   - Cleaned up backups older than $BACKUP_RETENTION_DAYS days
   - Cleaned up temporary files older than $TEMP_RETENTION_HOURS hours
   - Cleaned up old session data (7+ days)
   - Cleaned up old activity logs (90+ days)
   - Updated database statistics
   - Scanned for orphaned files
   
   Disk Space After Cleanup:
   $(df -h)
   
   Database Statistics:
   $(pmh db status)
   EOF
   
   echo "Maintenance cleanup completed successfully!"

SSL Certificate Renewal
~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Automate SSL certificate renewal and update web server configuration.

.. code-block:: bash

   #!/bin/bash
   # File: scripts/ssl-renewal.sh
   
   DOMAIN="your-domain.com"
   EMAIL="admin@your-domain.com"
   WEBROOT="/var/www/html"
   NOTIFICATION_EMAIL="admin@your-domain.com"
   
   echo "Starting SSL certificate renewal process..."
   echo "==========================================="
   
   # Check current certificate expiration
   echo "Checking current certificate expiration..."
   CURRENT_EXPIRY=$(openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -noout -enddate 2>/dev/null | cut -d= -f2)
   
   if [ -n "$CURRENT_EXPIRY" ]; then
       echo "Current certificate expires: $CURRENT_EXPIRY"
       
       # Check if renewal is needed (less than 30 days)
       EXPIRY_EPOCH=$(date -d "$CURRENT_EXPIRY" +%s)
       CURRENT_EPOCH=$(date +%s)
       DAYS_UNTIL_EXPIRY=$(( ($EXPIRY_EPOCH - $CURRENT_EPOCH) / 86400 ))
       
       echo "Days until expiry: $DAYS_UNTIL_EXPIRY"
       
       if [ $DAYS_UNTIL_EXPIRY -gt 30 ]; then
           echo "Certificate renewal not needed yet"
           exit 0
       fi
   fi
   
   # Stop web server temporarily for renewal
   echo "Stopping web server for renewal..."
   systemctl stop nginx
   
   # Renew certificate
   echo "Renewing SSL certificate..."
   if certbot certonly \
       --standalone \
       --non-interactive \
       --agree-tos \
       --email "$EMAIL" \
       --domains "$DOMAIN,www.$DOMAIN" \
       --force-renewal; then
       
       echo "✅ Certificate renewed successfully"
       
       # Start web server
       systemctl start nginx
       
       # Test SSL configuration
       echo "Testing SSL configuration..."
       if openssl s_client -connect $DOMAIN:443 -servername $DOMAIN </dev/null 2>/dev/null | openssl x509 -noout -dates; then
           echo "✅ SSL configuration test passed"
           
           # Send success notification
           if command -v mail &> /dev/null; then
               echo "SSL certificate for $DOMAIN has been renewed successfully." | \
                   mail -s "SSL Certificate Renewed - $DOMAIN" "$NOTIFICATION_EMAIL"
           fi
       else
           echo "❌ SSL configuration test failed"
           
           # Send failure notification
           if command -v mail &> /dev/null; then
               echo "SSL certificate renewal succeeded but configuration test failed for $DOMAIN." | \
                   mail -s "SSL Configuration Issue - $DOMAIN" "$NOTIFICATION_EMAIL"
           fi
       fi
   else
       echo "❌ Certificate renewal failed"
       
       # Start web server anyway
       systemctl start nginx
       
       # Send failure notification
       if command -v mail &> /dev/null; then
           echo "SSL certificate renewal failed for $DOMAIN. Manual intervention required." | \
               mail -s "SSL Renewal FAILED - $DOMAIN" "$NOTIFICATION_EMAIL"
       fi
       
       exit 1
   fi

Development and Testing Utilities
--------------------------------

Environment Setup
~~~~~~~~~~~~~~~~

**Use Case**: Set up development and testing environments quickly.

.. code-block:: bash

   #!/bin/bash
   # File: scripts/setup-dev-environment.sh
   
   ENVIRONMENT="${1:-development}"  # development, testing, staging
   
   echo "Setting up $ENVIRONMENT environment..."
   echo "======================================"
   
   # Create environment-specific configuration
   case $ENVIRONMENT in
       "development")
           CONFIG_FILE="dev-config.yaml"
           DB_NAME="pmh_development"
           DEBUG_MODE="true"
           LOG_LEVEL="DEBUG"
           ;;
       "testing")
           CONFIG_FILE="test-config.yaml"
           DB_NAME="pmh_testing"
           DEBUG_MODE="true"
           LOG_LEVEL="INFO"
           ;;
       "staging")
           CONFIG_FILE="staging-config.yaml"
           DB_NAME="pmh_staging"
           DEBUG_MODE="false"
           LOG_LEVEL="INFO"
           ;;
       *)
           echo "Unknown environment: $ENVIRONMENT"
           echo "Valid options: development, testing, staging"
           exit 1
           ;;
   esac
   
   # Generate configuration file
   echo "Generating configuration file: $CONFIG_FILE"
   pmh config generate --env "$ENVIRONMENT" --output "$CONFIG_FILE"
   
   # Update database name
   pmh config set --config "$CONFIG_FILE" database.name "$DB_NAME"
   pmh config set --config "$CONFIG_FILE" debug "$DEBUG_MODE"
   pmh config set --config "$CONFIG_FILE" logging.level "$LOG_LEVEL"
   
   # Create database
   echo "Creating database: $DB_NAME"
   sudo -u postgres createdb "$DB_NAME" || echo "Database may already exist"
   
   # Initialize database schema
   echo "Initializing database schema..."
   PMH_CONFIG_FILE="$CONFIG_FILE" pmh db init
   
   # Load sample data for development
   if [ "$ENVIRONMENT" = "development" ]; then
       echo "Loading sample data..."
       PMH_CONFIG_FILE="$CONFIG_FILE" pmh db seed --sample-data
   fi
   
   # Load test data for testing
   if [ "$ENVIRONMENT" = "testing" ]; then
       echo "Loading test data..."
       PMH_CONFIG_FILE="$CONFIG_FILE" pmh db seed --test-data
   fi
   
   echo "Environment setup completed!"
   echo "To use this environment:"
   echo "  export PMH_CONFIG_FILE=$CONFIG_FILE"
   echo "  pmh web start"

Integration Testing
~~~~~~~~~~~~~~~~~~

**Use Case**: Run comprehensive integration tests across the entire system.

.. code-block:: bash

   #!/bin/bash
   # File: scripts/integration-tests.sh
   
   set -e
   
   TEST_ENV="testing"
   TEST_CONFIG="test-config.yaml"
   TEST_PORT="8080"
   
   echo "Starting integration test suite..."
   echo "=================================="
   
   # Setup test environment
   echo "Setting up test environment..."
   ./setup-dev-environment.sh "$TEST_ENV"
   
   # Start test server
   echo "Starting test server on port $TEST_PORT..."
   PMH_CONFIG_FILE="$TEST_CONFIG" pmh web start --port "$TEST_PORT" --workers 1 --daemon
   
   # Wait for server to start
   echo "Waiting for server to start..."
   for i in {1..30}; do
       if curl -f "http://localhost:$TEST_PORT/health" >/dev/null 2>&1; then
           echo "Server is ready!"
           break
       fi
       sleep 1
       if [ $i -eq 30 ]; then
           echo "Server failed to start"
           exit 1
       fi
   done
   
   # Run integration tests
   echo "Running integration tests..."
   
   # Test user management
   echo "Testing user management..."
   USER_ID=$(pmh users create --username testuser --email test@example.com --output json | jq -r '.id')
   pmh users list --username testuser >/dev/null
   
   # Test course management
   echo "Testing course management..."
   COURSE_ID=$(pmh courses create --title "Test Course" --difficulty beginner --output json | jq -r '.id')
   pmh courses list --course-id "$COURSE_ID" >/dev/null
   
   # Test enrollment
   echo "Testing enrollment..."
   pmh courses enroll --user-id "$USER_ID" --course-id "$COURSE_ID"
   
   # Test API endpoints
   echo "Testing API endpoints..."
   API_TESTS=(
       "GET /health"
       "GET /api/v1/courses"
       "GET /api/v1/users/me"
   )
   
   for test in "${API_TESTS[@]}"; do
       method=$(echo "$test" | awk '{print $1}')
       endpoint=$(echo "$test" | awk '{print $2}')
       
       echo "  Testing $method $endpoint..."
       if [ "$method" = "GET" ]; then
           curl -f "http://localhost:$TEST_PORT$endpoint" >/dev/null
       fi
   done
   
   # Performance test
   echo "Running performance test..."
   ab -n 100 -c 10 "http://localhost:$TEST_PORT/health" > /tmp/performance_test.log
   
   # Check performance results
   AVG_TIME=$(grep "Time per request" /tmp/performance_test.log | head -1 | awk '{print $4}')
   echo "Average response time: ${AVG_TIME}ms"
   
   # Cleanup
   echo "Cleaning up..."
   pkill -f "pmh web start.*$TEST_PORT" || true
   
   echo "Integration tests completed successfully!"

Troubleshooting and Debugging
----------------------------

System Diagnostics
~~~~~~~~~~~~~~~~~

**Use Case**: Comprehensive system diagnostics when issues occur.

.. code-block:: bash

   #!/bin/bash
   # File: scripts/system-diagnostics.sh
   
   REPORT_FILE="diagnostics-$(date +%Y%m%d_%H%M%S).txt"
   
   echo "Python Mastery Hub System Diagnostics" | tee "$REPORT_FILE"
   echo "Generated: $(date)" | tee -a "$REPORT_FILE"
   echo "=======================================" | tee -a "$REPORT_FILE"
   echo "" | tee -a "$REPORT_FILE"
   
   # System information
   echo "=== SYSTEM INFORMATION ===" | tee -a "$REPORT_FILE"
   echo "OS: $(lsb_release -d | cut -f2)" | tee -a "$REPORT_FILE"
   echo "Kernel: $(uname -r)" | tee -a "$REPORT_FILE"
   echo "Architecture: $(uname -m)" | tee -a "$REPORT_FILE"
   echo "Uptime: $(uptime)" | tee -a "$REPORT_FILE"
   echo "" | tee -a "$REPORT_FILE"
   
   # Resource usage
   echo "=== RESOURCE USAGE ===" | tee -a "$REPORT_FILE"
   echo "CPU Usage:" | tee -a "$REPORT_FILE"
   top -bn1 | grep "Cpu(s)" | tee -a "$REPORT_FILE"
   echo "" | tee -a "$REPORT_FILE"
   echo "Memory Usage:" | tee -a "$REPORT_FILE"
   free -h | tee -a "$REPORT_FILE"
   echo "" | tee -a "$REPORT_FILE"
   echo "Disk Usage:" | tee -a "$REPORT_FILE"
   df -h | tee -a "$REPORT_FILE"
   echo "" | tee -a "$REPORT_FILE"
   
   # Service status
   echo "=== SERVICE STATUS ===" | tee -a "$REPORT_FILE"
   for service in pmh nginx postgresql redis-server; do
       echo "Service: $service" | tee -a "$REPORT_FILE"
       systemctl status "$service" --no-pager | tee -a "$REPORT_FILE"
       echo "" | tee -a "$REPORT_FILE"
   done
   
   # Python Mastery Hub status
   echo "=== PMH STATUS ===" | tee -a "$REPORT_FILE"
   if command -v pmh &> /dev/null; then
       echo "PMH Version: $(pmh --version)" | tee -a "$REPORT_FILE"
       echo "Web Server Status:" | tee -a "$REPORT_FILE"
       pmh web status 2>&1 | tee -a "$REPORT_FILE"
       echo "Database Status:" | tee -a "$REPORT_FILE"
       pmh db status 2>&1 | tee -a "$REPORT_FILE"
   else
       echo "PMH command not found" | tee -a "$REPORT_FILE"
   fi
   echo "" | tee -a "$REPORT_FILE"
   
   # Network connectivity
   echo "=== NETWORK CONNECTIVITY ===" | tee -a "$REPORT_FILE"
   echo "Listening ports:" | tee -a "$REPORT_FILE"
   netstat -tlnp | grep -E ':(80|443|8000|5432|6379)' | tee -a "$REPORT_FILE"
   echo "" | tee -a "$REPORT_FILE"
   
   # Recent log entries
   echo "=== RECENT LOG ENTRIES ===" | tee -a "$REPORT_FILE"
   if [ -f /var/log/pmh/app.log ]; then
       echo "Last 20 lines of application log:" | tee -a "$REPORT_FILE"
       tail -20 /var/log/pmh/app.log | tee -a "$REPORT_FILE"
   fi
   echo "" | tee -a "$REPORT_FILE"
   
   # Recent errors
   echo "=== RECENT ERRORS ===" | tee -a "$REPORT_FILE"
   journalctl --since "1 hour ago" --priority=err --no-pager | tail -20 | tee -a "$REPORT_FILE"
   echo "" | tee -a "$REPORT_FILE"
   
   echo "Diagnostics completed. Report saved to: $REPORT_FILE"

Best Practices and Tips
----------------------

CLI Automation Best Practices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Error Handling**: Always use ``set -e`` and check command return codes
2. **Logging**: Log all operations with timestamps for audit trails
3. **Backups**: Create backups before destructive operations
4. **Testing**: Test scripts in development environments first
5. **Configuration**: Use environment variables for configuration
6. **Documentation**: Document script purpose, usage, and requirements

**Example Template**:

.. code-block:: bash

   #!/bin/bash
   # Script: script-name.sh
   # Purpose: Brief description of what this script does
   # Usage: ./script-name.sh <required_param> [optional_param]
   # Requirements: List any prerequisites
   
   set -e  # Exit on any error
   
   # Configuration
   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
   LOG_FILE="/var/log/pmh/$(basename "$0" .sh)-$(date +%Y%m%d_%H%M%S).log"
   
   # Logging function
   log() {
       echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
   }
   
   # Error handling
   error_exit() {
       log "ERROR: $1"
       exit 1
   }
   
   # Parameter validation
   if [ $# -lt 1 ]; then
       echo "Usage: $0 <required_param> [optional_param]"
       exit 1
   fi
   
   # Main script logic here
   log "Starting script execution..."
   
   # Your code here
   
   log "Script completed successfully"

Security Considerations
~~~~~~~~~~~~~~~~~~~~~~

1. **Credentials**: Never hard-code passwords or API keys
2. **Permissions**: Run scripts with minimal required privileges
3. **Input Validation**: Validate all user inputs
4. **Audit Logging**: Log all administrative operations
5. **Secure Storage**: Use proper file permissions for sensitive data

Common Troubleshooting
~~~~~~~~~~~~~~~~~~~~~

**Script fails with permission errors:**

.. code-block:: bash

   # Fix file permissions
   chmod +x script.sh
   
   # Run with appropriate user
   sudo -u pmhuser ./script.sh

**Database connection issues:**

.. code-block:: bash

   # Check database status
   pmh db status
   
   # Test connection
   psql -h localhost -U pmhuser -d pmh_production -c "SELECT 1;"

**Web server not responding:**

.. code-block:: bash

   # Check service status
   systemctl status pmh
   
   # Check logs
   journalctl -u pmh -f
   
   # Restart if needed
   systemctl restart pmh

Getting Help
-----------

- **Documentation**: :doc:`../api/cli` for complete CLI reference
- **Community**: Discord #cli-help channel for script assistance
- **Examples**: GitHub repository with more automation examples
- **Support**: Enterprise customers get priority CLI automation support

.. admonition:: Automate Wisely! 🤖
   :class: tip

   Start with simple scripts and gradually build more complex automation. 
   Always test in development environments before deploying to production. 
   Remember: good automation saves time, but bad automation can cause downtime!