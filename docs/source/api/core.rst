.. File: docs/source/api/core.rst

Core API Reference
==================

The Core API provides access to internal Python modules, classes, and functions for extending 
and customizing Python Mastery Hub functionality.

.. currentmodule:: python_mastery_hub

Overview
--------

The Core API is organized into several main packages:

- :mod:`python_mastery_hub.core` - Core platform functionality
- :mod:`python_mastery_hub.web` - Web application components  
- :mod:`python_mastery_hub.cli` - Command-line interface
- :mod:`python_mastery_hub.database` - Database models and utilities
- :mod:`python_mastery_hub.config` - Configuration management

Core Module
-----------

.. automodule:: python_mastery_hub.core
   :members:
   :undoc-members:
   :show-inheritance:

Authentication
~~~~~~~~~~~~~~

.. automodule:: python_mastery_hub.core.auth
   :members:
   :undoc-members:
   :show-inheritance:

User Management
^^^^^^^^^^^^^^^

.. autoclass:: python_mastery_hub.core.auth.UserManager
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.auth.User
   :members:
   :undoc-members:
   :show-inheritance:

Authentication Providers
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: python_mastery_hub.core.auth.AuthProvider
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.auth.GitHubAuthProvider
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.auth.GoogleAuthProvider
   :members:
   :undoc-members:
   :show-inheritance:

Course Management
~~~~~~~~~~~~~~~~~

.. automodule:: python_mastery_hub.core.courses
   :members:
   :undoc-members:
   :show-inheritance:

Course Structure
^^^^^^^^^^^^^^^^

.. autoclass:: python_mastery_hub.core.courses.Course
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.courses.Module
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.courses.Lesson
   :members:
   :undoc-members:
   :show-inheritance:

Course Management
^^^^^^^^^^^^^^^^^

.. autoclass:: python_mastery_hub.core.courses.CourseManager
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.courses.ContentManager
   :members:
   :undoc-members:
   :show-inheritance:

Exercise Engine
~~~~~~~~~~~~~~~

.. automodule:: python_mastery_hub.core.exercises
   :members:
   :undoc-members:
   :show-inheritance:

Exercise Components
^^^^^^^^^^^^^^^^^^^

.. autoclass:: python_mastery_hub.core.exercises.Exercise
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.exercises.TestCase
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.exercises.Submission
   :members:
   :undoc-members:
   :show-inheritance:

Code Execution
^^^^^^^^^^^^^^

.. autoclass:: python_mastery_hub.core.exercises.CodeExecutor
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.exercises.SandboxExecutor
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.exercises.DockerExecutor
   :members:
   :undoc-members:
   :show-inheritance:

Testing Framework
^^^^^^^^^^^^^^^^^

.. autoclass:: python_mastery_hub.core.exercises.TestRunner
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.exercises.TestResult
   :members:
   :undoc-members:
   :show-inheritance:

Progress Tracking
~~~~~~~~~~~~~~~~~

.. automodule:: python_mastery_hub.core.progress
   :members:
   :undoc-members:
   :show-inheritance:

Progress Models
^^^^^^^^^^^^^^^

.. autoclass:: python_mastery_hub.core.progress.UserProgress
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.progress.CourseProgress
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.progress.LessonProgress
   :members:
   :undoc-members:
   :show-inheritance:

Progress Management
^^^^^^^^^^^^^^^^^^^

.. autoclass:: python_mastery_hub.core.progress.ProgressTracker
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.progress.ProgressAnalytics
   :members:
   :undoc-members:
   :show-inheritance:

Gamification
~~~~~~~~~~~~

.. automodule:: python_mastery_hub.core.gamification
   :members:
   :undoc-members:
   :show-inheritance:

Achievement System
^^^^^^^^^^^^^^^^^^

.. autoclass:: python_mastery_hub.core.gamification.Achievement
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.gamification.AchievementManager
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.gamification.Badge
   :members:
   :undoc-members:
   :show-inheritance:

Leveling System
^^^^^^^^^^^^^^^

.. autoclass:: python_mastery_hub.core.gamification.LevelSystem
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.gamification.ExperienceCalculator
   :members:
   :undoc-members:
   :show-inheritance:

Leaderboards
^^^^^^^^^^^^

.. autoclass:: python_mastery_hub.core.gamification.Leaderboard
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.gamification.LeaderboardManager
   :members:
   :undoc-members:
   :show-inheritance:

Utilities
~~~~~~~~~

.. automodule:: python_mastery_hub.core.utils
   :members:
   :undoc-members:
   :show-inheritance:

File Management
^^^^^^^^^^^^^^^

.. autofunction:: python_mastery_hub.core.utils.file_utils.save_upload
.. autofunction:: python_mastery_hub.core.utils.file_utils.get_file_hash
.. autofunction:: python_mastery_hub.core.utils.file_utils.validate_file_type

Security Utilities
^^^^^^^^^^^^^^^^^^

.. autofunction:: python_mastery_hub.core.utils.security.hash_password
.. autofunction:: python_mastery_hub.core.utils.security.verify_password
.. autofunction:: python_mastery_hub.core.utils.security.generate_token

