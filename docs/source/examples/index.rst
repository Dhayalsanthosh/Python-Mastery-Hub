.. File: docs/source/examples/index.rst

Examples
========

This section provides practical examples and code snippets to help you get the most 
out of Python Mastery Hub. Whether you're using the CLI, integrating with the API, 
or building web applications, these examples will accelerate your development process.

.. note::
   **Copy and Adapt**: All examples are designed to be copied and adapted for your 
   specific use cases. Don't forget to replace placeholder values with your actual 
   configuration.

Overview
--------

Our examples are organized into three main categories:

.. grid:: 3
   :gutter: 3

   .. grid-item-card:: 🖥️ CLI Examples
      :link: cli_examples
      :link-type: doc

      Command-line automation scripts, bulk operations, and administrative tasks.

   .. grid-item-card:: 🌐 Web Examples
      :link: web_examples  
      :link-type: doc

      Frontend integrations, custom dashboards, and user interface enhancements.

   .. grid-item-card:: 🔌 API Examples
      :link: api_examples
      :link-type: doc

      RESTful API usage, webhook handlers, and third-party integrations.

Getting Started with Examples
-----------------------------

Quick Setup
~~~~~~~~~~~

Before running the examples, ensure you have:

1. **Python Mastery Hub installed** and configured
2. **API credentials** (for API examples)
3. **Development environment** set up
4. **Required dependencies** installed

.. code-block:: bash

   # Install example dependencies
   pip install requests python-dotenv pandas matplotlib
   
   # Set up environment variables
   echo "PMH_API_KEY=your_api_key_here" > .env
   echo "PMH_BASE_URL=https://api.pythonmasteryhub.com/v1" >> .env

Example Categories
-----------------

Command Line Interface (CLI)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Perfect for automation, batch operations, and administrative tasks:

- **User Management**: Bulk user creation, role assignments, account maintenance
- **Content Management**: Course imports, exercise validation, content publishing
- **System Administration**: Database operations, monitoring, backup automation
- **Analytics**: Report generation, data exports, performance analysis

**Skill Level**: Beginner to Advanced
**Use Cases**: DevOps, System Administration, Content Creation

Web Integration
~~~~~~~~~~~~~~

Frontend examples for custom user interfaces and integrations:

- **Custom Dashboards**: Student progress tracking, instructor analytics
- **Embedded Learning**: Integrate PMH content into existing websites
- **User Experience**: Custom themes, enhanced navigation, mobile optimization
- **Third-party Integrations**: LMS connectivity, SSO implementations

**Skill Level**: Intermediate to Advanced  
**Use Cases**: Web Development, UI/UX Enhancement, Platform Integration

API Development
~~~~~~~~~~~~~~

Backend integration examples for building custom applications:

- **Data Integration**: Syncing with external systems, automated workflows
- **Custom Applications**: Mobile apps, desktop tools, browser extensions
- **Webhook Processing**: Real-time notifications, automated responses
- **Analytics and Reporting**: Custom metrics, business intelligence

**Skill Level**: Intermediate to Advanced
**Use Cases**: Software Development, System Integration, Custom Tools

Example Structure
----------------

Each example includes:

📝 **Description**: What the example does and when to use it
🎯 **Use Case**: Real-world scenarios where this applies  
⚙️ **Prerequisites**: Required setup and dependencies
💻 **Complete Code**: Full, working implementation
🔧 **Configuration**: Environment and setup instructions
📊 **Sample Output**: Expected results and data formats
🔄 **Variations**: Alternative approaches and customizations
🐛 **Troubleshooting**: Common issues and solutions

Interactive Examples
--------------------

Try Before You Code
~~~~~~~~~~~~~~~~~~~

Many examples include interactive components:

.. raw:: html

   <div class="example-showcase">
       <div class="example-item">
           <h3>🎮 Live API Explorer</h3>
           <p>Test API endpoints with real data in our interactive playground.</p>
           <a href="https://api-explorer.pythonmasteryhub.com" target="_blank" class="btn-example">Try API Explorer →</a>
       </div>
       
       <div class="example-item">
           <h3>📊 Dashboard Demo</h3>
           <p>Explore a fully functional analytics dashboard built with our API.</p>
           <a href="https://demo-dashboard.pythonmasteryhub.com" target="_blank" class="btn-example">View Demo →</a>
       </div>
       
       <div class="example-item">
           <h3>🔧 Code Generator</h3>
           <p>Generate custom integration code based on your requirements.</p>
           <a href="https://code-generator.pythonmasteryhub.com" target="_blank" class="btn-example">Generate Code →</a>
       </div>
   </div>

