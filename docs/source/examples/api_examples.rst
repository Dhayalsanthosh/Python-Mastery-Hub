.. File: docs/source/examples/api_examples.rst

API Examples
============

These examples demonstrate how to integrate with the Python Mastery Hub REST API 
for building custom applications, automating workflows, and creating powerful 
integrations with external systems.

.. note::
   **Prerequisites**: Basic understanding of REST APIs, HTTP methods, and JSON. 
   Familiarity with your chosen programming language and API client libraries.

Quick Setup
-----------

Before running the examples, set up your API credentials:

.. code-block:: bash

   # Environment variables
   export PMH_API_KEY="your_api_key_here"
   export PMH_BASE_URL="https://api.pythonmasteryhub.com/v1"

.. code-block:: python

   # Python setup
   import os
   import requests
   from datetime import datetime
   
   API_KEY = os.getenv('PMH_API_KEY')
   BASE_URL = os.getenv('PMH_BASE_URL', 'https://api.pythonmasteryhub.com/v1')
   
   headers = {
       'Authorization': f'Bearer {API_KEY}',
       'Content-Type': 'application/json'
   }

Python API Client Examples
--------------------------

Complete API Client Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Create a comprehensive Python client for all API operations with error handling and rate limiting.

.. code-block:: python

   # File: pmh_client.py
   import requests
   import time
   import json
   from typing import Optional, Dict, List, Any
   from datetime import datetime, timedelta
   import logging

   logger = logging.getLogger(__name__)

   class PMHAPIError(Exception):
       """Custom exception for PMH API errors."""
       def __init__(self, message: str, status_code: int = None, response_data: dict = None):
           super().__init__(message)
           self.status_code = status_code
           self.response_data = response_data

   class RateLimiter:
       """Simple rate limiter to respect API limits."""
       def __init__(self, max_requests: int = 100, time_window: int = 3600):
           self.max_requests = max_requests
           self.time_window = time_window
           self.requests = []
       
       def wait_if_needed(self):
           now = time.time()
           # Remove old requests outside the time window
           self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
           
           if len(self.requests) >= self.max_requests:
               # Calculate wait time
               oldest_request = min(self.requests)
               wait_time = self.time_window - (now - oldest_request)
               if wait_time > 0:
                   logger.info(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
                   time.sleep(wait_time)
           
           self.requests.append(now)

   class PMHClient:
       """Python Mastery Hub API Client."""
       
       def __init__(self, api_key: str, base_url: str = "https://api.pythonmasteryhub.com/v1"):
           self.api_key = api_key
           self.base_url = base_url.rstrip('/')
           self.session = requests.Session()
           self.session.headers.update({
               'Authorization': f'Bearer {api_key}',
               'Content-Type': 'application/json',
               'User-Agent': 'PMH-Python-Client/1.0'
           })
           self.rate_limiter = RateLimiter()
       
       def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
           """Make HTTP request with rate limiting and error handling."""
           self.rate_limiter.wait_if_needed()
           
           url = f"{self.base_url}{endpoint}"
           
           try:
               response = self.session.request(method, url, **kwargs)
               
               # Log rate limit headers
               if 'X-RateLimit-Remaining' in response.headers:
                   remaining = response.headers.get('X-RateLimit-Remaining')
                   logger.debug(f"Rate limit remaining: {remaining}")
               
               response.raise_for_status()
               
               # Handle empty responses
               if response.status_code == 204 or not response.content:
                   return {}
               
               return response.json()
               
           except requests.exceptions.HTTPError as e:
               error_data = {}
               try:
                   error_data = response.json()
               except:
                   pass
               
               error_message = error_data.get('error', {}).get('message', str(e))
               raise PMHAPIError(error_message, response.status_code, error_data)
           
           except requests.exceptions.RequestException as e:
               raise PMHAPIError(f"Network error: {str(e)}")
       
       def get(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
           """Make GET request."""
           return self._make_request('GET', endpoint, params=params)
       
       def post(self, endpoint: str, data: Dict = None) -> Dict[str, Any]:
           """Make POST request."""
           return self._make_request('POST', endpoint, json=data)
       
       def put(self, endpoint: str, data: Dict = None) -> Dict[str, Any]:
           """Make PUT request."""
           return self._make_request('PUT', endpoint, json=data)
       
       def delete(self, endpoint: str) -> Dict[str, Any]:
           """Make DELETE request."""
           return self._make_request('DELETE', endpoint)
       
       # User Management
       def get_user(self, user_id: str) -> Dict[str, Any]:
           """Get user information."""
           return self.get(f'/users/{user_id}')
       
       def get_current_user(self) -> Dict[str, Any]:
           """Get current authenticated user."""
           return self.get('/users/me')
       
       def update_user(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
           """Update user information."""
           return self.put(f'/users/{user_id}', data)
       
       def get_user_progress(self, user_id: str) -> Dict[str, Any]:
           """Get user's learning progress."""
           return self.get(f'/users/{user_id}/progress')
       
       def get_user_achievements(self, user_id: str, recent_only: bool = False) -> Dict[str, Any]:
           """Get user's achievements."""
           endpoint = f'/users/{user_id}/achievements'
           if recent_only:
               endpoint += '/recent'
           return self.get(endpoint)
       
       # Course Management
       def list_courses(self, difficulty: str = None, category: str = None, 
                       search: str = None, limit: int = 20, cursor: str = None) -> Dict[str, Any]:
           """List available courses with filtering."""
           params = {'limit': limit}
           if difficulty:
               params['difficulty'] = difficulty
           if category:
               params['category'] = category
           if search:
               params['search'] = search
           if cursor:
               params['cursor'] = cursor
           
           return self.get('/courses', params)
       
       def get_course(self, course_id: str) -> Dict[str, Any]:
           """Get course details."""
           return self.get(f'/courses/{course_id}')
       
       def enroll_in_course(self, course_id: str, user_id: str = None) -> Dict[str, Any]:
           """Enroll user in course."""
           data = {}
           if user_id:
               data['user_id'] = user_id
           return self.post(f'/courses/{course_id}/enroll', data)
       
       def get_course_progress(self, course_id: str, user_id: str = None) -> Dict[str, Any]:
           """Get course progress for user."""
           endpoint = f'/courses/{course_id}/progress'
           if user_id:
               endpoint += f'?user_id={user_id}'
           return self.get(endpoint)
       
       # Exercise Management
       def get_exercise(self, exercise_id: str) -> Dict[str, Any]:
           """Get exercise details."""
           return self.get(f'/exercises/{exercise_id}')
       
       def submit_exercise(self, exercise_id: str, code: str, attempt_number: int = 1) -> Dict[str, Any]:
           """Submit exercise solution."""
           data = {
               'code': code,
               'attempt_number': attempt_number
           }
           return self.post(f'/exercises/{exercise_id}/submit', data)
       
       def get_exercise_submissions(self, exercise_id: str, user_id: str = None) -> Dict[str, Any]:
           """Get exercise submission history."""
           params = {}
           if user_id:
               params['user_id'] = user_id
           return self.get(f'/exercises/{exercise_id}/submissions', params)
       
       # Analytics
       def get_analytics_overview(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
           """Get analytics overview."""
           params = {}
           if start_date:
               params['start_date'] = start_date
           if end_date:
               params['end_date'] = end_date
           return self.get('/analytics/overview', params)
       
       def get_user_analytics(self, user_id: str, period: str = '30days') -> Dict[str, Any]:
           """Get detailed user analytics."""
           params = {'period': period}
           return self.get(f'/users/{user_id}/analytics', params)
       
       # Batch Operations
       def batch_enroll_users(self, course_id: str, user_ids: List[str]) -> Dict[str, Any]:
           """Enroll multiple users in a course."""
           data = {
               'user_ids': user_ids,
               'course_id': course_id
           }
           return self.post('/admin/batch/enroll', data)
       
       def bulk_create_users(self, users_data: List[Dict[str, Any]]) -> Dict[str, Any]:
           """Create multiple users at once."""
           data = {'users': users_data}
           return self.post('/admin/users/bulk', data)
       
       # Utility Methods
       def paginate_all(self, endpoint: str, params: Dict = None, limit: int = 100) -> List[Dict[str, Any]]:
           """Fetch all items from a paginated endpoint."""
           all_items = []
           cursor = None
           
           if params is None:
               params = {}
           
           params['limit'] = limit
           
           while True:
               if cursor:
                   params['cursor'] = cursor
               
               response = self.get(endpoint, params)
               data = response.get('data', response)
               
               # Handle different response structures
               if isinstance(data, dict):
                   items = data.get('items', data.get('courses', data.get('users', [])))
                   pagination = data.get('pagination', {})
               else:
                   items = data
                   pagination = {}
               
               all_items.extend(items)
               
               if not pagination.get('has_more', False):
                   break
               
               cursor = pagination.get('next_cursor')
               if not cursor:
                   break
           
           return all_items

   # Usage Examples
   if __name__ == "__main__":
       import os
       
       # Initialize client
       client = PMHClient(os.getenv('PMH_API_KEY'))
       
       try:
           # Get current user
           user = client.get_current_user()
           print(f"Logged in as: {user['data']['username']}")
           
           # List all courses
           courses = client.list_courses(limit=10)
           print(f"Found {len(courses['data']['courses'])} courses")
           
           # Get user progress
           progress = client.get_user_progress(user['data']['id'])
           print(f"Total XP: {progress['data']['total_xp']}")
           
       except PMHAPIError as e:
           print(f"API Error: {e}")
           if e.status_code:
               print(f"Status Code: {e.status_code}")

Advanced Integration Examples
----------------------------

Automated Progress Reporting System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Create an automated system that generates and emails weekly progress reports for students and instructors.

.. code-block:: python

   # File: progress_reporter.py
   import smtplib
   import schedule
   import time
   from email.mime.text import MIMEText
   from email.mime.multipart import MIMEMultipart
   from email.mime.application import MIMEApplication
   import pandas as pd
   import matplotlib.pyplot as plt
   from datetime import datetime, timedelta
   import os
   import logging
   from pmh_client import PMHClient, PMHAPIError

   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)

   class ProgressReporter:
       """Automated progress reporting system."""
       
       def __init__(self, api_key: str, smtp_config: dict):
           self.client = PMHClient(api_key)
           self.smtp_config = smtp_config
           
       def generate_student_report(self, user_id: str, weeks: int = 1) -> dict:
           """Generate comprehensive progress report for a student."""
           try:
               # Get student information
               user = self.client.get_user(user_id)
               progress = self.client.get_user_progress(user_id)
               analytics = self.client.get_user_analytics(user_id, f'{weeks * 7}days')
               achievements = self.client.get_user_achievements(user_id, recent_only=True)
               
               # Calculate weekly statistics
               end_date = datetime.now()
               start_date = end_date - timedelta(weeks=weeks)
               
               report_data = {
                   'user': user['data'],
                   'progress': progress['data'],
                   'analytics': analytics['data'],
                   'achievements': achievements['data'],
                   'period': {
                       'start_date': start_date.isoformat(),
                       'end_date': end_date.isoformat(),
                       'weeks': weeks
                   }
               }
               
               return report_data
               
           except PMHAPIError as e:
               logger.error(f"Failed to generate report for user {user_id}: {e}")
               raise
       
       def generate_instructor_report(self, instructor_id: str, weeks: int = 1) -> dict:
           """Generate comprehensive report for an instructor."""
           try:
               # Get instructor's courses
               courses_response = self.client.get(f'/instructors/{instructor_id}/courses')
               courses = courses_response['data']['courses']
               
               instructor_data = {
                   'courses': [],
                   'total_students': 0,
                   'total_completions': 0,
                   'avg_progress': 0
               }
               
               for course in courses:
                   course_analytics = self.client.get(f'/courses/{course["id"]}/analytics')
                   course_students = self.client.get(f'/courses/{course["id"]}/students')
                   
                   course_data = {
                       'course': course,
                       'analytics': course_analytics['data'],
                       'students': course_students['data'],
                       'student_count': len(course_students['data']['students']),
                       'completion_rate': course_analytics['data'].get('completion_rate', 0)
                   }
                   
                   instructor_data['courses'].append(course_data)
                   instructor_data['total_students'] += course_data['student_count']
               
               # Calculate averages
               if instructor_data['courses']:
                   instructor_data['avg_progress'] = sum(
                       c['completion_rate'] for c in instructor_data['courses']
                   ) / len(instructor_data['courses'])
               
               return instructor_data
               
           except PMHAPIError as e:
               logger.error(f"Failed to generate instructor report for {instructor_id}: {e}")
               raise
       
       def create_progress_chart(self, analytics_data: dict, output_path: str) -> str:
           """Create progress visualization chart."""
           try:
               # Extract data for visualization
               daily_data = analytics_data.get('daily_progress', [])
               
               if not daily_data:
                   return None
               
               dates = [item['date'] for item in daily_data]
               xp_earned = [item['xp_earned'] for item in daily_data]
               time_spent = [item['time_spent_minutes'] / 60 for item in daily_data]  # Convert to hours
               
               # Create figure with subplots
               fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
               
               # XP Progress Chart
               ax1.plot(dates, xp_earned, marker='o', linewidth=2, color='#2ecc71')
               ax1.set_title('Daily XP Progress', fontsize=14, fontweight='bold')
               ax1.set_ylabel('XP Earned')
               ax1.grid(True, alpha=0.3)
               ax1.tick_params(axis='x', rotation=45)
               
               # Time Spent Chart
               ax2.bar(dates, time_spent, color='#3498db', alpha=0.7)
               ax2.set_title('Daily Study Time', fontsize=14, fontweight='bold')
               ax2.set_ylabel('Hours')
               ax2.set_xlabel('Date')
               ax2.grid(True, alpha=0.3)
               ax2.tick_params(axis='x', rotation=45)
               
               plt.tight_layout()
               plt.savefig(output_path, dpi=300, bbox_inches='tight')
               plt.close()
               
               return output_path
               
           except Exception as e:
               logger.error(f"Failed to create progress chart: {e}")
               return None
       
       def generate_html_report(self, report_data: dict, report_type: str = 'student') -> str:
           """Generate HTML report from data."""
           if report_type == 'student':
               return self._generate_student_html(report_data)
           else:
               return self._generate_instructor_html(report_data)
       
       def _generate_student_html(self, data: dict) -> str:
           """Generate HTML report for student."""
           user = data['user']
           progress = data['progress']
           analytics = data['analytics']
           achievements = data['achievements']
           
           html = f"""
           <!DOCTYPE html>
           <html>
           <head>
               <title>Weekly Progress Report - {user['first_name']} {user['last_name']}</title>
               <style>
                   body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
                   .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                   .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                   .stat {{ text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
                   .stat-value {{ font-size: 2em; font-weight: bold; color: #2ecc71; }}
                   .stat-label {{ font-size: 0.9em; color: #6c757d; }}
                   .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #3498db; 
                            background: #f8f9fa; }}
                   .achievement {{ display: inline-block; margin: 5px; padding: 8px 12px; 
                                 background: #fff3cd; border-radius: 15px; border: 1px solid #ffeaa7; }}
                   table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                   th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                   th {{ background-color: #f2f2f2; }}
               </style>
           </head>
           <body>
               <div class="header">
                   <h1>Weekly Progress Report</h1>
                   <h2>{user['first_name']} {user['last_name']}</h2>
                   <p>Report Period: {data['period']['start_date'][:10]} to {data['period']['end_date'][:10]}</p>
               </div>
               
               <div class="stats">
                   <div class="stat">
                       <div class="stat-value">{progress['total_xp']:,}</div>
                       <div class="stat-label">Total XP</div>
                   </div>
                   <div class="stat">
                       <div class="stat-value">{progress['current_level']}</div>
                       <div class="stat-label">Current Level</div>
                   </div>
                   <div class="stat">
                       <div class="stat-value">{progress['current_streak']}</div>
                       <div class="stat-label">Day Streak</div>
                   </div>
                   <div class="stat">
                       <div class="stat-value">{len(progress.get('courses', []))}</div>
                       <div class="stat-label">Active Courses</div>
                   </div>
               </div>
               
               <div class="section">
                   <h3>Course Progress</h3>
                   <table>
                       <tr>
                           <th>Course</th>
                           <th>Progress</th>
                           <th>Lessons Completed</th>
                           <th>Exercises Solved</th>
                       </tr>
           """
           
           for course in progress.get('courses', []):
               html += f"""
                       <tr>
                           <td>{course['title']}</td>
                           <td>{course['progress']:.1f}%</td>
                           <td>{course.get('lessons_completed', 0)}</td>
                           <td>{course.get('exercises_completed', 0)}</td>
                       </tr>
               """
           
           html += """
                   </table>
               </div>
           """
           
           if achievements.get('achievements'):
               html += """
               <div class="section">
                   <h3>Recent Achievements</h3>
               """
               for achievement in achievements['achievements']:
                   html += f"""
                   <div class="achievement">
                       {achievement.get('icon', '🏆')} {achievement['name']}
                   </div>
                   """
               html += """
               </div>
               """
           
           html += """
               <div class="section">
                   <h3>Weekly Summary</h3>
                   <ul>
                       <li><strong>Time Spent Learning:</strong> {:.1f} hours</li>
                       <li><strong>XP Earned This Week:</strong> {:,}</li>
                       <li><strong>Lessons Completed:</strong> {}</li>
                       <li><strong>Exercises Solved:</strong> {}</li>
                   </ul>
               </div>
               
               <div class="section">
                   <h3>Recommendations</h3>
                   <ul>
                       <li>Continue your excellent learning streak!</li>
                       <li>Try tackling more challenging exercises to boost your XP.</li>
                       <li>Join study groups to enhance collaborative learning.</li>
                   </ul>
               </div>
           </body>
           </html>
           """.format(
               analytics.get('total_time_hours', 0),
               analytics.get('weekly_xp', 0),
               analytics.get('weekly_lessons', 0),
               analytics.get('weekly_exercises', 0)
           )
           
           return html
       
       def _generate_instructor_html(self, data: dict) -> str:
           """Generate HTML report for instructor."""
           html = f"""
           <!DOCTYPE html>
           <html>
           <head>
               <title>Instructor Weekly Report</title>
               <style>
                   body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
                   .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                   .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                   .stat {{ text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
                   .stat-value {{ font-size: 2em; font-weight: bold; color: #e74c3c; }}
                   .course-card {{ margin: 15px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; }}
                   table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                   th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                   th {{ background-color: #f2f2f2; }}
               </style>
           </head>
           <body>
               <div class="header">
                   <h1>Instructor Weekly Report</h1>
                   <p>Report Period: Week of {datetime.now().strftime('%Y-%m-%d')}</p>
               </div>
               
               <div class="stats">
                   <div class="stat">
                       <div class="stat-value">{len(data['courses'])}</div>
                       <div class="stat-label">Active Courses</div>
                   </div>
                   <div class="stat">
                       <div class="stat-value">{data['total_students']}</div>
                       <div class="stat-label">Total Students</div>
                   </div>
                   <div class="stat">
                       <div class="stat-value">{data['avg_progress']:.1f}%</div>
                       <div class="stat-label">Avg Progress</div>
                   </div>
               </div>
               
               <h3>Course Details</h3>
           """
           
           for course_data in data['courses']:
               course = course_data['course']
               analytics = course_data['analytics']
               
               html += f"""
               <div class="course-card">
                   <h4>{course['title']}</h4>
                   <p><strong>Students:</strong> {course_data['student_count']}</p>
                   <p><strong>Completion Rate:</strong> {course_data['completion_rate']:.1f}%</p>
                   <p><strong>Average Score:</strong> {analytics.get('average_score', 0):.1f}%</p>
               </div>
               """
           
           html += """
           </body>
           </html>
           """
           
           return html
       
       def send_email_report(self, recipient_email: str, subject: str, 
                           html_content: str, attachments: list = None):
           """Send email report with optional attachments."""
           try:
               msg = MIMEMultipart('alternative')
               msg['Subject'] = subject
               msg['From'] = self.smtp_config['from_email']
               msg['To'] = recipient_email
               
               # Add HTML content
               html_part = MIMEText(html_content, 'html')
               msg.attach(html_part)
               
               # Add attachments
               if attachments:
                   for attachment_path in attachments:
                       if os.path.exists(attachment_path):
                           with open(attachment_path, 'rb') as f:
                               attachment = MIMEApplication(f.read())
                               attachment.add_header(
                                   'Content-Disposition', 
                                   'attachment', 
                                   filename=os.path.basename(attachment_path)
                               )
                               msg.attach(attachment)
               
               # Send email
               with smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['smtp_port']) as server:
                   server.starttls()
                   server.login(self.smtp_config['username'], self.smtp_config['password'])
                   server.send_message(msg)
               
               logger.info(f"Report sent successfully to {recipient_email}")
               
           except Exception as e:
               logger.error(f"Failed to send email to {recipient_email}: {e}")
               raise
       
       def run_weekly_reports(self):
           """Generate and send weekly reports for all users."""
           try:
               # Get all students
               students = self.client.paginate_all('/admin/users', {'role': 'student'})
               
               # Get all instructors
               instructors = self.client.paginate_all('/admin/users', {'role': 'instructor'})
               
               # Generate student reports
               for student in students:
                   try:
                       report_data = self.generate_student_report(student['id'])
                       html_content = self.generate_html_report(report_data, 'student')
                       
                       # Create progress chart
                       chart_path = f"/tmp/progress_chart_{student['id']}.png"
                       chart_file = self.create_progress_chart(
                           report_data['analytics'], 
                           chart_path
                       )
                       
                       # Send email
                       subject = f"Weekly Progress Report - {student['first_name']} {student['last_name']}"
                       attachments = [chart_file] if chart_file else []
                       
                       self.send_email_report(
                           student['email'], 
                           subject, 
                           html_content, 
                           attachments
                       )
                       
                       # Clean up chart file
                       if chart_file and os.path.exists(chart_file):
                           os.remove(chart_file)
                           
                   except Exception as e:
                       logger.error(f"Failed to process student {student['id']}: {e}")
                       continue
               
               # Generate instructor reports
               for instructor in instructors:
                   try:
                       report_data = self.generate_instructor_report(instructor['id'])
                       html_content = self.generate_html_report(report_data, 'instructor')
                       
                       subject = f"Weekly Instructor Report - {instructor['first_name']} {instructor['last_name']}"
                       
                       self.send_email_report(
                           instructor['email'], 
                           subject, 
                           html_content
                       )
                       
                   except Exception as e:
                       logger.error(f"Failed to process instructor {instructor['id']}: {e}")
                       continue
               
               logger.info("Weekly reports generation completed")
               
           except Exception as e:
               logger.error(f"Failed to run weekly reports: {e}")
               raise

   # Scheduling and main execution
   def main():
       """Main function to set up and run the progress reporter."""
       
       # Configuration
       api_key = os.getenv('PMH_API_KEY')
       if not api_key:
           logger.error("PMH_API_KEY environment variable not set")
           return
       
       smtp_config = {
           'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
           'smtp_port': int(os.getenv('SMTP_PORT', '587')),
           'username': os.getenv('SMTP_USERNAME'),
           'password': os.getenv('SMTP_PASSWORD'),
           'from_email': os.getenv('FROM_EMAIL')
       }
       
       # Validate SMTP configuration
       required_smtp_vars = ['username', 'password', 'from_email']
       if not all(smtp_config[var] for var in required_smtp_vars):
           logger.error("Missing required SMTP configuration variables")
           return
       
       # Initialize reporter
       reporter = ProgressReporter(api_key, smtp_config)
       
       # Schedule weekly reports (every Monday at 9 AM)
       schedule.every().monday.at("09:00").do(reporter.run_weekly_reports)
       
       # For testing, you can also run immediately
       # reporter.run_weekly_reports()
       
       logger.info("Progress reporter started. Waiting for scheduled runs...")
       
       # Keep the script running
       while True:
           schedule.run_pending()
           time.sleep(60)  # Check every minute

   if __name__ == "__main__":
       main()

Webhook Handler Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Create a robust webhook handler to process real-time events from Python Mastery Hub.

.. code-block:: python

   # File: webhook_handler.py
   from flask import Flask, request, jsonify
   import hmac
   import hashlib
   import json
   import logging
   from datetime import datetime
   import sqlite3
   import os
   from typing import Dict, Any

   app = Flask(__name__)
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)

   # Configuration
   WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your-webhook-secret')
   DATABASE_PATH = os.getenv('DATABASE_PATH', 'webhook_events.db')

   class WebhookProcessor:
       """Process and handle various webhook events."""
       
       def __init__(self, database_path: str):
           self.database_path = database_path
           self.init_database()
       
       def init_database(self):
           """Initialize SQLite database for event storage."""
           conn = sqlite3.connect(self.database_path)
           cursor = conn.cursor()
           
           cursor.execute('''
               CREATE TABLE IF NOT EXISTS webhook_events (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   event_id TEXT UNIQUE,
                   event_type TEXT NOT NULL,
                   user_id TEXT,
                   data TEXT,
                   processed BOOLEAN DEFAULT FALSE,
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                   processed_at TIMESTAMP
               )
           ''')
           
           cursor.execute('''
               CREATE TABLE IF NOT EXISTS notifications (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   event_id TEXT,
                   notification_type TEXT,
                   recipient TEXT,
                   message TEXT,
                   sent BOOLEAN DEFAULT FALSE,
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                   sent_at TIMESTAMP
               )
           ''')
           
           conn.commit()
           conn.close()
       
       def store_event(self, event_data: Dict[str, Any]) -> bool:
           """Store webhook event in database."""
           try:
               conn = sqlite3.connect(self.database_path)
               cursor = conn.cursor()
               
               cursor.execute('''
                   INSERT OR IGNORE INTO webhook_events 
                   (event_id, event_type, user_id, data)
                   VALUES (?, ?, ?, ?)
               ''', (
                   event_data.get('id'),
                   event_data.get('type'),
                   event_data.get('user_id'),
                   json.dumps(event_data)
               ))
               
               conn.commit()
               conn.close()
               return True
               
           except Exception as e:
               logger.error(f"Failed to store event: {e}")
               return False
       
       def process_achievement_unlocked(self, event_data: Dict[str, Any]):
           """Process achievement unlocked event."""
           try:
               user = event_data['user']
               achievement = event_data['achievement']
               
               # Send congratulations notification
               self.send_achievement_notification(user, achievement)
               
               # Update user's achievement count in external system
               self.update_external_user_stats(user['id'], 'achievements_count', 1)
               
               # Post to social media if it's a high-tier achievement
               if achievement.get('tier') in ['platinum', 'diamond']:
                   self.post_achievement_to_social(user, achievement)
               
               logger.info(f"Processed achievement unlock for user {user['id']}: {achievement['name']}")
               
           except Exception as e:
               logger.error(f"Failed to process achievement event: {e}")
       
       def process_course_completed(self, event_data: Dict[str, Any]):
           """Process course completion event."""
           try:
               user = event_data['user']
               course = event_data['course']
               completion_data = event_data['completion_data']
               
               # Send completion certificate
               self.generate_completion_certificate(user, course, completion_data)
               
               # Update external LMS
               self.sync_completion_to_lms(user['id'], course['id'], completion_data)
               
               # Send notification to instructor
               self.notify_instructor_of_completion(course['instructor_id'], user, course)
               
               # Recommend next courses
               self.recommend_next_courses(user['id'], course['category'])
               
               logger.info(f"Processed course completion for user {user['id']}: {course['title']}")
               
           except Exception as e:
               logger.error(f"Failed to process course completion event: {e}")
       
       def process_exercise_submitted(self, event_data: Dict[str, Any]):
           """Process exercise submission event."""
           try:
               user = event_data['user']
               exercise = event_data['exercise']
               submission = event_data['submission']
               
               # Check for plagiarism if score is high
               if submission['score'] > 90:
                   self.queue_plagiarism_check(submission['id'])
               
               # Update real-time leaderboards
               self.update_leaderboards(user['id'], submission['score'])
               
               # Send feedback notification if instructor feedback is available
               if submission.get('instructor_feedback'):
                   self.send_feedback_notification(user, exercise, submission)
               
               logger.info(f"Processed exercise submission for user {user['id']}: {exercise['title']}")
               
           except Exception as e:
               logger.error(f"Failed to process exercise submission event: {e}")
       
       def process_user_registered(self, event_data: Dict[str, Any]):
           """Process new user registration event."""
           try:
               user = event_data['user']
               
               # Send welcome email sequence
               self.start_welcome_email_sequence(user)
               
               # Create user profile in external systems
               self.create_external_user_profile(user)
               
               # Assign to default study group
               self.assign_to_study_group(user['id'])
               
               # Send notification to admins
               self.notify_admins_new_user(user)
               
               logger.info(f"Processed user registration: {user['email']}")
               
           except Exception as e:
               logger.error(f"Failed to process user registration event: {e}")
       
       def send_achievement_notification(self, user: Dict, achievement: Dict):
           """Send achievement notification via email/SMS."""
           message = f"🎉 Congratulations {user['first_name']}! You've earned the '{achievement['name']}' achievement!"
           
           self.queue_notification(
               user['email'], 
               'achievement', 
               f"Achievement Unlocked: {achievement['name']}", 
               message
           )
       
       def generate_completion_certificate(self, user: Dict, course: Dict, completion_data: Dict):
           """Generate and send course completion certificate."""
           # This would integrate with a certificate generation service
           logger.info(f"Generating certificate for {user['email']} - {course['title']}")
           
           # Queue certificate generation task
           self.queue_notification(
               user['email'],
               'certificate',
               f"Course Completion Certificate - {course['title']}",
               f"Congratulations on completing {course['title']}! Your certificate is attached."
           )
       
       def sync_completion_to_lms(self, user_id: str, course_id: str, completion_data: Dict):
           """Sync course completion to external LMS."""
           # This would integrate with external LMS APIs (Canvas, Moodle, etc.)
           logger.info(f"Syncing completion to external LMS: user {user_id}, course {course_id}")
       
       def update_external_user_stats(self, user_id: str, stat_type: str, increment: int):
           """Update user statistics in external systems."""
           # This would update external databases or APIs
           logger.info(f"Updating external stats for user {user_id}: {stat_type} +{increment}")
       
       def post_achievement_to_social(self, user: Dict, achievement: Dict):
           """Post achievement to social media (with user permission)."""
           # This would integrate with social media APIs
           logger.info(f"Posting achievement to social media: {user['username']} - {achievement['name']}")
       
       def queue_notification(self, recipient: str, notification_type: str, subject: str, message: str):
           """Queue notification for sending."""
           try:
               conn = sqlite3.connect(self.database_path)
               cursor = conn.cursor()
               
               cursor.execute('''
                   INSERT INTO notifications 
                   (notification_type, recipient, message)
                   VALUES (?, ?, ?)
               ''', (notification_type, recipient, json.dumps({
                   'subject': subject,
                   'message': message
               })))
               
               conn.commit()
               conn.close()
               
           except Exception as e:
               logger.error(f"Failed to queue notification: {e}")
       
       def mark_event_processed(self, event_id: str):
           """Mark event as processed in database."""
           try:
               conn = sqlite3.connect(self.database_path)
               cursor = conn.cursor()
               
               cursor.execute('''
                   UPDATE webhook_events 
                   SET processed = TRUE, processed_at = CURRENT_TIMESTAMP
                   WHERE event_id = ?
               ''', (event_id,))
               
               conn.commit()
               conn.close()
               
           except Exception as e:
               logger.error(f"Failed to mark event as processed: {e}")

   # Initialize processor
   processor = WebhookProcessor(DATABASE_PATH)

   def verify_webhook_signature(payload: bytes, signature: str) -> bool:
       """Verify webhook signature to ensure authenticity."""
       if not signature:
           return False
       
       expected_signature = hmac.new(
           WEBHOOK_SECRET.encode(),
           payload,
           hashlib.sha256
       ).hexdigest()
       
       return hmac.compare_digest(f"sha256={expected_signature}", signature)

   @app.route('/webhook', methods=['POST'])
   def handle_webhook():
       """Main webhook endpoint."""
       try:
           # Verify signature
           signature = request.headers.get('X-PMH-Signature')
           if not verify_webhook_signature(request.data, signature):
               logger.warning("Invalid webhook signature")
               return jsonify({'error': 'Invalid signature'}), 401
           
           # Parse event data
           event_data = request.json
           if not event_data:
               return jsonify({'error': 'No event data provided'}), 400
           
           event_type = event_data.get('type')
           if not event_type:
               return jsonify({'error': 'No event type specified'}), 400
           
           # Store event
           if not processor.store_event(event_data):
               return jsonify({'error': 'Failed to store event'}), 500
           
           # Process event based on type
           if event_type == 'achievement.unlocked':
               processor.process_achievement_unlocked(event_data)
           
           elif event_type == 'course.completed':
               processor.process_course_completed(event_data)
           
           elif event_type == 'exercise.submitted':
               processor.process_exercise_submitted(event_data)
           
           elif event_type == 'user.registered':
               processor.process_user_registered(event_data)
           
           else:
               logger.warning(f"Unknown event type: {event_type}")
           
           # Mark as processed
           processor.mark_event_processed(event_data.get('id'))
           
           return jsonify({'status': 'processed'}), 200
           
       except Exception as e:
           logger.error(f"Webhook processing error: {e}")
           return jsonify({'error': 'Internal server error'}), 500

   @app.route('/webhook/test', methods=['POST'])
   def test_webhook():
       """Test endpoint for webhook validation."""
       return jsonify({'status': 'webhook endpoint is working'}), 200

   @app.route('/webhook/health', methods=['GET'])
   def health_check():
       """Health check endpoint."""
       return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

   @app.route('/webhook/events', methods=['GET'])
   def list_events():
       """List recent webhook events (for debugging)."""
       try:
           conn = sqlite3.connect(DATABASE_PATH)
           cursor = conn.cursor()
           
           cursor.execute('''
               SELECT event_id, event_type, user_id, processed, created_at
               FROM webhook_events 
               ORDER BY created_at DESC 
               LIMIT 50
           ''')
           
           events = []
           for row in cursor.fetchall():
               events.append({
                   'event_id': row[0],
                   'event_type': row[1],
                   'user_id': row[2],
                   'processed': bool(row[3]),
                   'created_at': row[4]
               })
           
           conn.close()
           
           return jsonify({'events': events}), 200
           
       except Exception as e:
           logger.error(f"Failed to list events: {e}")
           return jsonify({'error': 'Failed to retrieve events'}), 500

   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000, debug=False)

