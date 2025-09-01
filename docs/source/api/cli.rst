.. File: docs/source/api/cli.rst

CLI API Reference
=================

The Command Line Interface (CLI) provides powerful tools for managing Python Mastery Hub 
installations, creating content, and automating administrative tasks.

.. note::
   **Installation**: The CLI is installed automatically with the main package.
   
   **Command**: All CLI commands start with ``pmh`` (Python Mastery Hub).

Overview
--------

The CLI is organized into several command groups:

- **Server Management**: Start, stop, and configure the application server
- **User Management**: Create and manage user accounts
- **Content Management**: Create and manage courses, lessons, and exercises
- **Database Operations**: Manage database schema and data
- **Development Tools**: Development and testing utilities
- **Deployment**: Production deployment helpers

Getting Started
---------------

Check CLI version and help:

.. code-block:: bash

   # Check version
   pmh --version
   
   # Get general help
   pmh --help
   
   # Get help for specific command
   pmh web --help

Global Options
--------------

All commands support these global options:

.. option:: --config PATH

   Path to configuration file (default: ``~/.pmh/config.yaml``)

.. option:: --verbose, -v

   Enable verbose output

.. option:: --quiet, -q

   Suppress non-error output

.. option:: --no-color

   Disable colored output

.. option:: --help

   Show help message and exit

Server Management
-----------------

pmh web
~~~~~~~

Manage the web application server.

.. code-block:: bash

   pmh web [COMMAND] [OPTIONS]

**Commands:**

``start``
  Start the web server

  .. code-block:: bash
  
     # Start with default settings
     pmh web start
     
     # Start on specific host and port
     pmh web start --host 0.0.0.0 --port 8080
     
     # Start in development mode with auto-reload
     pmh web start --dev
     
     # Start with SSL
     pmh web start --ssl-cert /path/to/cert.pem --ssl-key /path/to/key.pem

  **Options:**
  
  .. option:: --host TEXT
  
     Host to bind to (default: localhost)
  
  .. option:: --port INTEGER
  
     Port to bind to (default: 8000)
  
  .. option:: --workers INTEGER
  
     Number of worker processes (default: 1)
  
  .. option:: --dev
  
     Enable development mode with auto-reload
  
  .. option:: --ssl-cert PATH
  
     Path to SSL certificate file
  
  .. option:: --ssl-key PATH
  
     Path to SSL private key file

``stop``
  Stop the web server

  .. code-block:: bash
  
     pmh web stop

``restart``
  Restart the web server

  .. code-block:: bash
  
     pmh web restart

``status``
  Show server status

  .. code-block:: bash
  
     pmh web status

``config``
  Show or update server configuration

  .. code-block:: bash
  
     # Show current configuration
     pmh web config show
     
     # Update configuration
     pmh web config set database.url "postgresql://user:pass@localhost/pmh"

User Management
---------------

pmh users
~~~~~~~~~

Manage user accounts and permissions.

.. code-block:: bash

   pmh users [COMMAND] [OPTIONS]

**Commands:**

``create``
  Create a new user account

  .. code-block:: bash
  
     # Create user interactively
     pmh users create
     
     # Create user with parameters
     pmh users create --username john_doe --email john@example.com --password secure123
     
     # Create admin user
     pmh users create --username admin --email admin@example.com --role admin

  **Options:**
  
  .. option:: --username TEXT
  
     Username for the new user
  
  .. option:: --email TEXT
  
     Email address for the new user
  
  .. option:: --password TEXT
  
     Password for the new user (will prompt if not provided)
  
  .. option:: --first-name TEXT
  
     First name of the user
  
  .. option:: --last-name TEXT
  
     Last name of the user
  
  .. option:: --role TEXT
  
     User role (student, instructor, admin)

``list``
  List user accounts

  .. code-block:: bash
  
     # List all users
     pmh users list
     
     # List users with filters
     pmh users list --role admin --active-only
     
     # Export to CSV
     pmh users list --output csv --file users.csv

  **Options:**
  
  .. option:: --role TEXT
  
     Filter by user role
  
  .. option:: --active-only
  
     Show only active users
  
  .. option:: --output TEXT
  
     Output format (table, csv, json)
  
  .. option:: --file PATH
  
     Output file path

``update``
  Update user account

  .. code-block:: bash
  
     # Update user email
     pmh users update john_doe --email new_email@example.com
     
     # Change user role
     pmh users update john_doe --role instructor
     
     # Deactivate user
     pmh users update john_doe --active false

``delete``
  Delete user account

  .. code-block:: bash
  
     # Delete user (with confirmation)
     pmh users delete john_doe
     
     # Force delete without confirmation
     pmh users delete john_doe --force

``reset-password``
  Reset user password

  .. code-block:: bash
  
     # Reset password (will prompt for new password)
     pmh users reset-password john_doe
     
     # Reset with new password
     pmh users reset-password john_doe --password new_secure123

