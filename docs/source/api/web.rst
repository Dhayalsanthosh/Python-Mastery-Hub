.. File: docs/source/api/web.rst

Web API Reference
=================

The Web API provides RESTful HTTP endpoints for all Python Mastery Hub functionality. 
This API powers the web application and can be used for custom integrations.

.. note::
   **Base URL**: ``https://api.pythonmasteryhub.com/v1/``
   
   **Authentication**: All endpoints require authentication unless marked as public.

Overview
--------

The Web API is organized into several main sections:

- **Authentication**: User authentication and authorization
- **Users**: User management and profiles
- **Courses**: Course creation, management, and enrollment
- **Lessons**: Lesson content and progress tracking
- **Exercises**: Code exercises and submissions
- **Progress**: Learning progress and analytics
- **Achievements**: Gamification and achievement system
- **Admin**: Administrative functions

Base Response Format
--------------------

All API responses follow a consistent format:

**Success Response:**

.. code-block:: json

   {
     "success": true,
     "data": {
       // Response data here
     },
     "meta": {
       "timestamp": "2024-01-15T10:30:00Z",
       "request_id": "req_1234567890"
     }
   }

**Error Response:**

.. code-block:: json

   {
     "success": false,
     "error": {
       "code": "validation_error",
       "message": "Invalid input data",
       "details": {
         "field": "email",
         "issue": "Invalid email format"
       }
     },
     "meta": {
       "timestamp": "2024-01-15T10:30:00Z",
       "request_id": "req_1234567890"
     }
   }

Authentication Endpoints
------------------------

POST /auth/register
~~~~~~~~~~~~~~~~~~~

Register a new user account.

**Request:**

.. code-block:: http

   POST /auth/register
   Content-Type: application/json
   
   {
     "username": "john_doe",
     "email": "john@example.com",
     "password": "secure_password123",
     "first_name": "John",
     "last_name": "Doe"
   }

**Response:**

.. code-block:: json

   {
     "success": true,
     "data": {
       "user": {
         "id": 123,
         "username": "john_doe",
         "email": "john@example.com",
         "first_name": "John",
         "last_name": "Doe",
         "created_at": "2024-01-15T10:30:00Z"
       },
       "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
       "refresh_token": "refresh_token_here",
       "expires_in": 3600
     }
   }

POST /auth/login
~~~~~~~~~~~~~~~~

Authenticate with username/email and password.

**Request:**

.. code-block:: http

   POST /auth/login
   Content-Type: application/json
   
   {
     "username": "john_doe",
     "password": "secure_password123"
   }

**Response:**

.. code-block:: json

   {
     "success": true,
     "data": {
       "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
       "refresh_token": "refresh_token_here",
       "expires_in": 3600,
       "user": {
         "id": 123,
         "username": "john_doe",
         "email": "john@example.com"
       }
     }
   }

POST /auth/refresh
~~~~~~~~~~~~~~~~~~

Refresh an access token using a refresh token.

**Request:**

.. code-block:: http

   POST /auth/refresh
   Content-Type: application/json
   
   {
     "refresh_token": "refresh_token_here"
   }

GET /auth/oauth/{provider}
~~~~~~~~~~~~~~~~~~~~~~~~~~

Initiate OAuth authentication with external providers.

**Supported providers:** ``github``, ``google``, ``discord``

**Request:**

.. code-block:: http

   GET /auth/oauth/github?redirect_uri=https://app.pythonmasteryhub.com/callback

POST /auth/logout
~~~~~~~~~~~~~~~~~

Logout and invalidate tokens.

**Request:**

.. code-block:: http

   POST /auth/logout
   Authorization: Bearer {access_token}

User Endpoints
--------------

GET /users/me
~~~~~~~~~~~~~

Get current user profile.

**Request:**

.. code-block:: http

   GET /users/me
   Authorization: Bearer {access_token}

**Response:**

.. code-block:: json

   {
     "success": true,
     "data": {
       "id": 123,
       "username": "john_doe",
       "email": "john@example.com",
       "first_name": "John",
       "last_name": "Doe",
       "avatar_url": "https://cdn.pythonmasteryhub.com/avatars/123.jpg",
       "bio": "Learning Python for data science",
       "timezone": "UTC",
       "created_at": "2024-01-15T10:30:00Z",
       "last_login_at": "2024-01-20T15:45:00Z",
       "stats": {
         "courses_completed": 5,
         "exercises_solved": 127,
         "current_streak": 12,
         "total_xp": 2847
       }
     }
   }

