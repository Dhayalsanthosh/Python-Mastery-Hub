.. File: docs/source/examples/web_examples.rst

Web Examples
============

These examples demonstrate how to integrate Python Mastery Hub with web applications, 
create custom user interfaces, and build enhanced learning experiences using modern 
web technologies.

.. note::
   **Prerequisites**: Basic knowledge of HTML, CSS, JavaScript, and your chosen 
   web framework (React, Vue, Angular, etc.). Familiarity with REST APIs recommended.

Quick Start
-----------

Essential setup for web integration:

.. code-block:: bash

   # Install required dependencies
   npm install axios react react-dom @types/react
   # or
   pip install requests flask jinja2

.. code-block:: javascript

   // JavaScript API client setup
   const PMH_API_BASE = 'https://api.pythonmasteryhub.com/v1';
   const API_KEY = 'your_api_key_here';
   
   const apiClient = axios.create({
     baseURL: PMH_API_BASE,
     headers: {
       'Authorization': `Bearer ${API_KEY}`,
       'Content-Type': 'application/json'
     }
   });

React Integration Examples
-------------------------

Student Progress Dashboard
~~~~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Create a comprehensive student dashboard showing course progress, achievements, and learning analytics.

.. code-block:: jsx

   // File: components/StudentDashboard.jsx
   import React, { useState, useEffect } from 'react';
   import { Line, Doughnut, Bar } from 'react-chartjs-2';
   import axios from 'axios';
   
   const StudentDashboard = ({ userId }) => {
     const [dashboardData, setDashboardData] = useState(null);
     const [loading, setLoading] = useState(true);
     const [error, setError] = useState(null);
   
     useEffect(() => {
       fetchDashboardData();
       
       // Set up real-time updates
       const interval = setInterval(fetchDashboardData, 30000);
       return () => clearInterval(interval);
     }, [userId]);
   
     const fetchDashboardData = async () => {
       try {
         const [progress, achievements, analytics] = await Promise.all([
           apiClient.get(`/users/${userId}/progress`),
           apiClient.get(`/users/${userId}/achievements`),
           apiClient.get(`/users/${userId}/analytics`)
         ]);
   
         setDashboardData({
           progress: progress.data,
           achievements: achievements.data,
           analytics: analytics.data
         });
         setLoading(false);
       } catch (err) {
         setError(err.message);
         setLoading(false);
       }
     };
   
     if (loading) return <LoadingSpinner />;
     if (error) return <ErrorMessage message={error} />;
   
     const { progress, achievements, analytics } = dashboardData;
   
     return (
       <div className="student-dashboard">
         <header className="dashboard-header">
           <h1>Learning Dashboard</h1>
           <div className="quick-stats">
             <StatCard 
               title="Current Level" 
               value={progress.current_level} 
               icon="🏆" 
             />
             <StatCard 
               title="XP Earned" 
               value={progress.total_xp.toLocaleString()} 
               icon="⭐" 
             />
             <StatCard 
               title="Streak" 
               value={`${progress.current_streak} days`} 
               icon="🔥" 
             />
             <StatCard 
               title="Courses" 
               value={`${progress.completed_courses}/${progress.enrolled_courses}`} 
               icon="📚" 
             />
           </div>
         </header>
   
         <div className="dashboard-grid">
           <section className="progress-section">
             <h2>Course Progress</h2>
             <CourseProgressList courses={progress.courses} />
           </section>
   
           <section className="analytics-section">
             <h2>Learning Analytics</h2>
             <LearningChart data={analytics.weekly_progress} />
           </section>
   
           <section className="achievements-section">
             <h2>Recent Achievements</h2>
             <AchievementsList achievements={achievements.recent} />
           </section>
   
           <section className="activity-section">
             <h2>Recent Activity</h2>
             <ActivityFeed activities={progress.recent_activities} />
           </section>
         </div>
       </div>
     );
   };
   
   // Supporting components
   const StatCard = ({ title, value, icon }) => (
     <div className="stat-card">
       <div className="stat-icon">{icon}</div>
       <div className="stat-content">
         <div className="stat-value">{value}</div>
         <div className="stat-title">{title}</div>
       </div>
     </div>
   );
   
   const CourseProgressList = ({ courses }) => (
     <div className="course-progress-list">
       {courses.map(course => (
         <div key={course.id} className="course-progress-item">
           <div className="course-header">
             <h3>{course.title}</h3>
             <span className="progress-percentage">{course.progress}%</span>
           </div>
           <div className="progress-bar">
             <div 
               className="progress-fill" 
               style={{ width: `${course.progress}%` }}
             />
           </div>
           <div className="course-stats">
             <span>📖 {course.lessons_completed}/{course.total_lessons} lessons</span>
             <span>💻 {course.exercises_completed}/{course.total_exercises} exercises</span>
           </div>
         </div>
       ))}
     </div>
   );
   
   const LearningChart = ({ data }) => {
     const chartData = {
       labels: data.map(d => d.date),
       datasets: [{
         label: 'Daily XP',
         data: data.map(d => d.xp_earned),
         borderColor: 'rgb(75, 192, 192)',
         backgroundColor: 'rgba(75, 192, 192, 0.2)',
         tension: 0.1
       }]
     };
   
     const options = {
       responsive: true,
       plugins: {
         legend: {
           position: 'top',
         },
         title: {
           display: true,
           text: 'Weekly Learning Progress'
         }
       },
       scales: {
         y: {
           beginAtZero: true
         }
       }
     };
   
     return <Line data={chartData} options={options} />;
   };
   
   const AchievementsList = ({ achievements }) => (
     <div className="achievements-list">
       {achievements.map(achievement => (
         <div key={achievement.id} className="achievement-item">
           <div className="achievement-icon">{achievement.icon}</div>
           <div className="achievement-content">
             <h4>{achievement.name}</h4>
             <p>{achievement.description}</p>
             <span className="achievement-date">
               Earned {new Date(achievement.unlocked_at).toLocaleDateString()}
             </span>
           </div>
         </div>
       ))}
     </div>
   );
   
   const ActivityFeed = ({ activities }) => (
     <div className="activity-feed">
       {activities.map((activity, index) => (
         <div key={index} className="activity-item">
           <div className="activity-icon">{getActivityIcon(activity.type)}</div>
           <div className="activity-content">
             <p>{activity.description}</p>
             <span className="activity-time">
               {formatTimeAgo(activity.timestamp)}
             </span>
           </div>
         </div>
       ))}
     </div>
   );
   
   // Utility functions
   const getActivityIcon = (type) => {
     const icons = {
       'lesson_complete': '📖',
       'exercise_complete': '💻',
       'achievement_unlocked': '🏆',
       'course_complete': '🎓'
     };
     return icons[type] || '📝';
   };
   
   const formatTimeAgo = (timestamp) => {
     const now = new Date();
     const time = new Date(timestamp);
     const diffInHours = Math.floor((now - time) / (1000 * 60 * 60));
     
     if (diffInHours < 1) return 'Just now';
     if (diffInHours < 24) return `${diffInHours}h ago`;
     return `${Math.floor(diffInHours / 24)}d ago`;
   };
   
   export default StudentDashboard;

**Styling** (CSS):