Content Management
------------------

pmh courses
~~~~~~~~~~~

Manage courses and learning content.

.. code-block:: bash

   pmh courses [COMMAND] [OPTIONS]

**Commands:**

``create``
  Create a new course

  .. code-block:: bash
  
     # Create course interactively
     pmh courses create
     
     # Create course with parameters
     pmh courses create --title "Python Basics" --description "Learn Python fundamentals" --difficulty beginner
     
     # Create from template
     pmh courses create --from-template python-fundamentals

  **Options:**
  
  .. option:: --title TEXT
  
     Course title
  
  .. option:: --description TEXT
  
     Course description
  
  .. option:: --difficulty TEXT
  
     Course difficulty (beginner, intermediate, advanced)
  
  .. option:: --from-template TEXT
  
     Create from existing template

``list``
  List existing courses

  .. code-block:: bash
  
     # List all courses
     pmh courses list
     
     # List with details
     pmh courses list --detailed
     
     # Filter by difficulty
     pmh courses list --difficulty beginner

``import``
  Import course from file

  .. code-block:: bash
  
     # Import from YAML file
     pmh courses import course.yaml
     
     # Import from directory structure
     pmh courses import ./course-directory/ --format directory

``export``
  Export course to file

  .. code-block:: bash
  
     # Export to YAML
     pmh courses export python-basics --format yaml --output course.yaml
     
     # Export entire course structure
     pmh courses export python-basics --format directory --output ./exported-course/

``publish``
  Publish course to make it available to students

  .. code-block:: bash
  
     pmh courses publish python-basics

``unpublish``
  Unpublish course

  .. code-block:: bash
  
     pmh courses unpublish python-basics

pmh lessons
~~~~~~~~~~~

Manage individual lessons within courses.

.. code-block:: bash

   pmh lessons [COMMAND] [OPTIONS]

**Commands:**

``create``
  Create a new lesson

  .. code-block:: bash
  
     # Create lesson interactively
     pmh lessons create --course python-basics --module fundamentals
     
     # Create from markdown file
     pmh lessons create --course python-basics --module fundamentals --from-file lesson.md

``edit``
  Edit lesson content

  .. code-block:: bash
  
     # Edit in default editor
     pmh lessons edit lesson-123
     
     # Edit specific section
     pmh lessons edit lesson-123 --section content

pmh exercises
~~~~~~~~~~~~~

Manage coding exercises and assessments.

.. code-block:: bash

   pmh exercises [COMMAND] [OPTIONS]

**Commands:**

``create``
  Create a new exercise

  .. code-block:: bash
  
     # Create exercise interactively
     pmh exercises create --lesson lesson-123
     
     # Create from template
     pmh exercises create --lesson lesson-123 --template basic-function

``test``
  Test exercise solution

  .. code-block:: bash
  
     # Test with solution file
     pmh exercises test exercise-456 --solution solution.py
     
     # Test with inline code
     pmh exercises test exercise-456 --code "def hello(): return 'Hello World'"

``validate``
  Validate exercise configuration

  .. code-block:: bash
  
     pmh exercises validate exercise-456

Database Operations
-------------------

pmh db
~~~~~~

Manage database schema and data.

.. code-block:: bash

   pmh db [COMMAND] [OPTIONS]

**Commands:**

``init``
  Initialize database schema

  .. code-block:: bash
  
     # Initialize with default settings
     pmh db init
     
     # Initialize with custom database URL
     pmh db init --database-url postgresql://user:pass@localhost/pmh

``migrate``
  Run database migrations

  .. code-block:: bash
  
     # Run all pending migrations
     pmh db migrate
     
     # Migrate to specific revision
     pmh db migrate --revision 003
     
     # Show migration status
     pmh db migrate --status

``reset``
  Reset database (WARNING: destroys all data)

  .. code-block:: bash
  
     # Reset with confirmation
     pmh db reset
     
     # Force reset without confirmation
     pmh db reset --force

``backup``
  Create database backup

  .. code-block:: bash
  
     # Create backup with timestamp
     pmh db backup
     
     # Create backup to specific file
     pmh db backup --output backup_2024_01_20.sql
     
     # Compress backup
     pmh db backup --compress

``restore``
  Restore database from backup

  .. code-block:: bash
  
     # Restore from backup file
     pmh db restore backup_2024_01_20.sql
     
     # Restore compressed backup
     pmh db restore backup_2024_01_20.sql.gz

``seed``
  Seed database with sample data

  .. code-block:: bash
  
     # Seed with default sample data
     pmh db seed
     
     # Seed with custom data file
     pmh db seed --data-file custom_data.yaml

Development Tools
-----------------

pmh dev
~~~~~~~