Learning Analytics Dashboard
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Create a comprehensive analytics dashboard that aggregates data from multiple API endpoints.

.. code-block:: python

   # File: analytics_dashboard.py
   import streamlit as st
   import plotly.express as px
   import plotly.graph_objects as go
   from plotly.subplots import make_subplots
   import pandas as pd
   import numpy as np
   from datetime import datetime, timedelta
   import asyncio
   import aiohttp
   import os
   from pmh_client import PMHClient, PMHAPIError

   # Page configuration
   st.set_page_config(
       page_title="PMH Analytics Dashboard",
       page_icon="📊",
       layout="wide",
       initial_sidebar_state="expanded"
   )

   class AnalyticsDashboard:
       """Interactive analytics dashboard for Python Mastery Hub."""
       
       def __init__(self, api_key: str):
           self.client = PMHClient(api_key)
           
       @st.cache_data(ttl=300)  # Cache for 5 minutes
       def load_overview_data(_self, days: int = 30):
           """Load overview analytics data."""
           try:
               end_date = datetime.now()
               start_date = end_date - timedelta(days=days)
               
               # Fetch data from multiple endpoints
               overview = _self.client.get_analytics_overview(
                   start_date.isoformat(),
                   end_date.isoformat()
               )
               
               courses = _self.client.list_courses(limit=100)
               
               # Get user statistics
               users_data = _self.client.get('/admin/users/statistics')
               
               return {
                   'overview': overview['data'],
                   'courses': courses['data']['courses'],
                   'users': users_data['data']
               }
               
           except PMHAPIError as e:
               st.error(f"Failed to load data: {e}")
               return None
       
       @st.cache_data(ttl=600)  # Cache for 10 minutes
       def load_course_analytics(_self, course_id: str):
           """Load detailed course analytics."""
           try:
               course_data = _self.client.get(f'/courses/{course_id}/analytics')
               student_progress = _self.client.get(f'/courses/{course_id}/students/progress')
               
               return {
                   'course': course_data['data'],
                   'students': student_progress['data']
               }
               
           except PMHAPIError as e:
               st.error(f"Failed to load course data: {e}")
               return None
       
       def render_sidebar(self):
           """Render sidebar with filters and options."""
           st.sidebar.title("🎛️ Dashboard Controls")
           
           # Time period selector
           time_period = st.sidebar.selectbox(
               "📅 Time Period",
               options=[7, 14, 30, 60, 90],
               index=2,
               format_func=lambda x: f"Last {x} days"
           )
           
           # Dashboard view selector
           view = st.sidebar.radio(
               "📊 Dashboard View",
               options=["Overview", "Course Analytics", "User Analytics", "Performance"]
           )
           
           # Refresh button
           if st.sidebar.button("🔄 Refresh Data"):
               st.cache_data.clear()
               st.experimental_rerun()
           
           return time_period, view
       
       def render_overview_dashboard(self, days: int):
           """Render main overview dashboard."""
           data = self.load_overview_data(days)
           if not data:
               return
           
           overview = data['overview']
           courses = data['courses']
           users = data['users']
           
           # Key metrics
           col1, col2, col3, col4 = st.columns(4)
           
           with col1:
               st.metric(
                   label="👥 Total Users",
                   value=f"{users['total_users']:,}",
                   delta=f"+{users.get('new_users_this_period', 0)}"
               )
           
           with col2:
               st.metric(
                   label="📚 Active Courses", 
                   value=len([c for c in courses if c.get('is_active', True)]),
                   delta=f"+{overview.get('new_courses', 0)}"
               )
           
           with col3:
               st.metric(
                   label="💻 Exercise Submissions",
                   value=f"{overview.get('total_submissions', 0):,}",
                   delta=f"+{overview.get('submissions_this_period', 0)}"
               )
           
           with col4:
               st.metric(
                   label="🏆 Achievements Earned",
                   value=f"{overview.get('total_achievements', 0):,}",
                   delta=f"+{overview.get('achievements_this_period', 0)}"
               )
           
           # Charts row
           col1, col2 = st.columns(2)
           
           with col1:
               # User activity timeline
               if 'daily_activity' in overview:
                   activity_df = pd.DataFrame(overview['daily_activity'])
                   activity_df['date'] = pd.to_datetime(activity_df['date'])
                   
                   fig = px.line(
                       activity_df, 
                       x='date', 
                       y='active_users',
                       title="📈 Daily Active Users",
                       color_discrete_sequence=['#3498db']
                   )
                   fig.update_layout(
                       xaxis_title="Date",
                       yaxis_title="Active Users",
                       hovermode='x'
                   )
                   st.plotly_chart(fig, use_container_width=True)
           
           with col2:
               # Course popularity
               course_df = pd.DataFrame(courses)
               if not course_df.empty:
                   top_courses = course_df.nlargest(10, 'enrollment_count')
                   
                   fig = px.bar(
                       top_courses,
                       x='enrollment_count',
                       y='title',
                       orientation='h',
                       title="📊 Most Popular Courses",
                       color='enrollment_count',
                       color_continuous_scale='viridis'
                   )
                   fig.update_layout(
                       xaxis_title="Enrollments",
                       yaxis_title="Course",
                       height=400
                   )
                   st.plotly_chart(fig, use_container_width=True)
           
           # Progress distribution
           st.subheader("📈 Learning Progress Distribution")
           
           if 'progress_distribution' in overview:
               progress_data = overview['progress_distribution']
               
               # Create subplot with multiple charts
               fig = make_subplots(
                   rows=1, cols=2,
                   subplot_titles=('Course Completion Distribution', 'XP Distribution'),
                   specs=[[{"secondary_y": False}, {"secondary_y": False}]]
               )
               
               # Course completion histogram
               if 'completion_rates' in progress_data:
                   completion_rates = progress_data['completion_rates']
                   
                   fig.add_trace(
                       go.Histogram(
                           x=completion_rates,
                           nbinsx=20,
                           name="Completion Rate",
                           marker_color='lightblue'
                       ),
                       row=1, col=1
                   )
               
               # XP distribution
               if 'xp_distribution' in progress_data:
                   xp_data = progress_data['xp_distribution']
                   
                   fig.add_trace(
                       go.Histogram(
                           x=xp_data,
                           nbinsx=15,
                           name="XP Distribution",
                           marker_color='lightgreen'
                       ),
                       row=1, col=2
                   )
               
               fig.update_layout(height=400, showlegend=False)
               st.plotly_chart(fig, use_container_width=True)
       
       def render_course_analytics(self):
           """Render course-specific analytics."""
           st.subheader("📚 Course Analytics")
           
           # Course selector
           data = self.load_overview_data()
           if not data:
               return
           
           courses = data['courses']
           course_options = {f"{c['title']} ({c['id']})": c['id'] for c in courses}
           
           selected_course = st.selectbox(
               "Select Course",
               options=list(course_options.keys())
           )
           
           if selected_course:
               course_id = course_options[selected_course]
               course_data = self.load_course_analytics(course_id)
               
               if course_data:
                   self.render_course_details(course_data)
       
       def render_course_details(self, course_data):
           """Render detailed course analytics."""
           course_info = course_data['course']
           students = course_data['students']
           
           # Course metrics
           col1, col2, col3, col4 = st.columns(4)
           
           with col1:
               st.metric(
                   "👨‍🎓 Enrolled Students",
                   course_info.get('total_students', 0)
               )
           
           with col2:
               st.metric(
                   "✅ Completion Rate",
                   f"{course_info.get('completion_rate', 0):.1f}%"
               )
           
           with col3:
               st.metric(
                   "⭐ Average Score",
                   f"{course_info.get('average_score', 0):.1f}%"
               )
           
           with col4:
               st.metric(
                   "⏱️ Avg. Time to Complete",
                   f"{course_info.get('avg_completion_time_hours', 0):.1f}h"
               )
           
           # Student progress table
           if 'students' in students:
               st.subheader("👥 Student Progress")
               
               students_df = pd.DataFrame(students['students'])
               if not students_df.empty:
                   # Add progress bar column
                   students_df['Progress'] = students_df['progress_percentage'].apply(
                       lambda x: f"{x:.1f}%"
                   )
                   
                   st.dataframe(
                       students_df[['name', 'email', 'Progress', 'lessons_completed', 'exercises_completed', 'last_activity']],
                       use_container_width=True
                   )
                   
                   # Export option
                   csv = students_df.to_csv(index=False)
                   st.download_button(
                       label="📥 Download Student Data",
                       data=csv,
                       file_name=f"course_progress_{datetime.now().strftime('%Y%m%d')}.csv",
                       mime="text/csv"
                   )

   def main():
       """Main dashboard application."""
       st.title("📊 Python Mastery Hub Analytics Dashboard")
       st.markdown("---")
       
       # Check for API key
       api_key = os.getenv('PMH_API_KEY')
       if not api_key:
           st.error("❌ PMH_API_KEY environment variable not set")
           st.stop()
       
       # Initialize dashboard
       dashboard = AnalyticsDashboard(api_key)
       
       # Render sidebar and get selections
       time_period, view = dashboard.render_sidebar()
       
       # Render selected view
       if view == "Overview":
           dashboard.render_overview_dashboard(time_period)
       elif view == "Course Analytics":
           dashboard.render_course_analytics()
       elif view == "User Analytics":
           st.info("🚧 User Analytics view coming soon!")
       elif view == "Performance":
           st.info("🚧 Performance Analytics view coming soon!")
       
       # Footer
       st.markdown("---")
       st.markdown(
           f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
           f"Data refreshes every 5 minutes*"
       )

   if __name__ == "__main__":
       main()

