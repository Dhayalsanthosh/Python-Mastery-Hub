.. File: docs/source/api/index.rst

API Reference
=============

This section provides comprehensive documentation for all Python Mastery Hub APIs, modules, and components.

Overview
--------

Python Mastery Hub provides three main API interfaces:

1. **Core API**: Internal Python modules and classes for extending functionality
2. **Web API**: RESTful HTTP API for web applications and integrations
3. **CLI API**: Command-line interface for automation and scripting

.. note::
   **API Stability**: We follow semantic versioning. The public API is stable across minor versions,
   with breaking changes only in major version releases.

Quick Navigation
----------------

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: Core API
      :link: core
      :link-type: doc

      Internal Python modules, classes, and functions for building extensions
      and customizing the platform.

   .. grid-item-card:: Web API
      :link: web
      :link-type: doc

      RESTful HTTP API endpoints for authentication, course management,
      progress tracking, and more.

   .. grid-item-card:: CLI API
      :link: cli
      :link-type: doc

      Command-line interface for server management, content creation,
      and administrative tasks.

   .. grid-item-card:: Examples
      :link: ../examples/api_examples
      :link-type: doc

      Practical examples and code snippets for using all APIs effectively.

Core Components
---------------

The Python Mastery Hub platform is built around these core components:

**Authentication & Users**
   - User management and authentication
   - OAuth2 integration with GitHub, Google
   - Role-based access control (RBAC)
   - Session management

**Course Management**
   - Course, module, and lesson structure
   - Content versioning and publishing
   - Prerequisites and learning paths
   - Assessment and grading

**Exercise Engine**
   - Code execution sandbox
   - Automated testing framework
   - Plagiarism detection
   - Performance metrics

**Progress Tracking**
   - User progress analytics
   - Achievement system
   - Learning streaks and goals
   - Reporting and insights

**Web Interface**
   - Interactive code editor
   - Real-time collaboration
   - Responsive design
   - Accessibility features

API Documentation Sections
---------------------------

.. toctree::
   :maxdepth: 2

   core
   web
   cli

Authentication
--------------

All APIs support multiple authentication methods:

**API Keys**
   - For programmatic access
   - Scoped permissions
   - Rate limiting support

**JWT Tokens**
   - For web applications
   - Short-lived access tokens
   - Refresh token rotation

**OAuth2**
   - GitHub, Google, Discord
   - Standard OAuth2 flow
   - Automatic user creation

Example API Usage
-----------------

Here's a quick example of using the Web API:

.. code-block:: python

   import requests
   
   # Authenticate
   response = requests.post("https://api.pythonmasteryhub.com/auth/login", {
       "username": "your_username",
       "password": "your_password"
   })
   token = response.json()["access_token"]
   
   # Get user courses
   headers = {"Authorization": f"Bearer {token}"}
   courses = requests.get(
       "https://api.pythonmasteryhub.com/courses/my-courses",
       headers=headers
   ).json()
   
   print(f"You have {len(courses)} courses")

Rate Limiting
-------------

All APIs implement rate limiting to ensure fair usage:

- **Anonymous requests**: 100 requests per hour
- **Authenticated requests**: 1000 requests per hour
- **Premium accounts**: 5000 requests per hour

Rate limit headers are included in all responses:

.. code-block:: http

   X-RateLimit-Limit: 1000
   X-RateLimit-Remaining: 999
   X-RateLimit-Reset: 1640995200

Error Handling
--------------

All APIs use consistent error response format:

.. code-block:: json

   {
     "error": {
       "code": "validation_error",
       "message": "Invalid input data",
       "details": {
         "field": "email",
         "issue": "Invalid email format"
       }
     },
     "request_id": "req_1234567890"
   }

Common HTTP status codes:

- ``200 OK``: Success
- ``201 Created``: Resource created
- ``400 Bad Request``: Invalid input
- ``401 Unauthorized``: Authentication required
- ``403 Forbidden``: Access denied
- ``404 Not Found``: Resource not found
- ``429 Too Many Requests``: Rate limit exceeded
- ``500 Internal Server Error``: Server error

Pagination
----------

List endpoints support cursor-based pagination:

.. code-block:: http

   GET /api/courses?limit=20&cursor=eyJpZCI6MTIzfQ
   
   {
     "data": [...],
     "pagination": {
       "has_more": true,
       "next_cursor": "eyJpZCI6MTQzfQ"
     }
   }

Webhooks
--------

Set up webhooks to receive real-time notifications:

.. code-block:: python

   import requests
   
   webhook_config = {
       "url": "https://your-app.com/webhooks/pmh",
       "events": ["course.completed", "user.registered"],
       "secret": "your_webhook_secret"
   }
   
   response = requests.post(
       "https://api.pythonmasteryhub.com/webhooks",
       json=webhook_config,
       headers={"Authorization": f"Bearer {token}"}
   )

Supported webhook events:

- ``user.registered``: New user registration
- ``course.completed``: User completed a course
- ``exercise.submitted``: Exercise submission
- ``achievement.unlocked``: Achievement earned
- ``payment.completed``: Payment processed

SDKs and Libraries
------------------

Official SDKs are available for popular languages:

**Python**
   .. code-block:: bash
   
      pip install pythonmasteryhub-sdk

**JavaScript/Node.js**
   .. code-block:: bash
   
      npm install @pythonmasteryhub/sdk

**Go**
   .. code-block:: bash
   
      go get github.com/python-mastery-hub/go-sdk

**PHP**
   .. code-block:: bash
   
      composer require pythonmasteryhub/php-sdk

API Versioning
--------------

We use URL-based versioning:

- Current version: ``v1``
- Base URL: ``https://api.pythonmasteryhub.com/v1/``
- Version in header: ``API-Version: v1``

Deprecated versions remain available for 12 months after replacement.

Testing
-------

Use our sandbox environment for testing:

- **Sandbox URL**: ``https://sandbox-api.pythonmasteryhub.com/``
- **Test credentials**: Provided in developer dashboard
- **Mock data**: Realistic test data available
- **No charges**: All operations are free in sandbox

Support
-------

Need help with the API?

- 📖 **Documentation**: You're reading it!
- 🎯 **Examples**: Check the :doc:`../examples/api_examples` section
- 💬 **Support**: api-support@pythonmasteryhub.com
- 🐛 **Bug Reports**: `GitHub Issues <https://github.com/python-mastery-hub/python-mastery-hub/issues>`_