Development and testing utilities.

.. code-block:: bash

   pmh dev [COMMAND] [OPTIONS]

**Commands:**

``setup``
  Setup development environment

  .. code-block:: bash
  
     # Setup with default settings
     pmh dev setup
     
     # Setup with custom configuration
     pmh dev setup --config dev-config.yaml

``test``
  Run tests

  .. code-block:: bash
  
     # Run all tests
     pmh dev test
     
     # Run specific test module
     pmh dev test --module auth
     
     # Run with coverage
     pmh dev test --coverage

``lint``
  Run code linting

  .. code-block:: bash
  
     # Lint all code
     pmh dev lint
     
     # Lint specific directory
     pmh dev lint --path src/
     
     # Auto-fix issues
     pmh dev lint --fix

``format``
  Format code

  .. code-block:: bash
  
     # Format all Python files
     pmh dev format
     
     # Format specific files
     pmh dev format --files file1.py file2.py
     
     # Check formatting without changes
     pmh dev format --check

``docs``
  Generate documentation

  .. code-block:: bash
  
     # Generate all documentation
     pmh dev docs
     
     # Generate and serve locally
     pmh dev docs --serve
     
     # Generate specific format
     pmh dev docs --format html

Deployment
----------

pmh deploy
~~~~~~~~~~

Production deployment utilities.

.. code-block:: bash

   pmh deploy [COMMAND] [OPTIONS]

**Commands:**

``docker``
  Docker deployment utilities

  .. code-block:: bash
  
     # Build Docker image
     pmh deploy docker build --tag pmh:latest
     
     # Run Docker container
     pmh deploy docker run --port 8000
     
     # Generate docker-compose.yml
     pmh deploy docker compose --output docker-compose.yml

``kubernetes``
  Kubernetes deployment utilities

  .. code-block:: bash
  
     # Generate Kubernetes manifests
     pmh deploy kubernetes generate --output k8s/
     
     # Deploy to Kubernetes cluster
     pmh deploy kubernetes deploy --namespace pmh-prod
     
     # Check deployment status
     pmh deploy kubernetes status

``systemd``
  Systemd service management

  .. code-block:: bash
  
     # Generate systemd service file
     pmh deploy systemd generate --output /etc/systemd/system/pmh.service
     
     # Install systemd service
     pmh deploy systemd install
     
     # Start service
     pmh deploy systemd start

Configuration Management
-----------------------

pmh config
~~~~~~~~~~

Manage application configuration.

.. code-block:: bash

   pmh config [COMMAND] [OPTIONS]

**Commands:**

``show``
  Display current configuration

  .. code-block:: bash
  
     # Show all configuration
     pmh config show
     
     # Show specific section
     pmh config show --section database
     
     # Show in different format
     pmh config show --format yaml

``set``
  Set configuration value

  .. code-block:: bash
  
     # Set single value
     pmh config set database.url postgresql://localhost/pmh
     
     # Set multiple values from file
     pmh config set --from-file config.yaml

``get``
  Get configuration value

  .. code-block:: bash
  
     # Get specific value
     pmh config get database.url
     
     # Get with default
     pmh config get cache.timeout --default 300

``validate``
  Validate configuration

  .. code-block:: bash
  
     # Validate current configuration
     pmh config validate
     
     # Validate specific file
     pmh config validate --file config.yaml

``generate``
  Generate configuration template

  .. code-block:: bash
  
     # Generate default configuration
     pmh config generate --output config.yaml
     
     # Generate for specific environment
     pmh config generate --env production --output prod-config.yaml

Logging and Monitoring
----------------------

pmh logs
~~~~~~~~

View and manage application logs.

.. code-block:: bash

   pmh logs [COMMAND] [OPTIONS]

**Commands:**

``show``
  Display logs

  .. code-block:: bash
  
     # Show recent logs
     pmh logs show
     
     # Follow logs in real-time
     pmh logs show --follow
     
     # Filter by level
     pmh logs show --level error
     
     # Show logs from specific time
     pmh logs show --since "2024-01-20 10:00:00"

``search``
  Search through logs

  .. code-block:: bash
  
     # Search for specific term
     pmh logs search "authentication error"
     
     # Search with regex
     pmh logs search --regex "user_id: \d+"

``analyze``
  Analyze log patterns

  .. code-block:: bash
  
     # Generate log analysis report
     pmh logs analyze --period 24h
     
     # Export analysis to file
     pmh logs analyze --output analysis.json

Plugin Management
-----------------

pmh plugins
~~~~~~~~~~~

Manage Python Mastery Hub plugins.

.. code-block:: bash

   pmh plugins [COMMAND] [OPTIONS]

**Commands:**

``list``
  List installed plugins

  .. code-block:: bash
  
     # List all plugins
     pmh plugins list
     
     # Show detailed information
     pmh plugins list --detailed