PUT /users/me
~~~~~~~~~~~~~

Update current user profile.

**Request:**

.. code-block:: http

   PUT /users/me
   Authorization: Bearer {access_token}
   Content-Type: application/json
   
   {
     "first_name": "Johnny",
     "bio": "Full-stack Python developer",
     "timezone": "America/New_York"
   }

GET /users/{user_id}
~~~~~~~~~~~~~~~~~~~~

Get public user profile (limited information).

**Request:**

.. code-block:: http

   GET /users/456
   Authorization: Bearer {access_token}

**Response:**

.. code-block:: json

   {
     "success": true,
     "data": {
       "id": 456,
       "username": "jane_dev",
       "avatar_url": "https://cdn.pythonmasteryhub.com/avatars/456.jpg",
       "bio": "Python enthusiast",
       "joined_at": "2024-01-10T08:20:00Z",
       "public_stats": {
         "courses_completed": 8,
         "achievements_count": 15,
         "public_streak": 25
       }
     }
   }

Course Endpoints
----------------

GET /courses
~~~~~~~~~~~~

List all available courses with filtering and pagination.

**Request:**

.. code-block:: http

   GET /courses?difficulty=beginner&limit=20&cursor=eyJpZCI6MTIzfQ
   Authorization: Bearer {access_token}

**Query Parameters:**

- ``difficulty``: Filter by difficulty (beginner, intermediate, advanced)
- ``category``: Filter by category
- ``search``: Search in title and description
- ``limit``: Number of results (max 100)
- ``cursor``: Pagination cursor

**Response:**

.. code-block:: json

   {
     "success": true,
     "data": {
       "courses": [
         {
           "id": 1,
           "title": "Python Fundamentals",
           "description": "Learn Python programming basics",
           "difficulty": "beginner",
           "estimated_hours": 20,
           "modules_count": 8,
           "lessons_count": 45,
           "enrollment_count": 1547,
           "rating": 4.8,
           "thumbnail_url": "https://cdn.pythonmasteryhub.com/courses/1/thumb.jpg",
           "instructor": {
             "id": 10,
             "name": "Dr. Sarah Johnson",
             "avatar_url": "https://cdn.pythonmasteryhub.com/avatars/10.jpg"
           }
         }
       ],
       "pagination": {
         "has_more": true,
         "next_cursor": "eyJpZCI6MTQzfQ"
       }
     }
   }

GET /courses/{course_id}
~~~~~~~~~~~~~~~~~~~~~~~~

Get detailed course information.

**Request:**

.. code-block:: http

   GET /courses/1
   Authorization: Bearer {access_token}

POST /courses/{course_id}/enroll
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enroll in a course.

**Request:**

.. code-block:: http

   POST /courses/1/enroll
   Authorization: Bearer {access_token}

**Response:**

.. code-block:: json

   {
     "success": true,
     "data": {
       "enrollment": {
         "id": 789,
         "course_id": 1,
         "user_id": 123,
         "enrolled_at": "2024-01-20T16:00:00Z",
         "progress_percentage": 0.0
       }
     }
   }

GET /courses/my-courses
~~~~~~~~~~~~~~~~~~~~~~~

Get current user's enrolled courses.

**Request:**

.. code-block:: http

   GET /courses/my-courses
   Authorization: Bearer {access_token}

Lesson Endpoints
----------------

