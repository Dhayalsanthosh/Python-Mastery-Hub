.. File: docs/source/tutorials/getting_started.rst

Getting Started
===============

Welcome to Python Mastery Hub! This tutorial will guide you through installation, 
setup, and your first steps with the platform. By the end, you'll have a working 
installation and complete your first Python lesson.

What You'll Learn
-----------------

In this tutorial, you'll:

- ✅ Install Python Mastery Hub on your system
- ✅ Set up your user account and profile
- ✅ Navigate the web interface
- ✅ Complete your first interactive lesson
- ✅ Submit your first coding exercise
- ✅ Understand the progress tracking system

Prerequisites
-------------

Before starting, ensure you have:

- **Python 3.8+** installed on your system
- **Basic command line knowledge** (opening terminal, running commands)
- **Modern web browser** (Chrome, Firefox, Safari, or Edge)
- **Internet connection** for initial setup

.. note::
   **New to Python?** No problem! Python Mastery Hub includes beginner-friendly 
   content that will teach you Python from the ground up.

Step 1: Installation
--------------------

There are several ways to install Python Mastery Hub. Choose the method that works best for you.

Method 1: pip Install (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The easiest way is to install using pip:

.. code-block:: bash

   # Install Python Mastery Hub
   pip install python-mastery-hub
   
   # Verify installation
   pmh --version

.. code-block:: text

   Python Mastery Hub v1.0.0

Method 2: Docker (Containerized)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you prefer Docker or want to avoid local Python setup:

.. code-block:: bash

   # Pull the Docker image
   docker pull pythonmasteryhub/pmh:latest
   
   # Run the container
   docker run -p 8000:8000 pythonmasteryhub/pmh:latest

Method 3: From Source (Developers)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For developers or if you want the latest features:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/python-mastery-hub/python-mastery-hub.git
   cd python-mastery-hub
   
   # Install in development mode
   pip install -e .
   
   # Or install with development dependencies
   pip install -e ".[dev]"

Troubleshooting Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Permission Denied Error:**

.. code-block:: bash

   # Use user installation
   pip install --user python-mastery-hub

**Python Version Error:**

.. code-block:: bash

   # Check Python version
   python --version
   
   # Use Python 3 explicitly if needed
   python3 -m pip install python-mastery-hub

**Virtual Environment (Recommended):**

.. code-block:: bash

   # Create virtual environment
   python -m venv pmh-env
   
   # Activate virtual environment
   # On Windows:
   pmh-env\Scripts\activate
   # On macOS/Linux:
   source pmh-env/bin/activate
   
   # Install in virtual environment
   pip install python-mastery-hub

Step 2: Initial Configuration
-----------------------------

After installation, you need to set up the configuration and database.

Initialize the Database
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Initialize database with default settings
   pmh db init
   
   # You should see output like:
   # ✅ Database initialized successfully
   # ✅ Default admin user created
   # ✅ Sample content loaded

This command:
- Creates the database schema
- Sets up the default admin user (username: ``admin``, password: ``admin``)
- Loads sample courses and content for learning

Configure Basic Settings
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Generate default configuration file
   pmh config generate --output ~/.pmh/config.yaml
   
   # View current configuration
   pmh config show

The configuration file contains important settings like database URL, security keys, 
and server options. You can edit it later as needed.

Step 3: Start the Server
------------------------

Now let's start the web server to access the platform:

.. code-block:: bash

   # Start the development server
   pmh web start --dev
   
   # You should see output like:
   # 🚀 Starting Python Mastery Hub web server...
   # 📊 Database connection: ✅ Connected
   # 🌐 Server running at: http://localhost:8000
   # 🔧 Development mode: Enabled
   # ⚡ Auto-reload: Enabled

The ``--dev`` flag enables:
- **Auto-reload**: Server restarts when code changes
- **Detailed logging**: More verbose output for debugging
- **Debug toolbar**: Additional debugging information in the browser

.. note::
   **Keep this terminal open!** The server needs to keep running. Open a new terminal 
   window for other commands.

Access the Web Interface
~~~~~~~~~~~~~~~~~~~~~~~~

1. Open your web browser
2. Navigate to http://localhost:8000
3. You should see the Python Mastery Hub login page

.. image:: ../../assets/screenshots/login-page.png
   :alt: Python Mastery Hub Login Page
   :align: center
   :width: 600px

Step 4: First Login
-------------------

Login with Default Credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the default admin credentials created during initialization:

- **Username**: ``admin``
- **Password**: ``admin``

.. warning::
   **Security Note**: Change the default admin password immediately in production environments!

After logging in, you'll see the dashboard:

.. image:: ../../assets/screenshots/dashboard.png
   :alt: Python Mastery Hub Dashboard
   :align: center
   :width: 800px

Change Default Password
~~~~~~~~~~~~~~~~~~~~~~

1. Click on your profile icon (top right)
2. Select "Account Settings"
3. Click "Change Password"
4. Enter a secure new password
5. Click "Update Password"

Step 5: Explore the Interface
-----------------------------

Let's familiarize yourself with the main interface components:

Navigation Bar
~~~~~~~~~~~~~~

The top navigation bar contains:

- **🏠 Dashboard**: Overview of your progress and recent activity
- **📚 Courses**: Browse and access available courses
- **🎯 Exercises**: Quick access to coding challenges
- **📊 Progress**: Detailed progress tracking and analytics
- **🏆 Achievements**: View earned badges and achievements
- **👤 Profile**: Account settings and personal information

Sidebar
~~~~~~~

The left sidebar shows:
- **Current course** progress
- **Quick actions** (continue lesson, practice exercises)
- **Recent activity** feed
- **Upcoming deadlines** (if any)

Main Content Area
~~~~~~~~~~~~~~~~~

The center area displays:
- **Course content** (lessons, exercises, videos)
- **Interactive code editor** for programming exercises
- **Progress visualizations** and statistics
- **Community features** (discussions, peer reviews)

Step 6: Your First Course
-------------------------

Let's start with the "Python Fundamentals" course that was included with the sample data.

Enroll in a Course
~~~~~~~~~~~~~~~~~~

1. Click **"Courses"** in the navigation bar
2. Find **"Python Fundamentals"** in the course list
3. Click **"Enroll"** button
4. Confirm enrollment in the dialog

You'll see a confirmation message and be redirected to the course overview.

Course Structure
~~~~~~~~~~~~~~~~

The course is organized into:

- **Modules**: Major topic areas (e.g., "Variables and Data Types")
- **Lessons**: Individual learning units within modules
- **Exercises**: Hands-on coding practice
- **Assessments**: Quizzes and projects to test knowledge

Navigate to First Lesson
~~~~~~~~~~~~~~~~~~~~~~~~

1. In the course overview, click **"Start Learning"**
2. You'll be taken to **"Module 1: Introduction to Python"**
3. Click on **"Lesson 1: What is Python?"**

Step 7: Complete Your First Lesson
----------------------------------

The lesson page contains several sections:

Lesson Content
~~~~~~~~~~~~~~

The main content area shows:
- **Learning objectives** for the lesson
- **Written content** with explanations and examples
- **Code examples** with syntax highlighting
- **Interactive elements** like quizzes and polls

.. image:: ../../assets/screenshots/lesson-content.png
   :alt: Lesson Content View
   :align: center
   :width: 800px

Reading the Content
~~~~~~~~~~~~~~~~~~~

1. **Read through the lesson content** carefully
2. **Take notes** using the built-in note-taking feature (click the 📝 icon)
3. **Bookmark important sections** (click the 🔖 icon)
4. **Adjust reading speed** using the progress indicator

Interactive Elements
~~~~~~~~~~~~~~~~~~~~

Many lessons include interactive elements:

- **Code snippets**: Click "Run" to execute examples
- **Quick quizzes**: Test your understanding immediately
- **Interactive diagrams**: Explore concepts visually

Mark Lesson Complete
~~~~~~~~~~~~~~~~~~~

1. After reading through the content, scroll to the bottom
2. Click **"Mark as Complete"**
3. Add any personal notes about what you learned
4. Click **"Continue to Next"** to proceed

Step 8: Your First Exercise
---------------------------

After completing the lesson, you'll be directed to a coding exercise.

Understanding the Exercise
~~~~~~~~~~~~~~~~~~~~~~~~~

The exercise page shows:

- **Problem description**: What you need to accomplish
- **Instructions**: Step-by-step guidance
- **Starter code**: Pre-written code to begin with
- **Expected output**: What your solution should produce

.. image:: ../../assets/screenshots/exercise-editor.png
   :alt: Exercise Code Editor
   :align: center
   :width: 800px

Using the Code Editor
~~~~~~~~~~~~~~~~~~~~

The integrated code editor features:

- **Syntax highlighting**: Python code is color-coded
- **Auto-completion**: Press Ctrl+Space for suggestions
- **Error indicators**: Red underlines show syntax errors
- **Line numbers**: For easy reference and debugging

Let's solve the first exercise: "Hello World"

1. **Read the problem**: Create a Python program that prints "Hello, World!"
2. **Examine starter code**:

   .. code-block:: python
   
      # Write your code below
      # TODO: Print "Hello, World!" to the console

3. **Write your solution**:

   .. code-block:: python
   
      # Write your code below
      print("Hello, World!")

Running and Testing
~~~~~~~~~~~~~~~~~~~

1. **Run your code**: Click the "Run" button (▶️)
2. **Check output**: Verify it prints "Hello, World!"
3. **Submit solution**: Click "Submit" when ready

.. code-block:: text

   🔄 Running your code...
   ✅ Output: Hello, World!
   ✅ Test 1/1 passed
   🎉 Congratulations! Exercise completed successfully.

Exercise Feedback
~~~~~~~~~~~~~~~~

After submission, you'll receive:

- **Test results**: Which test cases passed/failed
- **Score**: Points earned (usually 0-100)
- **Automated feedback**: Suggestions for improvement
- **Achievement notifications**: Badges earned for completion

Step 9: Track Your Progress
---------------------------

Let's explore the progress tracking features.

Progress Dashboard
~~~~~~~~~~~~~~~~~

1. Click **"Progress"** in the navigation bar
2. You'll see your learning dashboard with:

   - **Overall statistics**: XP earned, lessons completed, streak count
   - **Course progress**: Completion percentage for each enrolled course
   - **Recent achievements**: Newly earned badges and milestones
   - **Learning analytics**: Time spent, success rate, areas of strength

.. image:: ../../assets/screenshots/progress-dashboard.png
   :alt: Progress Dashboard
   :align: center
   :width: 800px

Understanding XP and Levels
~~~~~~~~~~~~~~~~~~~~~~~~~~

Python Mastery Hub uses a gamified progression system:

- **XP (Experience Points)**: Earned by completing lessons and exercises
- **Levels**: Your overall rank based on total XP
- **Streaks**: Consecutive days of learning activity
- **Achievements**: Special badges for specific accomplishments

Your first exercise completion should have earned you:

- **50 XP** for lesson completion
- **100 XP** for exercise completion  
- **"First Steps"** achievement badge
- **Day 1** of your learning streak

Achievement System
~~~~~~~~~~~~~~~~~

Click on **"Achievements"** to see:

- **Unlocked achievements**: Badges you've earned
- **Progress towards achievements**: How close you are to earning others
- **Achievement categories**: Learning, consistency, mastery, social

Common first achievements include:
- 🎯 **First Steps**: Complete your first lesson
- 💻 **Hello World**: Submit your first exercise
- 📅 **Getting Started**: Log in for the first time

Step 10: Customize Your Profile
-------------------------------

Let's set up your profile for a personalized experience.

Update Profile Information
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Click your **profile icon** (top right)
2. Select **"Profile Settings"**
3. Update your information:

   - **Display name**: How others see you in the community
   - **Bio**: Brief description of your learning goals
   - **Profile picture**: Upload a personal avatar
   - **Timezone**: For accurate progress tracking
   - **Learning preferences**: Difficulty level, topics of interest

Set Learning Goals
~~~~~~~~~~~~~~~~~

1. Go to **"Learning Goals"** section
2. Set your preferences:

   - **Daily learning goal**: Minutes per day (default: 30)
   - **Weekly goal**: Hours per week
   - **Skill focus areas**: What you want to improve
   - **Completion timeline**: When you want to finish courses

Notification Preferences
~~~~~~~~~~~~~~~~~~~~~~~

Configure how you want to be notified:

- **Email notifications**: For achievements, reminders, announcements
- **Browser notifications**: For real-time updates
- **Streak reminders**: Daily prompts to maintain your learning streak
- **Achievement alerts**: Immediate notification when earning badges

Step 11: Join the Community
---------------------------

Python Mastery Hub includes community features to enhance your learning.

Community Features
~~~~~~~~~~~~~~~~~

- **Discussion forums**: Ask questions and help others
- **Study groups**: Join or create learning groups
- **Peer reviews**: Review and provide feedback on others' solutions
- **Leaderboards**: Friendly competition with other learners

Getting Started with Community
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Complete your profile**: Add a bio and profile picture
2. **Join a study group**: Find others learning similar topics
3. **Participate in discussions**: Ask questions or share insights
4. **Review solutions**: Provide helpful feedback to peers

.. note::
   **Community Guidelines**: Be respectful, helpful, and constructive. 
   Our community thrives on mutual support and positive interactions.

Step 12: Next Steps
-------------------

Congratulations! You've successfully:

✅ Installed Python Mastery Hub
✅ Set up your account and profile  
✅ Completed your first lesson and exercise
✅ Explored the progress tracking system
✅ Customized your learning preferences

What's Next?
~~~~~~~~~~~

Now that you're set up, here are recommended next steps:

1. **Continue the Python Fundamentals course**
   
   - Complete Module 1: Introduction to Python
   - Progress through variables, data types, and control structures
   - Practice with more complex exercises

2. **Explore additional features** (covered in :doc:`basic_usage`)
   
   - Advanced code editor features
   - Collaboration tools
   - Progress analytics
   - Mobile app usage

3. **Set a learning routine**
   
   - Aim for 30 minutes daily
   - Use streak tracking for motivation
   - Join study groups for accountability
   - Set weekly and monthly goals

4. **Engage with the community**
   
   - Ask questions when stuck
   - Help others with their challenges
   - Share your learning progress
   - Participate in coding challenges

Troubleshooting
---------------

Common Issues and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~

**Server won't start:**

.. code-block:: bash

   # Check if port is already in use
   pmh web start --port 8080
   
   # Or check server status
   pmh web status

**Database errors:**

.. code-block:: bash

   # Reset database if needed
   pmh db reset --force
   pmh db init

**Login issues:**

.. code-block:: bash

   # Reset admin password
   pmh users reset-password admin --password newpassword

**Performance issues:**

.. code-block:: bash

   # Check system requirements
   pmh config show
   
   # Start with fewer workers
   pmh web start --workers 1

Getting Help
~~~~~~~~~~~

If you encounter issues:

1. **Check the FAQ**: Common questions and solutions
2. **Search documentation**: Use the search feature
3. **Community forums**: Ask questions and get help from other users
4. **GitHub issues**: Report bugs or request features
5. **Email support**: Contact support@pythonmasteryhub.com

Additional Resources
-------------------

**Learning Resources:**
- :doc:`../notebooks/01_python_basics` - Interactive Python tutorial
- :doc:`basic_usage` - Detailed feature guide
- :doc:`../examples/index` - Practical examples and use cases

**Technical Resources:**
- :doc:`../api/index` - API documentation
- :doc:`../development/index` - Contributing guide
- :doc:`deployment` - Production deployment guide

**Community:**
- `Discord Server <https://discord.gg/pythonmasteryhub>`_ - Real-time chat
- `GitHub Discussions <https://github.com/python-mastery-hub/python-mastery-hub/discussions>`_ - Community Q&A
- `Twitter <https://twitter.com/PythonMasteryHub>`_ - Updates and tips

Feedback
--------

Help us improve this tutorial! Please let us know:

- What worked well for you?
- What was confusing or unclear?
- What additional information would be helpful?
- Did you encounter any errors or issues?

Send feedback to: tutorials@pythonmasteryhub.com

.. admonition:: Congratulations! 🎉
   :class: tip

   You've completed the Getting Started tutorial! You now have a working 
   Python Mastery Hub installation and understand the basic workflow. 
   
   **Ready for more?** Continue with :doc:`basic_usage` to learn about 
   advanced features and best practices.