``install``
  Install a plugin

  .. code-block:: bash
  
     # Install from PyPI
     pmh plugins install pmh-analytics
     
     # Install from local file
     pmh plugins install ./my-plugin/
     
     # Install from git repository
     pmh plugins install git+https://github.com/user/pmh-plugin.git

``uninstall``
  Uninstall a plugin

  .. code-block:: bash
  
     pmh plugins uninstall pmh-analytics

``enable``
  Enable a plugin

  .. code-block:: bash
  
     pmh plugins enable pmh-analytics

``disable``
  Disable a plugin

  .. code-block:: bash
  
     pmh plugins disable pmh-analytics

Automation and Scripting
-------------------------

Configuration Files
~~~~~~~~~~~~~~~~~~~

The CLI supports configuration files to avoid repeating common options:

**~/.pmh/config.yaml:**

.. code-block:: yaml

   database:
     url: postgresql://localhost/pmh
     echo: false
   
   web:
     host: localhost
     port: 8000
     workers: 4
   
   logging:
     level: INFO
     file: /var/log/pmh/app.log
   
   plugins:
     - pmh-analytics
     - pmh-reporting

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

All configuration options can be set via environment variables:

.. code-block:: bash

   export PMH_DATABASE_URL=postgresql://localhost/pmh
   export PMH_WEB_HOST=0.0.0.0
   export PMH_WEB_PORT=8080
   export PMH_LOG_LEVEL=DEBUG

Scripting Examples
~~~~~~~~~~~~~~~~~~

**Automated Deployment Script:**

.. code-block:: bash

   #!/bin/bash
   
   # Deploy Python Mastery Hub
   set -e
   
   echo "Backing up database..."
   pmh db backup --output "backup_$(date +%Y%m%d_%H%M%S).sql"
   
   echo "Running migrations..."
   pmh db migrate
   
   echo "Restarting web server..."
   pmh web restart
   
   echo "Deployment complete!"

**Content Import Script:**

.. code-block:: bash

   #!/bin/bash
   
   # Import course content from directory
   for course_dir in ./courses/*/; do
       course_name=$(basename "$course_dir")
       echo "Importing course: $course_name"
       pmh courses import "$course_dir" --format directory
   done

**User Management Script:**

.. code-block:: python

   #!/usr/bin/env python3
   
   import subprocess
   import csv
   
   # Bulk user creation from CSV
   with open('users.csv', 'r') as f:
       reader = csv.DictReader(f)
       for row in reader:
           cmd = [
               'pmh', 'users', 'create',
               '--username', row['username'],
               '--email', row['email'],
               '--first-name', row['first_name'],
               '--last-name', row['last_name'],
               '--role', row['role']
           ]
           subprocess.run(cmd, check=True)

Exit Codes
----------

The CLI uses standard exit codes:

- ``0``: Success
- ``1``: General error
- ``2``: Invalid command or arguments
- ``3``: Configuration error
- ``4``: Database error
- ``5``: Network error
- ``6``: Permission error
- ``7``: File not found
- ``8``: Validation error

Shell Completion
----------------

Enable shell completion for better CLI experience:

**Bash:**

.. code-block:: bash

   # Add to ~/.bashrc
   eval "$(_PMH_COMPLETE=bash_source pmh)"

**Zsh:**

.. code-block:: bash

   # Add to ~/.zshrc
   eval "$(_PMH_COMPLETE=zsh_source pmh)"

**Fish:**

.. code-block:: bash

   # Add to ~/.config/fish/config.fish
   eval (env _PMH_COMPLETE=fish_source pmh)

Troubleshooting
---------------

Common Issues and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Database Connection Error:**

.. code-block:: bash

   # Check database configuration
   pmh config get database.url
   
   # Test database connection
   pmh db status
   
   # Initialize database if needed
   pmh db init

**Permission Denied:**

.. code-block:: bash

   # Check file permissions
   ls -la ~/.pmh/
   
   # Fix permissions
   chmod 755 ~/.pmh/
   chmod 644 ~/.pmh/config.yaml

**Web Server Won't Start:**

.. code-block:: bash

   # Check if port is already in use
   netstat -tlnp | grep 8000
   
   # Start on different port
   pmh web start --port 8080
   
   # Check logs for errors
   pmh logs show --level error

Debug Mode
~~~~~~~~~~

Enable debug mode for detailed troubleshooting:

.. code-block:: bash

   # Enable debug mode
   export PMH_DEBUG=1
   pmh web start --verbose
   
   # Or use debug flag
   pmh --verbose web start

Getting Help
------------

- Use ``--help`` with any command for detailed information
- Check the logs: ``pmh logs show``
- Validate configuration: ``pmh config validate``
- Report issues: https://github.com/python-mastery-hub/python-mastery-hub/issues