Node.js API Integration Examples
-------------------------------

Express.js Middleware and Routes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Create Express.js middleware for authentication and API integration.

.. code-block:: javascript

   // File: pmh-middleware.js
   const axios = require('axios');
   const rateLimit = require('express-rate-limit');
   const NodeCache = require('node-cache');

   class PMHIntegration {
     constructor(apiKey, baseURL = 'https://api.pythonmasteryhub.com/v1') {
       this.apiKey = apiKey;
       this.baseURL = baseURL;
       this.cache = new NodeCache({ stdTTL: 300 }); // 5 minute cache
       
       this.client = axios.create({
         baseURL: this.baseURL,
         headers: {
           'Authorization': `Bearer ${apiKey}`,
           'Content-Type': 'application/json'
         }
       });
       
       // Setup response interceptor for error handling
       this.client.interceptors.response.use(
         response => response,
         error => {
           console.error('PMH API Error:', error.response?.data || error.message);
           throw error;
         }
       );
     }

     // Middleware for authenticating PMH users
     authenticateUser() {
       return async (req, res, next) => {
         try {
           const token = req.headers.authorization?.split(' ')[1];
           
           if (!token) {
             return res.status(401).json({ error: 'No authentication token provided' });
           }
           
           // Check cache first
           const cachedUser = this.cache.get(`user_${token}`);
           if (cachedUser) {
             req.user = cachedUser;
             return next();
           }
           
           // Verify token with PMH API
           const response = await this.client.get('/auth/verify', {
             headers: { 'Authorization': `Bearer ${token}` }
           });
           
           const user = response.data.data.user;
           
           // Cache user data
           this.cache.set(`user_${token}`, user);
           
           req.user = user;
           next();
           
         } catch (error) {
           res.status(401).json({ error: 'Invalid authentication token' });
         }
       };
     }

     // Middleware for checking user roles
     requireRole(roles) {
       return (req, res, next) => {
         if (!req.user) {
           return res.status(401).json({ error: 'Authentication required' });
         }
         
         const userRole = req.user.role;
         const allowedRoles = Array.isArray(roles) ? roles : [roles];
         
         if (!allowedRoles.includes(userRole)) {
           return res.status(403).json({ error: 'Insufficient permissions' });
         }
         
         next();
       };
     }

     // Middleware for caching API responses
     cacheMiddleware(ttl = 300) {
       return (req, res, next) => {
         const cacheKey = `${req.method}_${req.originalUrl}`;
         const cachedResponse = this.cache.get(cacheKey);
         
         if (cachedResponse) {
           return res.json(cachedResponse);
         }
         
         // Override res.json to cache the response
         const originalJson = res.json;
         res.json = function(data) {
           this.cache.set(cacheKey, data, ttl);
           originalJson.call(this, data);
         }.bind(this);
         
         next();
       };
     }

     // Get user progress with caching
     async getUserProgress(userId, useCache = true) {
       const cacheKey = `progress_${userId}`;
       
       if (useCache) {
         const cached = this.cache.get(cacheKey);
         if (cached) return cached;
       }
       
       try {
         const response = await this.client.get(`/users/${userId}/progress`);
         const progress = response.data.data;
         
         this.cache.set(cacheKey, progress);
         return progress;
         
       } catch (error) {
         throw new Error(`Failed to fetch user progress: ${error.message}`);
       }
     }

     // Enroll user in course
     async enrollUserInCourse(userId, courseId) {
       try {
         const response = await this.client.post(`/courses/${courseId}/enroll`, {
           user_id: userId
         });
         
         // Invalidate user progress cache
         this.cache.del(`progress_${userId}`);
         
         return response.data.data;
         
       } catch (error) {
         throw new Error(`Failed to enroll user: ${error.message}`);
       }
     }

     // Submit exercise solution
     async submitExercise(userId, exerciseId, code) {
       try {
         const response = await this.client.post(`/exercises/${exerciseId}/submit`, {
           code: code,
           user_id: userId
         });
         
         // Invalidate related caches
         this.cache.del(`progress_${userId}`);
         this.cache.del(`exercise_${exerciseId}_${userId}`);
         
         return response.data.data;
         
       } catch (error) {
         throw new Error(`Failed to submit exercise: ${error.message}`);
       }
     }
   }

   // Express.js application setup
   const express = require('express');
   const cors = require('cors');
   const helmet = require('helmet');

   const app = express();
   const pmh = new PMHIntegration(process.env.PMH_API_KEY);

   // Middleware setup
   app.use(helmet());
   app.use(cors());
   app.use(express.json());

   // Rate limiting
   const limiter = rateLimit({
     windowMs: 15 * 60 * 1000, // 15 minutes
     max: 100 // limit each IP to 100 requests per windowMs
   });
   app.use('/api/', limiter);

   // Routes
   app.get('/api/user/profile', pmh.authenticateUser(), async (req, res) => {
     try {
       res.json({
         success: true,
         data: req.user
       });
     } catch (error) {
       res.status(500).json({ error: error.message });
     }
   });

   app.get('/api/user/progress', 
     pmh.authenticateUser(), 
     pmh.cacheMiddleware(300),
     async (req, res) => {
       try {
         const progress = await pmh.getUserProgress(req.user.id);
         res.json({
           success: true,
           data: progress
         });
       } catch (error) {
         res.status(500).json({ error: error.message });
       }
     }
   );

   app.post('/api/courses/:courseId/enroll', 
     pmh.authenticateUser(),
     async (req, res) => {
       try {
         const enrollment = await pmh.enrollUserInCourse(
           req.user.id, 
           req.params.courseId
         );
         
         res.json({
           success: true,
           data: enrollment
         });
       } catch (error) {
         res.status(500).json({ error: error.message });
       }
     }
   );

   app.post('/api/exercises/:exerciseId/submit',
     pmh.authenticateUser(),
     async (req, res) => {
       try {
         const { code } = req.body;
         
         if (!code) {
           return res.status(400).json({ error: 'Code is required' });
         }
         
         const result = await pmh.submitExercise(
           req.user.id,
           req.params.exerciseId,
           code
         );
         
         res.json({
           success: true,
           data: result
         });
       } catch (error) {
         res.status(500).json({ error: error.message });
       }
     }
   );

   // Admin routes
   app.get('/api/admin/users', 
     pmh.authenticateUser(),
     pmh.requireRole(['admin', 'instructor']),
     async (req, res) => {
       try {
         const response = await pmh.client.get('/admin/users', {
           params: req.query
         });
         
         res.json({
           success: true,
           data: response.data.data
         });
       } catch (error) {
         res.status(500).json({ error: error.message });
       }
     }
   );

   // Health check endpoint
   app.get('/health', (req, res) => {
     res.json({
       status: 'healthy',
       timestamp: new Date().toISOString(),
       uptime: process.uptime()
     });
   });

   // Error handling middleware
   app.use((error, req, res, next) => {
     console.error('Unhandled error:', error);
     res.status(500).json({
       error: 'Internal server error',
       message: error.message
     });
   });

   const PORT = process.env.PORT || 3000;
   app.listen(PORT, () => {
     console.log(`Server running on port ${PORT}`);
   });

   module.exports = { PMHIntegration, app };