GET /courses/{course_id}/modules/{module_id}/lessons/{lesson_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get lesson content and details.

**Request:**

.. code-block:: http

   GET /courses/1/modules/2/lessons/5
   Authorization: Bearer {access_token}

**Response:**

.. code-block:: json

   {
     "success": true,
     "data": {
       "lesson": {
         "id": 5,
         "title": "Variables and Data Types",
         "content": "# Variables and Data Types\n\nIn Python, variables are...",
         "content_type": "lesson",
         "estimated_minutes": 15,
         "order_index": 1,
         "exercises": [
           {
             "id": 12,
             "title": "Create Variables",
             "difficulty": "beginner"
           }
         ]
       },
       "user_progress": {
         "status": "in_progress",
         "started_at": "2024-01-20T16:15:00Z",
         "time_spent_minutes": 8,
         "bookmarked": false
       }
     }
   }

POST /lessons/{lesson_id}/complete
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mark a lesson as completed.

**Request:**

.. code-block:: http

   POST /lessons/5/complete
   Authorization: Bearer {access_token}
   Content-Type: application/json
   
   {
     "time_spent_minutes": 15,
     "notes": "Great introduction to variables"
   }

Exercise Endpoints
------------------

GET /exercises/{exercise_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get exercise details and starter code.

**Request:**

.. code-block:: http

   GET /exercises/12
   Authorization: Bearer {access_token}

**Response:**

.. code-block:: json

   {
     "success": true,
     "data": {
       "exercise": {
         "id": 12,
         "title": "Create Variables",
         "description": "Create variables of different data types",
         "instructions": "1. Create a string variable named 'name'\n2. Create an integer variable named 'age'",
         "starter_code": "# Your code here\nname = \nage = ",
         "difficulty": "beginner",
         "max_attempts": 3,
         "time_limit_minutes": 30,
         "hints": [
           "Remember to use quotes for strings",
           "Integers don't need quotes"
         ]
       },
       "user_progress": {
         "attempts": 1,
         "best_score": 0.0,
         "status": "not_started"
       }
     }
   }

POST /exercises/{exercise_id}/submit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Submit exercise solution for testing.

**Request:**

.. code-block:: http

   POST /exercises/12/submit
   Authorization: Bearer {access_token}
   Content-Type: application/json
   
   {
     "code": "name = 'John Doe'\nage = 25",
     "attempt_number": 1
   }

**Response:**

.. code-block:: json

   {
     "success": true,
     "data": {
       "submission": {
         "id": 456,
         "status": "passed",
         "score": 100.0,
         "execution_time_ms": 45,
         "test_results": [
           {
             "test_case": "Check name variable",
             "status": "passed",
             "points_earned": 50.0
           },
           {
             "test_case": "Check age variable", 
             "status": "passed",
             "points_earned": 50.0
           }
         ],
         "feedback": [
           {
             "type": "automated",
             "message": "Great job! Your solution is correct.",
             "severity": "info"
           }
         ]
       }
     }
   }

GET /exercises/{exercise_id}/submissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get submission history for an exercise.

**Request:**

.. code-block:: http

   GET /exercises/12/submissions
   Authorization: Bearer {access_token}

Progress Endpoints
------------------

GET /progress/overview
~~~~~~~~~~~~~~~~~~~~~~

Get overall learning progress overview.

**Request:**

.. code-block:: http

   GET /progress/overview
   Authorization: Bearer {access_token}

**Response:**

.. code-block:: json

   {
     "success": true,
     "data": {
       "overview": {
         "total_xp": 2847,
         "current_level": 12,
         "xp_to_next_level": 153,
         "courses_enrolled": 3,
         "courses_completed": 1,
         "lessons_completed": 67,
         "exercises_solved": 127,
         "current_streak": 12,
         "longest_streak": 28,
         "time_spent_hours": 45.5
       },
       "recent_activity": [
         {
           "type": "lesson_complete",
           "item": "Variables and Data Types",
           "timestamp": "2024-01-20T16:30:00Z",
           "xp_earned": 25
         }
       ]
     }
   }

GET /progress/courses/{course_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get detailed progress for a specific course.

**Request:**

.. code-block:: http

   GET /progress/courses/1
   Authorization: Bearer {access_token}

GET /progress/analytics
~~~~~~~~~~~~~~~~~~~~~~

Get detailed learning analytics and insights.

**Request:**

.. code-block:: http

   GET /progress/analytics?period=30days
   Authorization: Bearer {access_token}

Achievement Endpoints
---------------------

GET /achievements
~~~~~~~~~~~~~~~~~

Get all available achievements.

**Request:**

.. code-block:: http

   GET /achievements
   Authorization: Bearer {access_token}

**Response:**

.. code-block:: json

   {
     "success": true,
     "data": {
       "achievements": [
         {
           "id": 1,
           "name": "First Steps",
           "description": "Complete your first lesson",
           "category": "learning",
           "tier": "bronze",
           "icon_name": "first-steps",
           "points_reward": 50,
           "unlocked": true,
           "unlocked_at": "2024-01-20T16:30:00Z"
         },
         {
           "id": 2,
           "name": "Speed Demon",
           "description": "Complete 10 exercises in one day",
           "category": "consistency",
           "tier": "silver",
           "icon_name": "speed",
           "points_reward": 200,
           "unlocked": false,
           "progress": {
             "current": 7,
             "required": 10
           }
         }
       ]
     }
   }

GET /achievements/my-achievements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get current user's unlocked achievements.

**Request:**

.. code-block:: http

   GET /achievements/my-achievements
   Authorization: Bearer {access_token}

GET /leaderboards
~~~~~~~~~~~~~~~~~

Get leaderboard rankings.

**Request:**

.. code-block:: http

   GET /leaderboards?type=weekly&metric=xp&limit=50
   Authorization: Bearer {access_token}

**Query Parameters:**

- ``type``: Leaderboard type (daily, weekly, monthly, all_time)
- ``metric``: Ranking metric (xp, streak, completions)
- ``limit``: Number of results (max 100)

Admin Endpoints
---------------

.. note::
   Admin endpoints require administrator privileges.

GET /admin/users
~~~~~~~~~~~~~~~~

List and manage users (admin only).

POST /admin/courses
~~~~~~~~~~~~~~~~~~~

Create new courses (admin only).

PUT /admin/courses/{course_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update course content (admin only).

DELETE /admin/users/{user_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Delete user account (admin only).

Webhooks
--------

POST /webhooks
~~~~~~~~~~~~~~

Create a new webhook subscription.

**Request:**

.. code-block:: http

   POST /webhooks
   Authorization: Bearer {access_token}
   Content-Type: application/json
   
   {
     "url": "https://your-app.com/webhooks/pmh",
     "events": ["course.completed", "user.registered"],
     "secret": "your_webhook_secret"
   }

GET /webhooks
~~~~~~~~~~~~~

List webhook subscriptions.

DELETE /webhooks/{webhook_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Delete a webhook subscription.

Error Codes
-----------

Common error codes returned by the API:

- ``400`` - Bad Request
  
  - ``validation_error``: Invalid input data
  - ``missing_required_field``: Required field missing
  - ``invalid_format``: Invalid data format

- ``401`` - Unauthorized
  
  - ``invalid_credentials``: Invalid username/password
  - ``token_expired``: Access token expired
  - ``token_invalid``: Invalid access token

- ``403`` - Forbidden
  
  - ``insufficient_permissions``: User lacks required permissions
  - ``account_suspended``: User account is suspended
  - ``feature_not_available``: Feature not available for user tier

- ``404`` - Not Found
  
  - ``resource_not_found``: Requested resource doesn't exist
  - ``endpoint_not_found``: API endpoint doesn't exist

- ``429`` - Too Many Requests
  
  - ``rate_limit_exceeded``: Rate limit exceeded
  - ``daily_quota_exceeded``: Daily API quota exceeded

- ``500`` - Internal Server Error
  
  - ``internal_error``: Unexpected server error
  - ``service_unavailable``: Service temporarily unavailable

SDK Usage Examples
------------------

**Python SDK:**

.. code-block:: python

   from pythonmasteryhub import Client
   
   # Initialize client
   client = Client(api_key="your_api_key")
   
   # Get user profile
   user = client.users.get_current_user()
   print(f"Hello, {user.first_name}!")
   
   # List courses
   courses = client.courses.list(difficulty="beginner")
   for course in courses:
       print(f"- {course.title}")

**JavaScript SDK:**

.. code-block:: javascript

   import { PythonMasteryHub } from '@pythonmasteryhub/sdk';
   
   // Initialize client
   const pmh = new PythonMasteryHub({
     apiKey: 'your_api_key'
   });
   
   // Get user progress
   const progress = await pmh.progress.getOverview();
   console.log(`XP: ${progress.total_xp}`);

Rate Limiting
-------------

API rate limits are applied per user/API key:

- **Free tier**: 100 requests/hour
- **Pro tier**: 1,000 requests/hour  
- **Enterprise**: 10,000 requests/hour

Rate limit headers are included in responses:

.. code-block:: http

   X-RateLimit-Limit: 1000
   X-RateLimit-Remaining: 999
   X-RateLimit-Reset: 1640995200
   X-RateLimit-Type: user