Code Playground
~~~~~~~~~~~~~~

Test code snippets directly in your browser:

.. code-block:: python

   # Example: Get user progress data
   import requests
   
   def get_user_progress(api_key, user_id):
       """Fetch comprehensive user progress data."""
       
       headers = {
           'Authorization': f'Bearer {api_key}',
           'Content-Type': 'application/json'
       }
       
       response = requests.get(
           f'https://api.pythonmasteryhub.com/v1/users/{user_id}/progress',
           headers=headers
       )
       
       if response.status_code == 200:
           return response.json()
       else:
           raise Exception(f"API Error: {response.status_code}")
   
   # Try it yourself:
   # progress = get_user_progress('your_api_key', 'user_id')
   # print(f"User has completed {progress['courses_completed']} courses")

.. raw:: html

   <div class="code-playground">
       <button onclick="runExample()" class="btn-run">▶️ Run Example</button>
       <div id="output" class="output-area"></div>
   </div>

Featured Examples
----------------

Popular and Highly Requested
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**1. Automated Course Progress Reports**

Generate weekly progress reports for all students:

.. code-block:: bash

   # Generate comprehensive progress report
   pmh reports generate weekly-progress \
     --format pdf \
     --email-to instructors@school.edu \
     --include-charts \
     --filter "enrollment_date >= '2024-01-01'"

**2. Custom Learning Dashboard**

Build a real-time learning dashboard with charts and metrics:

.. code-block:: javascript

   // React component for live progress tracking
   function ProgressDashboard({ userId }) {
     const [progress, setProgress] = useState(null);
     
     useEffect(() => {
       const fetchProgress = async () => {
         const response = await fetch(`/api/users/${userId}/progress`);
         const data = await response.json();
         setProgress(data);
       };
       
       fetchProgress();
       const interval = setInterval(fetchProgress, 30000); // Update every 30s
       
       return () => clearInterval(interval);
     }, [userId]);
     
     return (
       <div className="dashboard">
         <ProgressChart data={progress?.courses} />
         <AchievementsList achievements={progress?.achievements} />
         <StreakCounter streak={progress?.current_streak} />
       </div>
     );
   }

**3. Bulk User Management**

Import students from CSV and enroll them in courses:

.. code-block:: python

   import csv
   import requests
   
   def bulk_enroll_students(csv_file, course_ids, api_key):
       """Enroll students from CSV file into specified courses."""
       
       with open(csv_file, 'r') as f:
           reader = csv.DictReader(f)
           
           for row in reader:
               # Create user account
               user_data = {
                   'username': row['student_id'],
                   'email': row['email'],
                   'first_name': row['first_name'],
                   'last_name': row['last_name']
               }
               
               user_response = create_user(user_data, api_key)
               user_id = user_response['id']
               
               # Enroll in courses
               for course_id in course_ids:
                   enroll_user(user_id, course_id, api_key)

**4. Real-time Notifications**

Set up webhook handlers for instant notifications:

.. code-block:: python

   from flask import Flask, request, jsonify
   import smtplib
   from email.mime.text import MIMEText
   
   app = Flask(__name__)
   
   @app.route('/webhooks/achievement-unlocked', methods=['POST'])
   def handle_achievement(data):
       """Send congratulations email when user earns achievement."""
       
       user_email = data['user']['email']
       achievement_name = data['achievement']['name']
       
       send_congratulations_email(user_email, achievement_name)
       
       return jsonify({'status': 'processed'})

Community Examples
-----------------

User-Contributed Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~

Examples shared by the Python Mastery Hub community:

**Mobile App Integration**
   React Native app connecting to PMH API for mobile learning

**Discord Bot**
   Automated bot for study group coordination and progress sharing

**Grade Sync Tool**
   Synchronize PMH progress with university learning management systems

**Analytics Dashboard**
   Custom Grafana dashboard for detailed learning analytics

**Slack Integration**
   Daily progress summaries and achievement notifications in Slack

.. admonition:: Contribute Your Examples
   :class: tip

   Have a useful example to share? Submit it to our community examples repository 
   on GitHub. Great examples may be featured in the official documentation!

Example Collections
------------------

Starter Templates
~~~~~~~~~~~~~~~~

Ready-to-use templates for common scenarios:

.. list-table:: Template Collection
   :header-rows: 1
   :widths: 30 40 30

   * - Template
     - Description
     - Difficulty
   * - Student Dashboard
     - React.js dashboard for progress tracking
     - Intermediate
   * - Course Analytics
     - Python script for instructor insights
     - Beginner
   * - Mobile App Starter
     - React Native app template
     - Advanced
   * - Webhook Server
     - Express.js webhook handler
     - Intermediate
   * - CLI Automation
     - Bash scripts for common tasks
     - Beginner
   * - LMS Integration
     - Canvas/Moodle sync tools
     - Advanced

Advanced Patterns
~~~~~~~~~~~~~~~~

Complex integration patterns for experienced developers:

- **Microservices Architecture**: Break down PMH integration into microservices
- **Event-Driven Design**: Build reactive systems with webhook events
- **Caching Strategies**: Optimize performance with Redis and CDN integration
- **Security Patterns**: Implement OAuth2, rate limiting, and data encryption
- **Scalability Patterns**: Handle high-volume API usage and concurrent users

Testing Examples
---------------

Example Test Suites
~~~~~~~~~~~~~~~~~~

Learn how to test your PMH integrations:

.. code-block:: python

   import unittest
   from unittest.mock import patch, Mock
   import requests
   
   class TestPMHIntegration(unittest.TestCase):
       
       def setUp(self):
           self.api_key = 'test_api_key'
           self.base_url = 'https://api.pythonmasteryhub.com/v1'
       
       @patch('requests.get')
       def test_get_user_progress(self, mock_get):
           # Mock API response
           mock_response = Mock()
           mock_response.status_code = 200
           mock_response.json.return_value = {
               'courses_completed': 5,
               'total_xp': 2500
           }
           mock_get.return_value = mock_response
           
           # Test the function
           progress = get_user_progress(self.api_key, 'user123')
           
           self.assertEqual(progress['courses_completed'], 5)
           self.assertEqual(progress['total_xp'], 2500)

Performance Testing
~~~~~~~~~~~~~~~~~~

Examples for load testing and performance optimization:

.. code-block:: python

   import asyncio
   import aiohttp
   import time
   
   async def load_test_api():
       """Simulate concurrent API requests."""
       
       async def make_request(session, user_id):
           async with session.get(f'/api/users/{user_id}/progress') as response:
               return await response.json()
       
       async with aiohttp.ClientSession() as session:
           tasks = []
           for i in range(100):  # 100 concurrent requests
               task = make_request(session, f'user_{i}')
               tasks.append(task)
           
           start_time = time.time()
           results = await asyncio.gather(*tasks)
           end_time = time.time()
           
           print(f"Completed 100 requests in {end_time - start_time:.2f} seconds")

Getting Help with Examples
--------------------------

Documentation and Support
~~~~~~~~~~~~~~~~~~~~~~~~~

**Example-Specific Help:**
- Each example includes troubleshooting section
- Common issues and solutions documented
- Video walkthroughs for complex examples

**Community Support:**
- **Discord**: #examples channel for real-time help
- **GitHub**: Issues and discussions for specific examples
- **Forums**: Community Q&A and example sharing

**Professional Support:**
- **Consulting**: Custom example development
- **Training**: Workshop sessions on integration patterns
- **Code Review**: Professional review of your implementations

Contributing Examples
---------------------

Share Your Solutions
~~~~~~~~~~~~~~~~~~~

Help grow the example collection:

1. **Fork the examples repository** on GitHub
2. **Create a new example** following our template
3. **Include comprehensive documentation** and tests
4. **Submit a pull request** for review
5. **Engage with community feedback** during review

**Example Contribution Guidelines:**

- **Clear documentation**: Explain what, why, and how
- **Working code**: Test thoroughly before submission
- **Error handling**: Include proper error handling and validation
- **Best practices**: Follow coding standards and security guidelines
- **Licensing**: Ensure compatibility with MIT license

.. toctree::
   :maxdepth: 2

   cli_examples
   web_examples
   api_examples

What's Next?
-----------

Ready to explore specific examples?

👉 **Start with**: :doc:`cli_examples` for automation and scripting
🌐 **For web development**: :doc:`web_examples` for frontend integration
🔌 **For API work**: :doc:`api_examples` for backend development

.. admonition:: Learn by Doing! 💡
   :class: tip

   The best way to learn is by trying these examples yourself. Start with 
   simpler examples and gradually work your way up to more complex integrations. 
   Don't hesitate to modify and experiment with the code to fit your needs!