.. code-block:: css

   /* File: styles/StudentDashboard.css */
   .student-dashboard {
     max-width: 1200px;
     margin: 0 auto;
     padding: 20px;
     font-family: 'Inter', sans-serif;
   }
   
   .dashboard-header {
     margin-bottom: 30px;
   }
   
   .dashboard-header h1 {
     color: #2c3e50;
     margin-bottom: 20px;
   }
   
   .quick-stats {
     display: grid;
     grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
     gap: 20px;
     margin-bottom: 30px;
   }
   
   .stat-card {
     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
     color: white;
     padding: 20px;
     border-radius: 12px;
     display: flex;
     align-items: center;
     box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
     transition: transform 0.2s ease;
   }
   
   .stat-card:hover {
     transform: translateY(-2px);
   }
   
   .stat-icon {
     font-size: 2.5rem;
     margin-right: 15px;
   }
   
   .stat-value {
     font-size: 2rem;
     font-weight: bold;
     line-height: 1;
   }
   
   .stat-title {
     font-size: 0.9rem;
     opacity: 0.9;
     margin-top: 5px;
   }
   
   .dashboard-grid {
     display: grid;
     grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
     gap: 30px;
   }
   
   .dashboard-grid section {
     background: white;
     border-radius: 12px;
     padding: 25px;
     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
   }
   
   .dashboard-grid h2 {
     color: #2c3e50;
     margin-bottom: 20px;
     font-size: 1.3rem;
   }
   
   .course-progress-item {
     background: #f8f9fa;
     border-radius: 8px;
     padding: 15px;
     margin-bottom: 15px;
   }
   
   .course-header {
     display: flex;
     justify-content: space-between;
     align-items: center;
     margin-bottom: 10px;
   }
   
   .course-header h3 {
     margin: 0;
     color: #2c3e50;
   }
   
   .progress-percentage {
     font-weight: bold;
     color: #27ae60;
   }
   
   .progress-bar {
     background: #e9ecef;
     border-radius: 10px;
     height: 8px;
     margin-bottom: 10px;
     overflow: hidden;
   }
   
   .progress-fill {
     background: linear-gradient(90deg, #27ae60, #2ecc71);
     height: 100%;
     border-radius: 10px;
     transition: width 0.3s ease;
   }
   
   .course-stats {
     display: flex;
     gap: 15px;
     font-size: 0.9rem;
     color: #6c757d;
   }
   
   .achievement-item {
     display: flex;
     align-items: center;
     padding: 12px;
     border-radius: 8px;
     margin-bottom: 10px;
     background: #f8f9fa;
   }
   
   .achievement-icon {
     font-size: 2rem;
     margin-right: 15px;
   }
   
   .achievement-content h4 {
     margin: 0 0 5px 0;
     color: #2c3e50;
   }
   
   .achievement-content p {
     margin: 0 0 5px 0;
     font-size: 0.9rem;
     color: #6c757d;
   }
   
   .achievement-date {
     font-size: 0.8rem;
     color: #28a745;
   }
   
   .activity-item {
     display: flex;
     align-items: start;
     padding: 10px 0;
     border-bottom: 1px solid #e9ecef;
   }
   
   .activity-item:last-child {
     border-bottom: none;
   }
   
   .activity-icon {
     margin-right: 10px;
     font-size: 1.2rem;
   }
   
   .activity-content p {
     margin: 0 0 5px 0;
     font-size: 0.9rem;
   }
   
   .activity-time {
     font-size: 0.8rem;
     color: #6c757d;
   }

Interactive Code Editor Component
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Embed an interactive Python code editor with syntax highlighting and execution capabilities.

.. code-block:: jsx

   // File: components/CodeEditor.jsx
   import React, { useState, useEffect } from 'react';
   import MonacoEditor from '@monaco-editor/react';
   import axios from 'axios';
   
   const CodeEditor = ({ 
     exerciseId, 
     initialCode = '', 
     readOnly = false,
     theme = 'vs-dark'
   }) => {
     const [code, setCode] = useState(initialCode);
     const [output, setOutput] = useState('');
     const [isRunning, setIsRunning] = useState(false);
     const [testResults, setTestResults] = useState(null);
     const [hints, setHints] = useState([]);
     const [showHints, setShowHints] = useState(false);
   
     useEffect(() => {
       if (exerciseId) {
         fetchExerciseData();
       }
     }, [exerciseId]);
   
     const fetchExerciseData = async () => {
       try {
         const response = await apiClient.get(`/exercises/${exerciseId}`);
         const exercise = response.data;
         
         setCode(exercise.starter_code || '# Write your code here\n');
         setHints(exercise.hints || []);
       } catch (error) {
         console.error('Failed to fetch exercise data:', error);
       }
     };
   
     const runCode = async () => {
       setIsRunning(true);
       setOutput('Running...');
       
       try {
         const response = await apiClient.post('/code/execute', {
           code: code,
           language: 'python'
         });
         
         setOutput(response.data.output || response.data.error);
       } catch (error) {
         setOutput(`Error: ${error.message}`);
       } finally {
         setIsRunning(false);
       }
     };
   
     const submitSolution = async () => {
       setIsRunning(true);
       
       try {
         const response = await apiClient.post(`/exercises/${exerciseId}/submit`, {
           code: code
         });
         
         setTestResults(response.data);
         setOutput(formatTestResults(response.data));
       } catch (error) {
         setOutput(`Submission failed: ${error.message}`);
       } finally {
         setIsRunning(false);
       }
     };
   
     const formatTestResults = (results) => {
       if (!results.test_results) return results.output || '';
       
       let output = `Score: ${results.score}/${results.max_score}\n\n`;
       
       results.test_results.forEach((test, index) => {
         const status = test.status === 'passed' ? '✅' : '❌';
         output += `${status} Test ${index + 1}: ${test.test_case_name}\n`;
         
         if (test.status === 'failed') {
           output += `  Expected: ${test.expected_output}\n`;
           output += `  Got: ${test.actual_output}\n`;
         }
         
         if (test.error_message) {
           output += `  Error: ${test.error_message}\n`;
         }
         
         output += '\n';
       });
       
       return output;
     };
   
     const getNextHint = () => {
       const currentHintLevel = hints.findIndex(hint => !hint.used);
       if (currentHintLevel >= 0 && currentHintLevel < hints.length) {
         setHints(prev => prev.map((hint, index) => 
           index === currentHintLevel ? { ...hint, used: true } : hint
         ));
         return hints[currentHintLevel];
       }
       return null;
     };
   
     return (
       <div className="code-editor-container">
         <div className="editor-header">
           <div className="editor-actions">
             <button 
               onClick={runCode} 
               disabled={isRunning}
               className="btn btn-primary"
             >
               {isRunning ? '🔄 Running...' : '▶️ Run Code'}
             </button>
             
             {exerciseId && (
               <button 
                 onClick={submitSolution} 
                 disabled={isRunning}
                 className="btn btn-success"
               >
                 {isRunning ? '🔄 Submitting...' : '📝 Submit Solution'}
               </button>
             )}
             
             {hints.length > 0 && (
               <button 
                 onClick={() => setShowHints(!showHints)}
                 className="btn btn-info"
               >
                 💡 Hints ({hints.filter(h => h.used).length}/{hints.length})
               </button>
             )}
           </div>
           
           <div className="editor-settings">
             <select 
               value={theme} 
               onChange={(e) => setTheme(e.target.value)}
               className="theme-selector"
             >
               <option value="vs-dark">Dark Theme</option>
               <option value="light">Light Theme</option>
               <option value="hc-black">High Contrast</option>
             </select>
           </div>
         </div>
   
         <div className="editor-main">
           <div className="code-panel">
             <MonacoEditor
               height="400px"
               language="python"
               theme={theme}
               value={code}
               onChange={setCode}
               options={{
                 readOnly: readOnly,
                 minimap: { enabled: false },
                 scrollBeyondLastLine: false,
                 fontSize: 14,
                 wordWrap: 'on',
                 automaticLayout: true
               }}
             />
           </div>
           
           <div className="output-panel">
             <div className="panel-header">
               <h3>Output</h3>
               {testResults && (
                 <div className="test-summary">
                   Score: {testResults.score}/{testResults.max_score}
                   {testResults.status === 'passed' && ' ✅'}
                   {testResults.status === 'failed' && ' ❌'}
                 </div>
               )}
             </div>
             
             <pre className="output-content">{output}</pre>
           </div>
         </div>
   
         {showHints && (
           <div className="hints-panel">
             <div className="hints-header">
               <h3>Hints</h3>
               <button 
                 onClick={getNextHint}
                 className="btn btn-sm btn-outline"
               >
                 Get Next Hint
               </button>
             </div>
             
             <div className="hints-content">
               {hints.map((hint, index) => (
                 <div 
                   key={index} 
                   className={`hint-item ${hint.used ? 'revealed' : 'hidden'}`}
                 >
                   {hint.used && (
                     <>
                       <h4>Hint {index + 1}: {hint.title}</h4>
                       <p>{hint.content}</p>
                     </>
                   )}
                 </div>
               ))}
             </div>
           </div>
         )}
       </div>
     );
   };
   
   export default CodeEditor;

Course Catalog Component
~~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Display available courses with filtering, search, and enrollment capabilities.

.. code-block:: jsx

   // File: components/CourseCatalog.jsx
   import React, { useState, useEffect } from 'react';
   import axios from 'axios';
   
   const CourseCatalog = ({ userId }) => {
     const [courses, setCourses] = useState([]);
     const [filteredCourses, setFilteredCourses] = useState([]);
     const [loading, setLoading] = useState(true);
     const [filters, setFilters] = useState({
       difficulty: '',
       category: '',
       search: '',
       enrolled: false
     });
     const [enrolledCourses, setEnrolledCourses] = useState(new Set());
   
     useEffect(() => {
       fetchCourses();
       if (userId) {
         fetchEnrolledCourses();
       }
     }, [userId]);
   
     useEffect(() => {
       applyFilters();
     }, [courses, filters]);
   
     const fetchCourses = async () => {
       try {
         const response = await apiClient.get('/courses');
         setCourses(response.data.courses);
         setLoading(false);
       } catch (error) {
         console.error('Failed to fetch courses:', error);
         setLoading(false);
       }
     };
   
     const fetchEnrolledCourses = async () => {
       try {
         const response = await apiClient.get(`/users/${userId}/enrollments`);
         const enrolled = new Set(response.data.enrollments.map(e => e.course_id));
         setEnrolledCourses(enrolled);
       } catch (error) {
         console.error('Failed to fetch enrollments:', error);
       }
     };
   
     const applyFilters = () => {
       let filtered = [...courses];
   
       // Search filter
       if (filters.search) {
         const searchTerm = filters.search.toLowerCase();
         filtered = filtered.filter(course =>
           course.title.toLowerCase().includes(searchTerm) ||
           course.description.toLowerCase().includes(searchTerm)
         );
       }
   
       // Difficulty filter
       if (filters.difficulty) {
         filtered = filtered.filter(course => course.difficulty === filters.difficulty);
       }
   
       // Category filter
       if (filters.category) {
         filtered = filtered.filter(course => course.category === filters.category);
       }
   
       // Enrollment filter
       if (filters.enrolled) {
         filtered = filtered.filter(course => enrolledCourses.has(course.id));
       }
   
       setFilteredCourses(filtered);
     };
   
     const enrollInCourse = async (courseId) => {
       try {
         await apiClient.post(`/courses/${courseId}/enroll`);
         setEnrolledCourses(prev => new Set([...prev, courseId]));
         
         // Show success message
         showNotification('Successfully enrolled in course!', 'success');
       } catch (error) {
         showNotification('Failed to enroll in course', 'error');
       }
     };
   
     const unenrollFromCourse = async (courseId) => {
       try {
         await apiClient.delete(`/courses/${courseId}/enroll`);
         setEnrolledCourses(prev => {
           const newSet = new Set(prev);
           newSet.delete(courseId);
           return newSet;
         });
         
         showNotification('Successfully unenrolled from course', 'info');
       } catch (error) {
         showNotification('Failed to unenroll from course', 'error');
       }
     };
   
     const showNotification = (message, type) => {
       // Implementation depends on your notification system
       console.log(`${type}: ${message}`);
     };
   
     if (loading) {
       return <div className="loading-spinner">Loading courses...</div>;
     }
   
     return (
       <div className="course-catalog">
         <div className="catalog-header">
           <h1>Course Catalog</h1>
           <p>Discover and enroll in Python programming courses</p>
         </div>
   
         <div className="filters-section">
           <div className="search-bar">
             <input
               type="text"
               placeholder="Search courses..."
               value={filters.search}
               onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
               className="search-input"
             />
           </div>
   
           <div className="filter-controls">
             <select
               value={filters.difficulty}
               onChange={(e) => setFilters(prev => ({ ...prev, difficulty: e.target.value }))}
               className="filter-select"
             >
               <option value="">All Difficulties</option>
               <option value="beginner">Beginner</option>
               <option value="intermediate">Intermediate</option>
               <option value="advanced">Advanced</option>
             </select>
   
             <select
               value={filters.category}
               onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))}
               className="filter-select"
             >
               <option value="">All Categories</option>
               <option value="fundamentals">Fundamentals</option>
               <option value="web-development">Web Development</option>
               <option value="data-science">Data Science</option>
               <option value="automation">Automation</option>
             </select>
   
             {userId && (
               <label className="checkbox-label">
                 <input
                   type="checkbox"
                   checked={filters.enrolled}
                   onChange={(e) => setFilters(prev => ({ ...prev, enrolled: e.target.checked }))}
                 />
                 Show only enrolled courses
               </label>
             )}
           </div>
         </div>

         <div className="courses-grid">
           {filteredCourses.map(course => (
             <CourseCard
               key={course.id}
               course={course}
               isEnrolled={enrolledCourses.has(course.id)}
               onEnroll={() => enrollInCourse(course.id)}
               onUnenroll={() => unenrollFromCourse(course.id)}
               userId={userId}
             />
           ))}
         </div>

         {filteredCourses.length === 0 && (
           <div className="no-results">
             <h3>No courses found</h3>
             <p>Try adjusting your filters or search terms</p>
           </div>
         )}
       </div>
     );
   };

   const CourseCard = ({ course, isEnrolled, onEnroll, onUnenroll, userId }) => {
     const getDifficultyColor = (difficulty) => {
       const colors = {
         beginner: '#27ae60',
         intermediate: '#f39c12',
         advanced: '#e74c3c'
       };
       return colors[difficulty] || '#6c757d';
     };

     const formatDuration = (hours) => {
       if (hours < 1) return `${Math.round(hours * 60)} minutes`;
       return `${hours} hour${hours !== 1 ? 's' : ''}`;
     };

     return (
       <div className="course-card">
         <div className="course-image">
           <img 
             src={course.thumbnail_url || '/default-course-image.jpg'} 
             alt={course.title}
           />
           <div className="course-difficulty" style={{ backgroundColor: getDifficultyColor(course.difficulty) }}>
             {course.difficulty}
           </div>
         </div>

         <div className="course-content">
           <h3 className="course-title">{course.title}</h3>
           <p className="course-description">{course.description}</p>

           <div className="course-meta">
             <span className="course-duration">
               ⏱️ {formatDuration(course.estimated_hours)}
             </span>
             <span className="course-lessons">
               📚 {course.lessons_count} lessons
             </span>
             <span className="course-students">
               👥 {course.enrollment_count} students
             </span>
           </div>

           <div className="course-rating">
             <div className="stars">
               {[...Array(5)].map((_, i) => (
                 <span 
                   key={i} 
                   className={i < Math.floor(course.rating) ? 'star filled' : 'star'}
                 >
                   ⭐
                 </span>
               ))}
             </div>
             <span className="rating-value">({course.rating.toFixed(1)})</span>
           </div>

           <div className="course-instructor">
             <img 
               src={course.instructor.avatar_url} 
               alt={course.instructor.name}
               className="instructor-avatar"
             />
             <span>by {course.instructor.name}</span>
           </div>
         </div>

         <div className="course-actions">
           {userId ? (
             isEnrolled ? (
               <div className="enrolled-actions">
                 <button className="btn btn-primary" onClick={() => window.location.href = `/courses/${course.id}`}>
                   Continue Learning
                 </button>
                 <button className="btn btn-outline" onClick={onUnenroll}>
                   Unenroll
                 </button>
               </div>
             ) : (
               <button className="btn btn-success" onClick={onEnroll}>
                 Enroll Now
               </button>
             )
           ) : (
             <button className="btn btn-primary" onClick={() => window.location.href = '/login'}>
               Login to Enroll
             </button>
           )}
         </div>
       </div>
     );
   };

   export default CourseCatalog;

Vue.js Integration Examples
---------------------------

Instructor Analytics Dashboard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Create a comprehensive analytics dashboard for instructors to track student progress and course performance.

.. code-block:: vue

   <!-- File: components/InstructorDashboard.vue -->
   <template>
     <div class="instructor-dashboard">
       <header class="dashboard-header">
         <h1>Instructor Dashboard</h1>
         <div class="header-stats">
           <stat-card 
             title="Total Students" 
             :value="analytics.total_students" 
             icon="👥"
             trend="+12%"
           />
           <stat-card 
             title="Active Courses" 
             :value="analytics.active_courses" 
             icon="📚"
           />
           <stat-card 
             title="Avg. Completion" 
             :value="`${analytics.avg_completion}%`" 
             icon="✅"
             :trend="analytics.completion_trend"
           />
         </div>
       </header>

       <div class="dashboard-content">
         <div class="chart-section">
           <div class="chart-container">
             <h2>Student Progress Over Time</h2>
             <line-chart :data="progressChartData" :options="chartOptions" />
           </div>
           
           <div class="chart-container">
             <h2>Course Completion Rates</h2>
             <bar-chart :data="completionChartData" :options="chartOptions" />
           </div>
         </div>

         <div class="courses-section">
           <h2>Your Courses</h2>
           <div class="courses-grid">
             <course-analytics-card 
               v-for="course in courses" 
               :key="course.id"
               :course="course"
               @view-details="viewCourseDetails"
             />
           </div>
         </div>

         <div class="students-section">
           <h2>Student Performance</h2>
           <student-performance-table 
             :students="students"
             :loading="studentsLoading"
             @export-data="exportStudentData"
           />
         </div>
       </div>
     </div>
   </template>

   <script>
   import { ref, onMounted, computed } from 'vue'
   import axios from 'axios'
   import { Line as LineChart, Bar as BarChart } from 'vue-chartjs'
   import {
     Chart as ChartJS,
     CategoryScale,
     LinearScale,
     PointElement,
     LineElement,
     BarElement,
     Title,
     Tooltip,
     Legend
   } from 'chart.js'

   ChartJS.register(
     CategoryScale,
     LinearScale,
     PointElement,
     LineElement,
     BarElement,
     Title,
     Tooltip,
     Legend
   )

   export default {
     name: 'InstructorDashboard',
     components: {
       LineChart,
       BarChart,
       StatCard,
       CourseAnalyticsCard,
       StudentPerformanceTable
     },
     props: {
       instructorId: {
         type: String,
         required: true
       }
     },
     setup(props) {
       const analytics = ref({})
       const courses = ref([])
       const students = ref([])
       const loading = ref(true)
       const studentsLoading = ref(true)

       const progressChartData = computed(() => ({
         labels: analytics.value.progress_timeline?.map(d => d.date) || [],
         datasets: [{
           label: 'Students Active',
           data: analytics.value.progress_timeline?.map(d => d.active_students) || [],
           borderColor: 'rgb(75, 192, 192)',
           backgroundColor: 'rgba(75, 192, 192, 0.2)',
           tension: 0.1
         }, {
           label: 'Lessons Completed',
           data: analytics.value.progress_timeline?.map(d => d.lessons_completed) || [],
           borderColor: 'rgb(255, 99, 132)',
           backgroundColor: 'rgba(255, 99, 132, 0.2)',
           tension: 0.1
         }]
       }))

       const completionChartData = computed(() => ({
         labels: courses.value.map(c => c.title),
         datasets: [{
           label: 'Completion Rate (%)',
           data: courses.value.map(c => c.completion_rate),
           backgroundColor: courses.value.map((_, index) => 
             `hsla(${index * 360 / courses.value.length}, 70%, 60%, 0.8)`
           )
         }]
       }))

       const chartOptions = {
         responsive: true,
         plugins: {
           legend: {
             position: 'top'
           }
         },
         scales: {
           y: {
             beginAtZero: true
           }
         }
       }

       const fetchAnalytics = async () => {
         try {
           const response = await axios.get(`/api/instructors/${props.instructorId}/analytics`)
           analytics.value = response.data
         } catch (error) {
           console.error('Failed to fetch analytics:', error)
         }
       }

       const fetchCourses = async () => {
         try {
           const response = await axios.get(`/api/instructors/${props.instructorId}/courses`)
           courses.value = response.data.courses
         } catch (error) {
           console.error('Failed to fetch courses:', error)
         }
       }

       const fetchStudents = async () => {
         try {
           studentsLoading.value = true
           const response = await axios.get(`/api/instructors/${props.instructorId}/students`)
           students.value = response.data.students
         } catch (error) {
           console.error('Failed to fetch students:', error)
         } finally {
           studentsLoading.value = false
         }
       }

       const viewCourseDetails = (courseId) => {
         // Navigate to course details page
         window.location.href = `/instructor/courses/${courseId}`
       }

       const exportStudentData = () => {
         // Export student performance data
         const csvData = students.value.map(student => ({
           name: student.name,
           email: student.email,
           progress: student.overall_progress,
           last_active: student.last_activity,
           score: student.average_score
         }))
         
         downloadCSV(csvData, 'student-performance.csv')
       }

       const downloadCSV = (data, filename) => {
         const csv = convertToCSV(data)
         const blob = new Blob([csv], { type: 'text/csv' })
         const url = window.URL.createObjectURL(blob)
         const a = document.createElement('a')
         a.href = url
         a.download = filename
         a.click()
         window.URL.revokeObjectURL(url)
       }

       const convertToCSV = (data) => {
         const headers = Object.keys(data[0]).join(',')
         const rows = data.map(row => Object.values(row).join(','))
         return [headers, ...rows].join('\n')
       }

       onMounted(async () => {
         loading.value = true
         await Promise.all([
           fetchAnalytics(),
           fetchCourses(),
           fetchStudents()
         ])
         loading.value = false
       })

       return {
         analytics,
         courses,
         students,
         loading,
         studentsLoading,
         progressChartData,
         completionChartData,
         chartOptions,
         viewCourseDetails,
         exportStudentData
       }
     }
   }
   </script>

   <style scoped>
   .instructor-dashboard {
     max-width: 1400px;
     margin: 0 auto;
     padding: 20px;
   }

   .dashboard-header {
     margin-bottom: 30px;
   }

   .dashboard-header h1 {
     color: #2c3e50;
     margin-bottom: 20px;
   }

   .header-stats {
     display: grid;
     grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
     gap: 20px;
   }

   .dashboard-content {
     display: grid;
     gap: 30px;
   }

   .chart-section {
     display: grid;
     grid-template-columns: 1fr 1fr;
     gap: 20px;
   }

   .chart-container {
     background: white;
     padding: 20px;
     border-radius: 12px;
     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
   }

   .chart-container h2 {
     margin-bottom: 15px;
     color: #2c3e50;
     font-size: 1.2rem;
   }

   .courses-grid {
     display: grid;
     grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
     gap: 20px;
   }

   @media (max-width: 768px) {
     .chart-section {
       grid-template-columns: 1fr;
     }
     
     .header-stats {
       grid-template-columns: 1fr;
     }
   }
   </style>

Angular Integration Examples
---------------------------

Real-time Learning Activity Feed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Display real-time learning activities across the platform using WebSocket connections.

.. code-block:: typescript

   // File: components/activity-feed.component.ts
   import { Component, OnInit, OnDestroy } from '@angular/core';
   import { WebSocketService } from '../services/websocket.service';
   import { ApiService } from '../services/api.service';
   import { Subscription } from 'rxjs';

   interface Activity {
     id: string;
     type: 'lesson_complete' | 'exercise_submit' | 'achievement_unlock' | 'course_enroll';
     user: {
       id: string;
       name: string;
       avatar_url: string;
     };
     data: any;
     timestamp: string;
   }

   @Component({
     selector: 'app-activity-feed',
     templateUrl: './activity-feed.component.html',
     styleUrls: ['./activity-feed.component.scss']
   })
   export class ActivityFeedComponent implements OnInit, OnDestroy {
     activities: Activity[] = [];
     private wsSubscription: Subscription = new Subscription();
     loading = true;
     error: string | null = null;

     constructor(
       private wsService: WebSocketService,
       private apiService: ApiService
     ) {}

     ngOnInit(): void {
       this.loadRecentActivities();
       this.subscribeToRealTimeUpdates();
     }

     ngOnDestroy(): void {
       this.wsSubscription.unsubscribe();
     }

     private async loadRecentActivities(): Promise<void> {
       try {
         const response = await this.apiService.get('/activities/recent');
         this.activities = response.data.activities;
         this.loading = false;
       } catch (error) {
         this.error = 'Failed to load activities';
         this.loading = false;
       }
     }

     private subscribeToRealTimeUpdates(): void {
       this.wsSubscription = this.wsService.connect('/activities/stream')
         .subscribe({
           next: (activity: Activity) => {
             this.addActivity(activity);
           },
           error: (error) => {
             console.error('WebSocket error:', error);
           }
         });
     }

     private addActivity(activity: Activity): void {
       this.activities.unshift(activity);
       
       // Keep only last 100 activities
       if (this.activities.length > 100) {
         this.activities = this.activities.slice(0, 100);
       }

       // Add visual feedback for new activity
       this.highlightNewActivity(activity.id);
     }

     private highlightNewActivity(activityId: string): void {
       setTimeout(() => {
         const element = document.getElementById(`activity-${activityId}`);
         if (element) {
           element.classList.add('new-activity');
           setTimeout(() => {
             element.classList.remove('new-activity');
           }, 3000);
         }
       }, 100);
     }

     getActivityIcon(type: string): string {
       const icons = {
         'lesson_complete': '📖',
         'exercise_submit': '💻',
         'achievement_unlock': '🏆',
         'course_enroll': '📚'
       };
       return icons[type] || '📝';
     }

     getActivityMessage(activity: Activity): string {
       const { type, data, user } = activity;
       
       switch (type) {
         case 'lesson_complete':
           return `${user.name} completed "${data.lesson_title}"`;
         case 'exercise_submit':
           return `${user.name} solved "${data.exercise_title}"`;
         case 'achievement_unlock':
           return `${user.name} earned "${data.achievement_name}" achievement`;
         case 'course_enroll':
           return `${user.name} enrolled in "${data.course_title}"`;
         default:
           return `${user.name} performed an activity`;
       }
     }

     formatTimeAgo(timestamp: string): string {
       const now = new Date();
       const time = new Date(timestamp);
       const diffInMinutes = Math.floor((now.getTime() - time.getTime()) / (1000 * 60));

       if (diffInMinutes < 1) return 'Just now';
       if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
       if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
       return `${Math.floor(diffInMinutes / 1440)}d ago`;
     }

     trackByFn(index: number, activity: Activity): string {
       return activity.id;
     }
   }

   // File: components/activity-feed.component.html
   <div class="activity-feed">
     <header class="feed-header">
       <h2>🔥 Live Activity Feed</h2>
       <p>See what's happening across the platform in real-time</p>
     </header>

     <div class="feed-content" *ngIf="!loading && !error">
       <div 
         *ngFor="let activity of activities; trackBy: trackByFn"
         [id]="'activity-' + activity.id"
         class="activity-item"
       >
         <div class="activity-avatar">
           <img [src]="activity.user.avatar_url" [alt]="activity.user.name">
         </div>
         
         <div class="activity-content">
           <div class="activity-header">
             <span class="activity-icon">{{ getActivityIcon(activity.type) }}</span>
             <span class="activity-message">{{ getActivityMessage(activity) }}</span>
           </div>
           
           <div class="activity-meta">
             <span class="activity-time">{{ formatTimeAgo(activity.timestamp) }}</span>
             <span class="activity-type">{{ activity.type.replace('_', ' ') | titlecase }}</span>
           </div>
           
           <!-- Activity-specific details -->
           <div class="activity-details" [ngSwitch]="activity.type">
             <div *ngSwitchCase="'exercise_submit'" class="exercise-details">
               <span class="score-badge" [class.passed]="activity.data.passed">
                 Score: {{ activity.data.score }}%
               </span>
             </div>
             
             <div *ngSwitchCase="'achievement_unlock'" class="achievement-details">
               <div class="achievement-badge">
                 <span class="badge-icon">{{ activity.data.achievement_icon }}</span>
                 <span class="badge-tier">{{ activity.data.achievement_tier | titlecase }}</span>
               </div>
             </div>
           </div>
         </div>
         
         <div class="activity-actions">
           <button 
             class="btn-link"
             (click)="viewActivity(activity)"
             title="View details"
           >
             👁️
           </button>
         </div>
       </div>
     </div>

     <div class="loading-state" *ngIf="loading">
       <div class="spinner"></div>
       <p>Loading activities...</p>
     </div>

     <div class="error-state" *ngIf="error">
       <p>{{ error }}</p>
       <button class="btn btn-primary" (click)="loadRecentActivities()">
         Try Again
       </button>
     </div>

     <div class="empty-state" *ngIf="!loading && !error && activities.length === 0">
       <p>No recent activities to show</p>
     </div>
   </div>

   // File: components/activity-feed.component.scss
   .activity-feed {
     max-width: 600px;
     margin: 0 auto;
     background: white;
     border-radius: 12px;
     box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
     overflow: hidden;
   }

   .feed-header {
     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
     color: white;
     padding: 20px;
     text-align: center;

     h2 {
       margin: 0 0 5px 0;
       font-size: 1.5rem;
     }

     p {
       margin: 0;
       opacity: 0.9;
       font-size: 0.9rem;
     }
   }

   .feed-content {
     max-height: 500px;
     overflow-y: auto;
   }

   .activity-item {
     display: flex;
     align-items: flex-start;
     padding: 15px 20px;
     border-bottom: 1px solid #e9ecef;
     transition: all 0.3s ease;

     &:hover {
       background-color: #f8f9fa;
     }

     &.new-activity {
       background-color: #e3f2fd;
       animation: highlightFade 3s ease-out;
     }

     &:last-child {
       border-bottom: none;
     }
   }

   @keyframes highlightFade {
     0% { background-color: #bbdefb; }
     100% { background-color: transparent; }
   }

   .activity-avatar {
     margin-right: 12px;

     img {
       width: 40px;
       height: 40px;
       border-radius: 50%;
       object-fit: cover;
     }
   }

   .activity-content {
     flex: 1;
   }

   .activity-header {
     display: flex;
     align-items: center;
     margin-bottom: 5px;
   }

   .activity-icon {
     margin-right: 8px;
     font-size: 1.2rem;
   }

   .activity-message {
     font-weight: 500;
     color: #2c3e50;
   }

   .activity-meta {
     display: flex;
     gap: 10px;
     font-size: 0.8rem;
     color: #6c757d;
     margin-bottom: 8px;
   }

   .activity-details {
     margin-top: 8px;
   }

   .score-badge {
     display: inline-block;
     padding: 2px 8px;
     border-radius: 12px;
     font-size: 0.75rem;
     background-color: #dc3545;
     color: white;

     &.passed {
       background-color: #28a745;
     }
   }

   .achievement-badge {
     display: flex;
     align-items: center;
     gap: 5px;
     padding: 4px 8px;
     background-color: #ffeaa7;
     border-radius: 8px;
     display: inline-flex;

     .badge-icon {
       font-size: 0.9rem;
     }

     .badge-tier {
       font-size: 0.75rem;
       font-weight: 500;
       color: #d63031;
     }
   }

   .activity-actions {
     margin-left: 10px;
   }

   .btn-link {
     background: none;
     border: none;
     cursor: pointer;
     opacity: 0.6;
     transition: opacity 0.2s ease;

     &:hover {
       opacity: 1;
     }
   }

   .loading-state,
   .error-state,
   .empty-state {
     padding: 40px 20px;
     text-align: center;
     color: #6c757d;
   }

   .spinner {
     width: 40px;
     height: 40px;
     border: 4px solid #e9ecef;
     border-top: 4px solid #007bff;
     border-radius: 50%;
     animation: spin 1s linear infinite;
     margin: 0 auto 10px;
   }

   @keyframes spin {
     0% { transform: rotate(0deg); }
     100% { transform: rotate(360deg); }
   }

Vanilla JavaScript Examples
---------------------------

Embeddable Learning Widget
~~~~~~~~~~~~~~~~~~~~~~~~~

**Use Case**: Create a lightweight widget that can be embedded on any website to showcase Python Mastery Hub courses.

.. code-block:: html

   <!-- File: embeddable-widget.html -->
   <!DOCTYPE html>
   <html>
   <head>
     <meta charset="UTF-8">
     <title>PMH Learning Widget</title>
     <style>
       .pmh-widget {
         font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         max-width: 400px;
         border: 1px solid #e1e5e9;
         border-radius: 12px;
         overflow: hidden;
         box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
         background: white;
       }

       .pmh-widget-header {
         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
         color: white;
         padding: 16px;
         text-align: center;
       }

       .pmh-widget-header h3 {
         margin: 0 0 4px 0;
         font-size: 1.2rem;
         font-weight: 600;
       }

       .pmh-widget-header p {
         margin: 0;
         opacity: 0.9;
         font-size: 0.9rem;
       }

       .pmh-widget-content {
         padding: 0;
       }

       .pmh-course-item {
         display: flex;
         align-items: center;
         padding: 12px 16px;
         border-bottom: 1px solid #f1f3f4;
         text-decoration: none;
         color: inherit;
         transition: background-color 0.2s ease;
       }

       .pmh-course-item:hover {
         background-color: #f8f9fa;
       }

       .pmh-course-item:last-child {
         border-bottom: none;
       }

       .pmh-course-icon {
         width: 40px;
         height: 40px;
         background: #e3f2fd;
         border-radius: 8px;
         display: flex;
         align-items: center;
         justify-content: center;
         margin-right: 12px;
         font-size: 1.2rem;
       }

       .pmh-course-info {
         flex: 1;
       }

       .pmh-course-title {
         font-weight: 500;
         color: #2c3e50;
         margin: 0 0 2px 0;
         font-size: 0.9rem;
       }

       .pmh-course-meta {
         font-size: 0.75rem;
         color: #6c757d;
       }

       .pmh-course-difficulty {
         padding: 2px 6px;
         border-radius: 8px;
         font-size: 0.7rem;
         font-weight: 500;
       }

       .pmh-course-difficulty.beginner {
         background-color: #d4edda;
         color: #155724;
       }

       .pmh-course-difficulty.intermediate {
         background-color: #fff3cd;
         color: #856404;
       }

       .pmh-course-difficulty.advanced {
         background-color: #f8d7da;
         color: #721c24;
       }

       .pmh-widget-footer {
         padding: 12px 16px;
         background-color: #f8f9fa;
         text-align: center;
       }

       .pmh-cta-button {
         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
         color: white;
         padding: 8px 16px;
         border: none;
         border-radius: 6px;
         font-size: 0.85rem;
         font-weight: 500;
         text-decoration: none;
         display: inline-block;
         transition: transform 0.2s ease;
       }

       .pmh-cta-button:hover {
         transform: translateY(-1px);
         color: white;
         text-decoration: none;
       }

       .pmh-loading {
         text-align: center;
         padding: 40px 16px;
         color: #6c757d;
       }

       .pmh-error {
         text-align: center;
         padding: 20px 16px;
         color: #dc3545;
       }
     </style>
   </head>
   <body>
     <div id="pmh-widget-container"></div>

     <script>
       (function() {
         'use strict';

         class PMHWidget {
           constructor(containerId, options = {}) {
             this.container = document.getElementById(containerId);
             this.options = {
               apiKey: options.apiKey || '',
               baseURL: options.baseURL || 'https://api.pythonmasteryhub.com/v1',
               limit: options.limit || 5,
               difficulty: options.difficulty || '',
               category: options.category || '',
               title: options.title || 'Learn Python Programming',
               subtitle: options.subtitle || 'Interactive courses and exercises'
             };
             
             this.init();
           }

           async init() {
             this.showLoading();
             
             try {
               const courses = await this.fetchCourses();
               this.render(courses);
             } catch (error) {
               this.showError('Failed to load courses');
               console.error('PMH Widget Error:', error);
             }
           }

           showLoading() {
             this.container.innerHTML = `
               <div class="pmh-widget">
                 <div class="pmh-widget-header">
                   <h3>${this.options.title}</h3>
                   <p>${this.options.subtitle}</p>
                 </div>
                 <div class="pmh-loading">
                   <div>Loading courses...</div>
                 </div>
               </div>
             `;
           }

           showError(message) {
             this.container.innerHTML = `
               <div class="pmh-widget">
                 <div class="pmh-widget-header">
                   <h3>${this.options.title}</h3>
                   <p>${this.options.subtitle}</p>
                 </div>
                 <div class="pmh-error">
                   <div>${message}</div>
                 </div>
               </div>
             `;
           }

           async fetchCourses() {
             const params = new URLSearchParams({
               limit: this.options.limit,
               ...(this.options.difficulty && { difficulty: this.options.difficulty }),
               ...(this.options.category && { category: this.options.category })
             });

             const response = await fetch(`${this.options.baseURL}/courses?${params}`, {
               headers: {
                 ...(this.options.apiKey && { 'Authorization': `Bearer ${this.options.apiKey}` })
               }
             });

             if (!response.ok) {
               throw new Error(`HTTP ${response.status}: ${response.statusText}`);
             }

             const data = await response.json();
             return data.data?.courses || data.courses || [];
           }

           render(courses) {
             const coursesHTML = courses.map(course => `
               <a href="${this.getCourseURL(course)}" class="pmh-course-item" target="_blank">
                 <div class="pmh-course-icon">
                   ${this.getCourseIcon(course.category)}
                 </div>
                 <div class="pmh-course-info">
                   <div class="pmh-course-title">${this.escapeHTML(course.title)}</div>
                   <div class="pmh-course-meta">
                     <span class="pmh-course-difficulty ${course.difficulty}">
                       ${course.difficulty}
                     </span>
                     • ${course.estimated_hours}h
                     • ${course.lessons_count} lessons
                   </div>
                 </div>
               </a>
             `).join('');

             this.container.innerHTML = `
               <div class="pmh-widget">
                 <div class="pmh-widget-header">
                   <h3>${this.options.title}</h3>
                   <p>${this.options.subtitle}</p>
                 </div>
                 <div class="pmh-widget-content">
                   ${coursesHTML}
                 </div>
                 <div class="pmh-widget-footer">
                   <a href="https://pythonmasteryhub.com" class="pmh-cta-button" target="_blank">
                     Explore All Courses →
                   </a>
                 </div>
               </div>
             `;
           }

           getCourseURL(course) {
             return `https://pythonmasteryhub.com/courses/${course.id}`;
           }

           getCourseIcon(category) {
             const icons = {
               'fundamentals': '🐍',
               'web-development': '🌐',
               'data-science': '📊',
               'automation': '🤖',
               'algorithms': '🧮'
             };
             return icons[category] || '📚';
           }

           escapeHTML(text) {
             const div = document.createElement('div');
             div.textContent = text;
             return div.innerHTML;
           }
         }

         // Auto-initialize widgets
         document.addEventListener('DOMContentLoaded', function() {
           const widgetElements = document.querySelectorAll('[data-pmh-widget]');
           
           widgetElements.forEach(element => {
             const options = {
               apiKey: element.dataset.apiKey,
               limit: parseInt(element.dataset.limit) || 5,
               difficulty: element.dataset.difficulty,
               category: element.dataset.category,
               title: element.dataset.title,
               subtitle: element.dataset.subtitle
             };

             new PMHWidget(element.id, options);
           });
         });

         // Export for manual initialization
         window.PMHWidget = PMHWidget;
       })();
     </script>
   </body>
   </html>

**Usage Examples**:

.. code-block:: html

   <!-- Basic widget -->
   <div id="pmh-widget-1" data-pmh-widget></div>

   <!-- Customized widget -->
   <div 
     id="pmh-widget-2" 
     data-pmh-widget
     data-limit="3"
     data-difficulty="beginner"
     data-title="Start Learning Python"
     data-subtitle="Perfect for beginners"
   ></div>

   <!-- Manual initialization -->
   <div id="custom-widget"></div>
   <script>
     new PMHWidget('custom-widget', {
       limit: 4,
       category: 'web-development',
       title: 'Web Development with Python'
     });
   </script>

Backend Integration Examples
---------------------------

Flask Integration
~~~~~~~~~~~~~~~~

**Use Case**: Integrate Python Mastery Hub with an existing Flask application for single sign-on and progress tracking.

.. code-block:: python

   # File: app.py
   from flask import Flask, render_template, request, redirect, session, jsonify
   import requests
   import os
   from functools import wraps

   app = Flask(__name__)
   app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key')

   # PMH API Configuration
   PMH_API_BASE = os.getenv('PMH_API_BASE', 'https://api.pythonmasteryhub.com/v1')
   PMH_API_KEY = os.getenv('PMH_API_KEY')

   class PMHClient:
       def __init__(self, api_key, base_url):
           self.api_key = api_key
           self.base_url = base_url
           self.session = requests.Session()
           self.session.headers.update({
               'Authorization': f'Bearer {api_key}',
               'Content-Type': 'application/json'
           })

       def get(self, endpoint, params=None):
           response = self.session.get(f"{self.base_url}{endpoint}", params=params)
           response.raise_for_status()
           return response.json()

       def post(self, endpoint, data=None):
           response = self.session.post(f"{self.base_url}{endpoint}", json=data)
           response.raise_for_status()
           return response.json()

   pmh_client = PMHClient(PMH_API_KEY, PMH_API_BASE)

   def require_auth(f):
       @wraps(f)
       def decorated_function(*args, **kwargs):
           if 'user_id' not in session:
               return redirect('/login')
           return f(*args, **kwargs)
       return decorated_function

   @app.route('/')
   def index():
       if 'user_id' in session:
           return redirect('/dashboard')
       return render_template('index.html')

   @app.route('/login', methods=['GET', 'POST'])
   def login():
       if request.method == 'POST':
           username = request.form['username']
           password = request.form['password']
           
           try:
               # Authenticate with PMH
               auth_response = pmh_client.post('/auth/login', {
                   'username': username,
                   'password': password
               })
               
               # Store user info in session
               user_data = auth_response['data']
               session['user_id'] = user_data['user']['id']
               session['username'] = user_data['user']['username']
               session['pmh_token'] = user_data['access_token']
               
               return redirect('/dashboard')
               
           except requests.exceptions.HTTPError as e:
               error_message = 'Invalid username or password'
               return render_template('login.html', error=error_message)
       
       return render_template('login.html')

   @app.route('/dashboard')
   @require_auth
   def dashboard():
       try:
           # Fetch user progress from PMH
           user_id = session['user_id']
           progress_data = pmh_client.get(f'/users/{user_id}/progress')
           
           # Fetch enrolled courses
           courses_data = pmh_client.get(f'/users/{user_id}/courses')
           
           # Fetch recent achievements
           achievements_data = pmh_client.get(f'/users/{user_id}/achievements/recent')
           
           return render_template('dashboard.html',
               progress=progress_data['data'],
               courses=courses_data['data'],
               achievements=achievements_data['data']
           )
           
       except requests.exceptions.RequestException as e:
           return render_template('error.html', 
               error='Failed to load dashboard data')

   @app.route('/courses')
   @require_auth
   def courses():
       try:
           courses_data = pmh_client.get('/courses')
           user_enrollments = pmh_client.get(f'/users/{session["user_id"]}/enrollments')
           
           enrolled_course_ids = {e['course_id'] for e in user_enrollments['data']}
           
           return render_template('courses.html',
               courses=courses_data['data'],
               enrolled_course_ids=enrolled_course_ids
           )
           
       except requests.exceptions.RequestException as e:
           return render_template('error.html', 
               error='Failed to load courses')

   @app.route('/api/enroll/<int:course_id>', methods=['POST'])
   @require_auth
   def enroll_course(course_id):
       try:
           enrollment_data = pmh_client.post(f'/courses/{course_id}/enroll')
           return jsonify({'success': True, 'data': enrollment_data['data']})
           
       except requests.exceptions.HTTPError as e:
           return jsonify({'success': False, 'error': 'Failed to enroll'}), 400

   @app.route('/api/progress')
   @require_auth
   def api_progress():
       try:
           user_id = session['user_id']
           progress_data = pmh_client.get(f'/users/{user_id}/analytics')
           return jsonify(progress_data)
           
       except requests.exceptions.RequestException as e:
           return jsonify({'error': 'Failed to fetch progress'}), 500

   @app.route('/logout')
   def logout():
       session.clear()
       return redirect('/')

   if __name__ == '__main__':
       app.run(debug=True)

**Templates** (Jinja2):

.. code-block:: html

   <!-- File: templates/dashboard.html -->
   <!DOCTYPE html>
   <html>
   <head>
       <title>Learning Dashboard</title>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
       <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
   </head>
   <body>
       <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
           <div class="container">
               <a class="navbar-brand" href="/">Learning Platform</a>
               <div class="navbar-nav ms-auto">
                   <a class="nav-link" href="/courses">Courses</a>
                   <a class="nav-link" href="/logout">Logout</a>
               </div>
           </div>
       </nav>

       <div class="container mt-4">
           <div class="row">
               <div class="col-12">
                   <h1>Welcome back, {{ session.username }}!</h1>
               </div>
           </div>

           <div class="row mt-4">
               <div class="col-md-3">
                   <div class="card text-center">
                       <div class="card-body">
                           <h5 class="card-title">{{ progress.total_xp }}</h5>
                           <p class="card-text">Total XP</p>
                       </div>
                   </div>
               </div>
               <div class="col-md-3">
                   <div class="card text-center">
                       <div class="card-body">
                           <h5 class="card-title">{{ progress.current_level }}</h5>
                           <p class="card-text">Current Level</p>
                       </div>
                   </div>
               </div>
               <div class="col-md-3">
                   <div class="card text-center">
                       <div class="card-body">
                           <h5 class="card-title">{{ progress.current_streak }}</h5>
                           <p class="card-text">Day Streak</p>
                       </div>
                   </div>
               </div>
               <div class="col-md-3">
                   <div class="card text-center">
                       <div class="card-body">
                           <h5 class="card-title">{{ progress.courses_completed }}</h5>
                           <p class="card-text">Courses Completed</p>
                       </div>
                   </div>
               </div>
           </div>

           <div class="row mt-4">
               <div class="col-md-8">
                   <div class="card">
                       <div class="card-header">
                           <h5>Course Progress</h5>
                       </div>
                       <div class="card-body">
                           {% for course in courses.courses %}
                           <div class="mb-3">
                               <div class="d-flex justify-content-between">
                                   <span>{{ course.title }}</span>
                                   <span>{{ course.progress }}%</span>
                               </div>
                               <div class="progress">
                                   <div class="progress-bar" style="width: {{ course.progress }}%"></div>
                               </div>
                           </div>
                           {% endfor %}
                       </div>
                   </div>
               </div>
               
               <div class="col-md-4">
                   <div class="card">
                       <div class="card-header">
                           <h5>Recent Achievements</h5>
                       </div>
                       <div class="card-body">
                           {% for achievement in achievements.achievements %}
                           <div class="d-flex align-items-center mb-2">
                               <span class="me-2">{{ achievement.icon }}</span>
                               <div>
                                   <strong>{{ achievement.name }}</strong>
                                   <br>
                                   <small class="text-muted">{{ achievement.unlocked_at }}</small>
                               </div>
                           </div>
                           {% endfor %}
                       </div>
                   </div>
               </div>
           </div>
       </div>

       <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
   </body>
   </html>

Best Practices and Tips
----------------------

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~

1. **API Caching**: Cache frequently accessed data to reduce API calls
2. **Lazy Loading**: Load content on-demand to improve initial page load
3. **Code Splitting**: Split JavaScript bundles for better performance
4. **Image Optimization**: Optimize images and use appropriate formats
5. **CDN Usage**: Use CDNs for static assets and libraries

Security Considerations
~~~~~~~~~~~~~~~~~~~~~~

1. **API Key Security**: Never expose API keys in client-side code
2. **Input Validation**: Validate all user inputs before API calls
3. **HTTPS Only**: Always use HTTPS for API communications
4. **CORS Configuration**: Properly configure CORS for cross-origin requests
5. **Rate Limiting**: Implement client-side rate limiting to avoid hitting API limits

User Experience Best Practices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Loading States**: Show loading indicators during API calls
2. **Error Handling**: Provide meaningful error messages and recovery options
3. **Responsive Design**: Ensure compatibility across all device sizes
4. **Accessibility**: Follow WCAG guidelines for accessibility
5. **Progressive Enhancement**: Ensure basic functionality works without JavaScript

Common Troubleshooting
~~~~~~~~~~~~~~~~~~~~~

**CORS Issues:**

.. code-block:: javascript

   // If you encounter CORS issues, ensure your API calls include proper headers
   const response = await fetch(url, {
     method: 'GET',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': `Bearer ${apiKey}`
     },
     mode: 'cors'
   });

**Authentication Errors:**

.. code-block:: javascript

   // Implement token refresh logic
   const refreshToken = async () => {
     try {
       const response = await fetch('/api/auth/refresh', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ refresh_token: localStorage.getItem('refreshToken') })
       });
       
       if (response.ok) {
         const data = await response.json();
         localStorage.setItem('accessToken', data.access_token);
         return data.access_token;
       }
     } catch (error) {
       // Redirect to login
       window.location.href = '/login';
     }
   };

Getting Help
-----------

- **Documentation**: :doc:`../api/web` for complete Web API reference
- **Examples Repository**: GitHub repository with more web integration examples
- **Community**: Discord #web-development channel for assistance
- **Support**: Enterprise customers get priority web integration support

.. admonition:: Build Amazing Experiences! 🌟
   :class: tip

   The web examples provided here are starting points for creating engaging 
   learning experiences. Customize them to match your design system and user 
   needs. Remember to test across different browsers and devices for the best 
   user experience!