Best Practices and Guidelines
----------------------------

Error Handling Patterns
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Comprehensive error handling
   import logging
   from tenacity import retry, stop_after_attempt, wait_exponential

   class PMHAPIHandler:
       def __init__(self, api_key):
           self.client = PMHClient(api_key)
           self.logger = logging.getLogger(__name__)
       
       @retry(
           stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=4, max=10)
       )
       def robust_api_call(self, method, endpoint, **kwargs):
           """Make API call with automatic retry on failures."""
           try:
               if method.upper() == 'GET':
                   return self.client.get(endpoint, **kwargs)
               elif method.upper() == 'POST':
                   return self.client.post(endpoint, **kwargs)
               elif method.upper() == 'PUT':
                   return self.client.put(endpoint, **kwargs)
               elif method.upper() == 'DELETE':
                   return self.client.delete(endpoint, **kwargs)
               
           except PMHAPIError as e:
               self.logger.error(f"API error: {e}")
               
               # Handle specific error codes
               if e.status_code == 429:  # Rate limit
                   self.logger.warning("Rate limit exceeded, backing off...")
                   raise  # Let retry decorator handle it
               elif e.status_code == 401:  # Authentication
                   self.logger.error("Authentication failed")
                   # Don't retry auth errors
                   raise
               elif e.status_code >= 500:  # Server errors
                   self.logger.warning("Server error, retrying...")
                   raise  # Let retry decorator handle it
               else:
                   # Client errors shouldn't be retried
                   raise

Rate Limiting and Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   import aiohttp
   from asyncio import Semaphore

   class AsyncPMHClient:
       """Async client with built-in rate limiting."""
       
       def __init__(self, api_key, max_concurrent=10, requests_per_second=5):
           self.api_key = api_key
           self.base_url = "https://api.pythonmasteryhub.com/v1"
           self.semaphore = Semaphore(max_concurrent)
           self.rate_limit = requests_per_second
           self.last_request_time = 0
       
       async def _rate_limit(self):
           """Implement rate limiting."""
           current_time = asyncio.get_event_loop().time()
           time_since_last = current_time - self.last_request_time
           min_interval = 1.0 / self.rate_limit
           
           if time_since_last < min_interval:
               await asyncio.sleep(min_interval - time_since_last)
           
           self.last_request_time = asyncio.get_event_loop().time()
       
       async def request(self, method, endpoint, **kwargs):
           """Make rate-limited async request."""
           async with self.semaphore:
               await self._rate_limit()
               
               headers = {
                   'Authorization': f'Bearer {self.api_key}',
                   'Content-Type': 'application/json'
               }
               
               async with aiohttp.ClientSession() as session:
                   async with session.request(
                       method, 
                       f"{self.base_url}{endpoint}",
                       headers=headers,
                       **kwargs
                   ) as response:
                       response.raise_for_status()
                       return await response.json()

Security Best Practices
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Secure API key management
   import os
   from cryptography.fernet import Fernet

   class SecureAPIClient:
       def __init__(self):
           # Load encrypted API key
           self.api_key = self._load_encrypted_api_key()
           
       def _load_encrypted_api_key(self):
           """Load and decrypt API key from secure storage."""
           key = os.getenv('ENCRYPTION_KEY').encode()
           encrypted_key = os.getenv('ENCRYPTED_PMH_API_KEY').encode()
           
           f = Fernet(key)
           decrypted_key = f.decrypt(encrypted_key)
           return decrypted_key.decode()
       
       def _validate_input(self, data):
           """Validate and sanitize input data."""
           # Implement input validation logic
           if isinstance(data, dict):
               for key, value in data.items():
                   if isinstance(value, str):
                       # Basic XSS prevention
                       data[key] = value.replace('<', '&lt;').replace('>', '&gt;')
           return data

Getting Help and Resources
-------------------------

- **API Documentation**: :doc:`../api/web` for complete endpoint reference
- **Rate Limits**: Monitor `X-RateLimit-*` headers in responses
- **Error Codes**: See API documentation for complete error code reference
- **SDKs**: Official SDKs available for Python, JavaScript, Go, and PHP
- **Support**: Enterprise customers get priority API support
- **Community**: Discord #api-help channel for developer assistance

.. admonition:: Build Robust Integrations! 🔧
   :class: tip

   When building API integrations, always implement proper error handling, 
   rate limiting, and caching. Monitor your API usage and implement exponential 
   backoff for retries. Keep your API keys secure and never expose them in 
   client-side code. Test your integrations thoroughly before deploying to production!