Validation Utilities
^^^^^^^^^^^^^^^^^^^^

.. autofunction:: python_mastery_hub.core.utils.validation.validate_email
.. autofunction:: python_mastery_hub.core.utils.validation.validate_username
.. autofunction:: python_mastery_hub.core.utils.validation.sanitize_html

Database Models
---------------

.. automodule:: python_mastery_hub.database.models
   :members:
   :undoc-members:
   :show-inheritance:

Base Model
~~~~~~~~~~

.. autoclass:: python_mastery_hub.database.models.base.BaseModel
   :members:
   :undoc-members:
   :show-inheritance:

User Models
~~~~~~~~~~~

.. autoclass:: python_mastery_hub.database.models.user.User
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.database.models.user.UserProfile
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.database.models.user.UserPreferences
   :members:
   :undoc-members:
   :show-inheritance:

Course Models
~~~~~~~~~~~~~

.. autoclass:: python_mastery_hub.database.models.course.Course
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.database.models.course.Module
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.database.models.course.Lesson
   :members:
   :undoc-members:
   :show-inheritance:

Exercise Models
~~~~~~~~~~~~~~~

.. autoclass:: python_mastery_hub.database.models.exercise.Exercise
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.database.models.exercise.Submission
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.database.models.exercise.TestCaseResult
   :members:
   :undoc-members:
   :show-inheritance:

Configuration
-------------

.. automodule:: python_mastery_hub.config
   :members:
   :undoc-members:
   :show-inheritance:

Settings Management
~~~~~~~~~~~~~~~~~~~

.. autoclass:: python_mastery_hub.config.Settings
   :members:
   :undoc-members:
   :show-inheritance:

.. autofunction:: python_mastery_hub.config.get_settings

Environment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: python_mastery_hub.config.DatabaseSettings
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.config.RedisSettings
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.config.SecuritySettings
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Creating a Course
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from python_mastery_hub.core.courses import CourseManager, Course
   
   # Create course manager
   course_manager = CourseManager()
   
   # Create a new course
   course = Course(
       title="Python Fundamentals",
       description="Learn Python programming basics",
       difficulty="beginner"
   )
   
   # Save the course
   saved_course = course_manager.create_course(course)
   print(f"Created course: {saved_course.title}")

Executing Code
~~~~~~~~~~~~~~

.. code-block:: python

   from python_mastery_hub.core.exercises import CodeExecutor
   
   # Create code executor
   executor = CodeExecutor()
   
   # Execute Python code
   code = """
   def hello(name):
       return f"Hello, {name}!"
   
   print(hello("World"))
   """
   
   result = executor.execute(code, language="python")
   print(f"Output: {result.output}")
   print(f"Success: {result.success}")

Tracking Progress
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from python_mastery_hub.core.progress import ProgressTracker
   
   # Create progress tracker
   tracker = ProgressTracker()
   
   # Track lesson completion
   tracker.complete_lesson(
       user_id=123,
       lesson_id=456,
       time_spent=1800  # 30 minutes
   )
   
   # Get user progress
   progress = tracker.get_user_progress(user_id=123)
   print(f"Completed lessons: {progress.lessons_completed}")

Managing Achievements
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from python_mastery_hub.core.gamification import AchievementManager
   
   # Create achievement manager
   achievement_manager = AchievementManager()
   
   # Check for new achievements
   new_achievements = achievement_manager.check_achievements(user_id=123)
   
   for achievement in new_achievements:
       print(f"Achievement unlocked: {achievement.name}")

Error Handling
--------------

The Core API uses custom exceptions for error handling:

.. autoexception:: python_mastery_hub.core.exceptions.PMHException
.. autoexception:: python_mastery_hub.core.exceptions.AuthenticationError
.. autoexception:: python_mastery_hub.core.exceptions.PermissionError
.. autoexception:: python_mastery_hub.core.exceptions.ValidationError
.. autoexception:: python_mastery_hub.core.exceptions.NotFoundError
.. autoexception:: python_mastery_hub.core.exceptions.ExecutionError

Example error handling:

.. code-block:: python

   from python_mastery_hub.core.exceptions import ValidationError
   from python_mastery_hub.core.courses import CourseManager
   
   try:
       course_manager = CourseManager()
       course = course_manager.get_course(course_id=999)
   except NotFoundError as e:
       print(f"Course not found: {e}")
   except ValidationError as e:
       print(f"Validation error: {e}")

Testing
-------

The Core API includes comprehensive testing utilities:

.. automodule:: python_mastery_hub.core.testing
   :members:
   :undoc-members:
   :show-inheritance:

Test Fixtures
~~~~~~~~~~~~~

.. autofunction:: python_mastery_hub.core.testing.fixtures.create_test_user
.. autofunction:: python_mastery_hub.core.testing.fixtures.create_test_course
.. autofunction:: python_mastery_hub.core.testing.fixtures.create_test_exercise

Test Utilities
~~~~~~~~~~~~~~

.. autoclass:: python_mastery_hub.core.testing.utils.TestDatabaseManager
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: python_mastery_hub.core.testing.utils.MockExecutor
   :members:
   :undoc-members:
   :show-inheritance: