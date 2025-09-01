Basic Usage
===========

Now that you have Python Mastery Hub installed and running, let's explore the platform's 
core features in detail. This tutorial covers everything from navigating courses to 
mastering the code editor and tracking your progress effectively.

.. note::
   **Prerequisites**: Complete the :doc:`getting_started` tutorial before proceeding. 
   You should have Python Mastery Hub installed and have completed your first lesson.

What You'll Learn
-----------------

In this tutorial, you'll master:

- 🗺️ **Course Navigation**: Efficiently browse and organize your learning
- 💻 **Code Editor Mastery**: Advanced editor features and shortcuts
- 📝 **Exercise Strategies**: Approaches for solving coding challenges
- 📊 **Progress Tracking**: Understanding analytics and goal setting
- 🏆 **Achievement System**: Maximizing XP and earning badges
- 👥 **Community Features**: Collaboration and peer learning
- 🔧 **Customization**: Personalizing your learning environment

Course Management
-----------------

Understanding Course Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python Mastery Hub organizes content hierarchically:

.. code-block:: text

   Course
   ├── Module 1: Topic Area
   │   ├── Lesson 1.1: Concept Introduction
   │   ├── Lesson 1.2: Practical Examples
   │   ├── Exercise 1.1: Basic Practice
   │   └── Exercise 1.2: Advanced Challenge
   ├── Module 2: Next Topic
   │   └── ...
   └── Final Project

**Course Types:**

- **Guided Courses**: Structured learning paths with prerequisites
- **Topic Collections**: Standalone lessons on specific subjects
- **Challenge Series**: Progressive difficulty coding challenges
- **Projects**: Real-world application development

Browsing and Filtering Courses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The course catalog offers powerful filtering options:

1. **Access the Course Catalog**:
   
   - Click **"Courses"** in the navigation bar
   - Use the search bar for specific topics
   - Apply filters to narrow results

2. **Available Filters**:
   
   - **Difficulty Level**: Beginner, Intermediate, Advanced
   - **Duration**: Short (< 5 hours), Medium (5-20 hours), Long (> 20 hours)
   - **Category**: Web Development, Data Science, Automation, etc.
   - **Prerequisites**: Courses you can start immediately
   - **Language Features**: Python 3.8+, async/await, type hints

3. **Sorting Options**:
   
   - **Popularity**: Most enrolled courses
   - **Rating**: Highest rated by students
   - **Recent**: Newly added or updated courses
   - **Difficulty**: Easiest to hardest progression

.. image:: ../../assets/screenshots/course-catalog.png
   :alt: Course Catalog with Filters
   :align: center
   :width: 800px

Course Enrollment and Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Enrolling in Courses:**

1. **Browse** available courses using filters
2. **Preview** course content and structure
3. **Check prerequisites** and estimated time
4. **Click "Enroll"** to add to your learning path
5. **Set completion goals** (optional)

**Managing Enrolled Courses:**

- **My Courses Dashboard**: Access from the main navigation
- **Course Progress**: Visual indicators show completion percentage
- **Recently Accessed**: Quick links to continue where you left off
- **Favorites**: Star important courses for easy access
- **Archive**: Hide completed courses from active view

Course Progress States
~~~~~~~~~~~~~~~~~~~~~

Courses can be in different states:

- **🚀 Not Started**: Enrolled but no lessons completed
- **📚 In Progress**: Actively working through content
- **⏸️ Paused**: Temporarily stopped (maintains progress)
- **✅ Completed**: All required content finished
- **🏆 Mastered**: Completed with high scores and achievements

Mastering the Code Editor
-------------------------

The integrated code editor is designed specifically for learning Python. 
Let's explore its powerful features.

Editor Interface Overview
~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: ../../assets/screenshots/code-editor-overview.png
   :alt: Code Editor Interface
   :align: center
   :width: 800px

**Main Components:**

1. **Code Editor Pane**: Where you write your Python code
2. **Output Console**: Shows execution results and error messages
3. **Test Panel**: Displays test case results and feedback
4. **Toolbar**: Quick access to run, submit, and formatting tools
5. **Sidebar**: File explorer, hints, and reference materials

Essential Editor Features
~~~~~~~~~~~~~~~~~~~~~~~~

**Syntax Highlighting and IntelliSense:**

.. code-block:: python

   # Type this to see IntelliSense in action
   import datetime
   
   now = datetime.datetime.  # <- Auto-completion appears here
   print(now.strftime("%Y-%m-%d"))  # <- Syntax highlighted

**Code Formatting and Linting:**

- **Auto-format**: Press ``Ctrl+Shift+F`` (or ``Cmd+Shift+F`` on Mac)
- **Lint warnings**: Yellow underlines show style issues
- **Error indicators**: Red underlines show syntax errors
- **Quick fixes**: Click the lightbulb icon for suggestions

**Multi-file Support:**

For complex exercises, you can work with multiple files:

.. code-block:: text

   exercise_folder/
   ├── main.py          # Main solution file
   ├── utils.py         # Helper functions
   ├── data.csv         # Data files
   └── tests.py         # Additional test cases

**Code Snippets and Templates:**

Use built-in snippets for common patterns:

- Type ``def`` + Tab → Function template
- Type ``class`` + Tab → Class template  
- Type ``if`` + Tab → Conditional template
- Type ``for`` + Tab → Loop template

Keyboard Shortcuts
~~~~~~~~~~~~~~~~~

Master these shortcuts for efficient coding:

**Navigation:**

- ``Ctrl+G``: Go to line number
- ``Ctrl+F``: Find and replace
- ``Ctrl+D``: Select next occurrence
- ``Alt+Up/Down``: Move line up/down

**Editing:**

- ``Ctrl+/``: Toggle line comment
- ``Ctrl+Shift+K``: Delete line
- ``Ctrl+Enter``: Run current line/selection
- ``Tab/Shift+Tab``: Indent/unindent

**Code Intelligence:**

- ``Ctrl+Space``: Trigger auto-completion
- ``Ctrl+Click``: Go to definition
- ``F12``: Go to declaration
- ``Shift+F12``: Find all references

Running and Testing Code
~~~~~~~~~~~~~~~~~~~~~~~

**Execution Options:**

1. **Run All** (``Ctrl+F5``): Execute entire file
2. **Run Selection** (``F9``): Execute highlighted code
3. **Run Line** (``Ctrl+Enter``): Execute current line
4. **Debug Mode** (``F5``): Step through code with debugger

**Test Integration:**

Every exercise includes automated tests:

.. code-block:: python

   # Your solution
   def calculate_average(numbers):
       return sum(numbers) / len(numbers)
   
   # Tests run automatically when you click "Submit"
   # Test 1: calculate_average([1, 2, 3]) should return 2.0
   # Test 2: calculate_average([10, 20]) should return 15.0
   # Test 3: Empty list should raise appropriate error

**Understanding Test Results:**

- **✅ Passed**: Test case succeeded
- **❌ Failed**: Expected vs actual output shown
- **⚠️ Error**: Runtime error occurred
- **⏱️ Timeout**: Code took too long to execute

Exercise Solving Strategies
---------------------------

Effective Problem-Solving Approach
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Follow this systematic approach for coding exercises:

**1. Read and Understand**

- Read the problem statement carefully
- Identify input and output requirements
- Note any constraints or edge cases
- Look at provided examples

**2. Plan Your Solution**

- Break down the problem into smaller steps
- Choose appropriate data structures
- Consider algorithm complexity
- Sketch out the logic before coding

**3. Implement Incrementally**

- Start with a basic working solution
- Test with simple cases first
- Add complexity gradually
- Refactor for clarity and efficiency

**4. Test Thoroughly**

- Test with provided examples
- Consider edge cases (empty input, large numbers, etc.)
- Verify error handling
- Check performance with large inputs

Common Exercise Types
~~~~~~~~~~~~~~~~~~~~

**Algorithm Challenges:**

.. code-block:: python

   # Example: Find the longest word in a sentence
   def longest_word(sentence):
       words = sentence.split()
       return max(words, key=len)
   
   # Test your understanding of:
   # - String manipulation
   # - List operations  
   # - Built-in functions

**Data Structure Problems:**

.. code-block:: python

   # Example: Implement a simple stack
   class Stack:
       def __init__(self):
           self.items = []
       
       def push(self, item):
           self.items.append(item)
       
       def pop(self):
           return self.items.pop()
       
       def is_empty(self):
           return len(self.items) == 0

**Real-world Applications:**

.. code-block:: python

   # Example: Parse and analyze log files
   def analyze_logs(log_file):
       error_count = 0
       with open(log_file, 'r') as f:
           for line in f:
               if 'ERROR' in line:
                   error_count += 1
       return error_count

Using Hints Effectively
~~~~~~~~~~~~~~~~~~~~~~~

Each exercise includes a hint system:

**Hint Levels:**

1. **General Direction**: Points you toward the right approach
2. **Specific Technique**: Suggests specific functions or methods
3. **Code Snippet**: Provides partial implementation
4. **Full Solution**: Complete answer (use sparingly!)

**Best Practices:**

- Try solving without hints first
- Use hints progressively (start with Level 1)
- Understand why the hint helps
- Apply the technique to similar problems

Getting Unstuck
~~~~~~~~~~~~~~~

When you're stuck on an exercise:

1. **Take a Break**: Sometimes stepping away helps
2. **Re-read the Problem**: You might have missed something
3. **Use Print Debugging**: Add print statements to see what's happening
4. **Check Similar Examples**: Look at related lessons or exercises
5. **Ask for Help**: Use community forums or discussion features

Progress Tracking and Analytics
------------------------------

Understanding Your Dashboard
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The progress dashboard provides comprehensive learning insights:

.. image:: ../../assets/screenshots/progress-analytics.png
   :alt: Progress Analytics Dashboard
   :align: center
   :width: 800px

**Key Metrics:**

- **Learning Streak**: Consecutive days of activity
- **Total XP**: Experience points earned across all activities
- **Current Level**: Your rank based on total XP
- **Course Progress**: Completion percentage for each enrolled course
- **Time Invested**: Hours spent learning and practicing
- **Success Rate**: Percentage of exercises solved correctly

**Weekly Goals:**

Set and track weekly learning targets:

- **Time Goal**: Hours of study per week
- **Exercise Goal**: Number of coding challenges to complete
- **Course Goal**: Lessons or modules to finish
- **Streak Goal**: Consecutive days of learning

Learning Analytics Deep Dive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Skill Development Tracking:**

Monitor progress in specific areas:

- **Python Fundamentals**: Variables, functions, control flow
- **Data Structures**: Lists, dictionaries, sets, tuples
- **Object-Oriented Programming**: Classes, inheritance, polymorphism
- **Web Development**: Flask, Django, REST APIs
- **Data Science**: NumPy, Pandas, data analysis

**Time Analysis:**

Understand your learning patterns:

.. code-block:: text

   📊 Learning Time Analysis
   
   Peak Learning Hours: 7-9 PM
   Most Productive Day: Tuesday
   Average Session: 45 minutes
   Longest Streak: 12 days
   
   💡 Recommendation: Schedule consistent 
   study time during your peak hours!

**Performance Insights:**

Identify strengths and areas for improvement:

- **Fastest Topics**: Areas you grasp quickly
- **Challenging Areas**: Topics requiring more practice
- **Common Mistakes**: Frequent error patterns
- **Improvement Trends**: Progress over time

Setting and Achieving Goals
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**SMART Goals Framework:**

Create Specific, Measurable, Achievable, Relevant, Time-bound goals:

.. code-block:: text

   ❌ Vague: "Learn Python better"
   ✅ SMART: "Complete Python Fundamentals course 
            with 90%+ exercise scores by end of month"

**Goal Types:**

- **Daily Goals**: 30 minutes of study, 2 exercises completed
- **Weekly Goals**: Complete 1 course module, maintain 7-day streak
- **Monthly Goals**: Finish specific course, earn 5 new achievements
- **Project Goals**: Build a complete application using learned skills

**Goal Tracking:**

Monitor progress with visual indicators:

- **Progress bars**: Show completion percentage
- **Milestone markers**: Celebrate intermediate achievements
- **Trend charts**: Visualize improvement over time
- **Streak counters**: Maintain motivation through consistency

Achievement System and Gamification
-----------------------------------

Understanding the XP System
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Experience Points (XP) are earned through various activities:

**XP Earning Activities:**

.. list-table:: XP Rewards
   :header-rows: 1
   :widths: 50 25 25

   * - Activity
     - Base XP
     - Bonus Conditions
   * - Complete Lesson
     - 50 XP
     - +25 for perfect quiz scores
   * - Solve Exercise
     - 100 XP
     - +50 for first attempt success
   * - Submit Project
     - 500 XP
     - +200 for exceptional quality
   * - Help Peer
     - 25 XP
     - +10 per helpful rating
   * - Daily Streak
     - 10 XP
     - Multiplier for longer streaks
   * - Course Completion
     - 1000 XP
     - +500 for high overall score

**Level Progression:**

XP translates to levels using this formula:

.. code-block:: python

   def calculate_level(total_xp):
       # Each level requires more XP than the last
       return int((total_xp / 100) ** 0.5) + 1
   
   # Examples:
   # Level 1: 0-99 XP
   # Level 2: 100-399 XP  
   # Level 3: 400-899 XP
   # Level 10: 8100+ XP

Achievement Categories
~~~~~~~~~~~~~~~~~~~~~

**Learning Achievements:**

- 🎯 **First Steps**: Complete your first lesson
- 📚 **Bookworm**: Read 50 lessons
- 💻 **Code Warrior**: Solve 100 exercises
- 🚀 **Speed Demon**: Complete lesson in under 10 minutes
- 🧠 **Perfect Score**: Get 100% on 10 exercises
- 🏆 **Course Master**: Complete any course with 95%+ average

**Consistency Achievements:**

- 🔥 **Streak Starter**: Maintain 3-day learning streak
- ⚡ **Lightning Week**: 7-day streak
- 🌟 **Dedication**: 30-day streak
- 💎 **Legendary**: 100-day streak
- 📅 **Early Bird**: Study before 8 AM for 5 days
- 🌙 **Night Owl**: Study after 10 PM for 5 days

**Mastery Achievements:**

- 🥇 **Python Fundamentals Expert**: Master basic concepts
- 🏅 **Algorithm Ace**: Excel at problem-solving
- 🎖️ **Data Structures Guru**: Master complex data types
- 👑 **OOP Champion**: Excel at object-oriented programming
- 🧪 **Testing Specialist**: Write comprehensive tests
- 🔧 **Debugging Detective**: Find and fix complex bugs

**Social Achievements:**

- 🤝 **Helper**: Assist 10 fellow learners
- 👥 **Collaborator**: Complete group project
- 💬 **Community**: Active in discussions for 30 days
- ⭐ **Mentor**: Receive 50+ helpful ratings
- 🎉 **Party Starter**: Create popular study group
- 🏆 **Leader**: Top 10 on monthly leaderboard

Maximizing Your Achievement Progress
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Strategic Learning:**

- **Focus on weak areas**: Target skills needing improvement
- **Consistent practice**: Maintain daily learning streaks
- **Quality over quantity**: Aim for understanding, not just completion
- **Help others**: Contribute to community discussions
- **Challenge yourself**: Attempt exercises above your current level

**Community Engagement:**

- **Join study groups**: Learn collaboratively with peers
- **Share knowledge**: Answer questions in forums
- **Provide feedback**: Review others' code and projects
- **Participate in challenges**: Join coding competitions and events

Community Features
------------------

Discussion Forums
~~~~~~~~~~~~~~~~

Engage with fellow learners through topic-based forums:

**Forum Categories:**

- **General Discussion**: Platform feedback and general Python topics
- **Course-Specific**: Dedicated spaces for each course
- **Project Showcase**: Share your completed projects
- **Help & Support**: Get assistance with technical issues
- **Career Advice**: Professional development discussions

**Best Practices:**

- **Search first**: Check if your question has been answered
- **Be specific**: Provide context and code examples
- **Help others**: Answer questions within your expertise
- **Stay respectful**: Maintain a positive learning environment

Study Groups
~~~~~~~~~~~~

Form or join study groups for collaborative learning:

**Group Types:**

- **Course-based**: Work through specific courses together
- **Skill-focused**: Target particular Python concepts
- **Project teams**: Build applications collaboratively
- **Accountability**: Regular check-ins and progress sharing

**Creating Effective Groups:**

- **Set clear goals**: Define what you want to achieve
- **Establish schedule**: Regular meeting times and formats
- **Assign roles**: Designate facilitators and note-takers
- **Use collaboration tools**: Shared documents and code repositories

Peer Code Review
~~~~~~~~~~~~~~~

Get feedback on your code from experienced developers:

**Review Process:**

1. **Submit code**: Share your solution with context
2. **Receive feedback**: Get constructive criticism and suggestions
3. **Iterate**: Improve based on recommendations
4. **Review others**: Provide feedback to build your skills

**Review Guidelines:**

- **Focus on clarity**: Is the code easy to understand?
- **Check efficiency**: Are there more optimal approaches?
- **Verify correctness**: Does the solution work for all cases?
- **Suggest improvements**: Offer specific, actionable advice

Customization and Settings
--------------------------

Personalizing Your Learning Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Theme and Appearance:**

- **Dark/Light Mode**: Choose your preferred color scheme
- **Font Settings**: Adjust size and family for comfort
- **Code Highlighting**: Customize syntax color schemes
- **Layout Options**: Arrange panels to suit your workflow

**Learning Preferences:**

- **Difficulty Progression**: Set preferred challenge levels
- **Hint Settings**: Configure when and how hints appear
- **Notification Preferences**: Control reminders and updates
- **Privacy Settings**: Manage profile visibility and data sharing

**Accessibility Features:**

- **Screen Reader Support**: Full compatibility with assistive technologies
- **Keyboard Navigation**: Complete platform access without mouse
- **High Contrast Mode**: Enhanced visibility for visual impairments
- **Text Scaling**: Adjustable font sizes for better readability

Integration and Export Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**External Tool Integration:**

- **GitHub**: Sync projects and submissions
- **IDE Integration**: Export code to your preferred development environment
- **Calendar Sync**: Add study sessions to your calendar
- **Progress Tracking**: Export analytics data

**Data Export:**

- **Certificate Generation**: Official completion certificates
- **Portfolio Export**: Showcase projects and achievements
- **Progress Reports**: Detailed learning analytics
- **Code Archives**: Download all your solutions and projects

Troubleshooting Common Issues
----------------------------

Technical Issues
~~~~~~~~~~~~~~~

**Code Editor Problems:**

- **Editor not loading**: Clear browser cache and refresh
- **Syntax highlighting broken**: Try switching themes
- **Auto-completion not working**: Check JavaScript is enabled
- **Files not saving**: Verify stable internet connection

**Performance Issues:**

- **Slow loading**: Check internet speed and browser performance
- **Memory errors**: Close unnecessary browser tabs
- **Timeout errors**: Optimize code efficiency
- **Display problems**: Update browser to latest version

**Account and Progress:**

- **Login issues**: Reset password or contact support
- **Missing progress**: Check sync status and refresh page
- **Achievement not unlocking**: Verify completion requirements
- **Course access problems**: Confirm enrollment status

Getting Help and Support
~~~~~~~~~~~~~~~~~~~~~~~~

**Self-Service Resources:**

- **FAQ Section**: Common questions and answers
- **Video Tutorials**: Step-by-step guidance
- **Documentation**: Comprehensive platform guide
- **Community Forums**: Peer support and discussions

**Contacting Support:**

- **Help Desk**: Submit tickets for technical issues
- **Live Chat**: Real-time assistance during business hours
- **Email Support**: Detailed issue reporting
- **Feature Requests**: Suggest platform improvements

Next Steps
----------

Congratulations! You now have a comprehensive understanding of Python Mastery Hub's features. 

**Recommended Next Actions:**

1. **Explore Advanced Features**: Check out the :doc:`advanced_features` guide
2. **Join the Community**: Participate in forums and study groups
3. **Set Learning Goals**: Create SMART goals for your Python journey
4. **Start a Project**: Apply your skills to real-world applications
5. **Share Your Progress**: Connect with other learners and mentors

**Additional Resources:**

- :doc:`getting_started` - Platform setup and first steps
- :doc:`advanced_features` - Power user tips and tricks
- :doc:`api_reference` - Technical documentation
- :doc:`troubleshooting` - Common issues and solutions

Remember, learning Python is a journey. Take advantage of all the tools and community support available to make your experience both effective and enjoyable!