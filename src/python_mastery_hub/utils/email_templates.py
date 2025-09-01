# src/python_mastery_hub/utils/email_templates.py
"""
Email Template Management - Dynamic Email Generation

Provides email template management for various user communications including
welcome emails, progress reports, achievement notifications, and reminders.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from string import Template
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EmailTemplate:
    """Represents an email template."""
    id: str
    name: str
    subject_template: str
    html_template: str
    text_template: str
    variables: List[str]
    category: str
    description: Optional[str] = None
    tags: List[str] = None


class EmailTemplateManager:
    """Manages email templates and rendering."""
    
    def __init__(self, template_dir: Optional[Path] = None):
        self.template_dir = template_dir or Path(__file__).parent / 'email_templates'
        self.template_dir.mkdir(exist_ok=True)
        self.templates: Dict[str, EmailTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self) -> None:
        """Load default email templates."""
        
        # Welcome Email
        self.register_template(EmailTemplate(
            id='welcome',
            name='Welcome Email',
            subject_template='Welcome to Python Mastery Hub, ${user_name}!',
            html_template=self._get_welcome_html_template(),
            text_template=self._get_welcome_text_template(),
            variables=['user_name', 'user_email', 'platform_url'],
            category='onboarding',
            description='Welcome email for new users',
            tags=['welcome', 'onboarding']
        ))
        
        # Progress Report
        self.register_template(EmailTemplate(
            id='progress_report',
            name='Weekly Progress Report',
            subject_template='Your Python Learning Progress - Week of ${week_start}',
            html_template=self._get_progress_report_html_template(),
            text_template=self._get_progress_report_text_template(),
            variables=[
                'user_name', 'week_start', 'week_end', 'topics_completed',
                'total_study_time', 'current_streak', 'achievements_earned',
                'next_milestone', 'progress_percentage'
            ],
            category='progress',
            description='Weekly progress summary email',
            tags=['progress', 'weekly', 'report']
        ))
        
        # Achievement Notification
        self.register_template(EmailTemplate(
            id='achievement_notification',
            name='Achievement Unlocked',
            subject_template='🏆 Achievement Unlocked: ${achievement_name}',
            html_template=self._get_achievement_html_template(),
            text_template=self._get_achievement_text_template(),
            variables=[
                'user_name', 'achievement_name', 'achievement_description',
                'achievement_badge', 'achievement_points', 'total_points'
            ],
            category='achievement',
            description='Notification for earned achievements',
            tags=['achievement', 'notification', 'gamification']
        ))
        
        # Learning Reminder
        self.register_template(EmailTemplate(
            id='learning_reminder',
            name='Learning Reminder',
            subject_template='Don\'t break your streak! Continue your Python journey',
            html_template=self._get_reminder_html_template(),
            text_template=self._get_reminder_text_template(),
            variables=[
                'user_name', 'days_since_last_activity', 'current_streak',
                'suggested_topic', 'estimated_time', 'next_module'
            ],
            category='reminder',
            description='Reminder to continue learning',
            tags=['reminder', 'engagement', 'streak']
        ))
        
        # Course Completion
        self.register_template(EmailTemplate(
            id='course_completion',
            name='Course Completion Celebration',
            subject_template='🎉 Congratulations! You completed ${module_name}',
            html_template=self._get_completion_html_template(),
            text_template=self._get_completion_text_template(),
            variables=[
                'user_name', 'module_name', 'completion_date', 'total_time',
                'topics_completed', 'final_score', 'next_recommended_module',
                'certificate_url'
            ],
            category='completion',
            description='Module/course completion celebration',
            tags=['completion', 'celebration', 'certificate']
        ))
        
        # Streak Milestone
        self.register_template(EmailTemplate(
            id='streak_milestone',
            name='Streak Milestone Achieved',
            subject_template='🔥 Amazing! ${streak_days}-day learning streak achieved!',
            html_template=self._get_streak_milestone_html_template(),
            text_template=self._get_streak_milestone_text_template(),
            variables=[
                'user_name', 'streak_days', 'milestone_type', 'total_topics',
                'total_time', 'next_milestone', 'encouragement_message'
            ],
            category='milestone',
            description='Learning streak milestone notification',
            tags=['streak', 'milestone', 'motivation']
        ))
    
    def register_template(self, template: EmailTemplate) -> None:
        """Register a new email template."""
        self.templates[template.id] = template
        logger.debug(f"Registered email template: {template.id}")
    
    def get_template(self, template_id: str) -> Optional[EmailTemplate]:
        """Get template by ID."""
        return self.templates.get(template_id)
    
    def list_templates(self, category: Optional[str] = None) -> List[EmailTemplate]:
        """List all templates, optionally filtered by category."""
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        return templates
    
    def render_email(
        self, 
        template_id: str, 
        variables: Dict[str, Any],
        format_type: str = 'html'
    ) -> Dict[str, str]:
        """
        Render email template with variables.
        
        Args:
            template_id: ID of template to render
            variables: Variables to substitute
            format_type: 'html', 'text', or 'both'
            
        Returns:
            Dictionary with rendered email content
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Prepare variables with defaults
        render_vars = self._prepare_variables(variables)
        
        # Render subject
        subject = Template(template.subject_template).safe_substitute(render_vars)
        
        result = {'subject': subject}
        
        # Render body based on format type
        if format_type in ('html', 'both'):
            html_body = Template(template.html_template).safe_substitute(render_vars)
            result['html_body'] = html_body
        
        if format_type in ('text', 'both'):
            text_body = Template(template.text_template).safe_substitute(render_vars)
            result['text_body'] = text_body
        
        return result
    
    def _prepare_variables(self, variables: Dict[str, Any]) -> Dict[str, str]:
        """Prepare variables for template rendering."""
        # Convert all values to strings and add default values
        render_vars = {}
        
        for key, value in variables.items():
            if isinstance(value, datetime):
                render_vars[key] = value.strftime('%B %d, %Y')
            elif isinstance(value, (list, dict)):
                render_vars[key] = str(value)
            else:
                render_vars[key] = str(value) if value is not None else ''
        
        # Add current date/time
        now = datetime.now()
        render_vars.update({
            'current_date': now.strftime('%B %d, %Y'),
            'current_year': str(now.year),
            'platform_name': 'Python Mastery Hub',
            'support_email': 'support@pythonmasteryhub.com',
            'unsubscribe_url': 'https://pythonmasteryhub.com/unsubscribe',
            'platform_url': 'https://pythonmasteryhub.com'
        })
        
        return render_vars
    
    # Template definitions
    def _get_welcome_html_template(self) -> str:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to Python Mastery Hub</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #2E86AB; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9f9f9; }
                .button { display: inline-block; background: #2E86AB; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
                .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Python Mastery Hub!</h1>
                </div>
                <div class="content">
                    <h2>Hello ${user_name},</h2>
                    <p>Welcome to your Python learning journey! We're excited to have you join our community of Python enthusiasts.</p>
                    
                    <h3>What's Next?</h3>
                    <ul>
                        <li>Complete your profile setup</li>
                        <li>Take the skills assessment</li>
                        <li>Start with Python Basics</li>
                        <li>Set your learning goals</li>
                    </ul>
                    
                    <p>Ready to begin? Click the button below to start learning!</p>
                    <p><a href="${platform_url}/dashboard" class="button">Start Learning Now</a></p>
                    
                    <p>If you have any questions, our support team is here to help at ${support_email}.</p>
                    
                    <p>Happy coding!<br>The Python Mastery Hub Team</p>
                </div>
                <div class="footer">
                    <p>&copy; ${current_year} ${platform_name}. All rights reserved.</p>
                    <p><a href="${unsubscribe_url}">Unsubscribe</a></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_welcome_text_template(self) -> str:
        return """
        Welcome to Python Mastery Hub!
        
        Hello ${user_name},
        
        Welcome to your Python learning journey! We're excited to have you join our community of Python enthusiasts.
        
        What's Next?
        - Complete your profile setup
        - Take the skills assessment  
        - Start with Python Basics
        - Set your learning goals
        
        Ready to begin? Visit ${platform_url}/dashboard to start learning!
        
        If you have any questions, our support team is here to help at ${support_email}.
        
        Happy coding!
        The Python Mastery Hub Team
        
        --
        © ${current_year} ${platform_name}. All rights reserved.
        Unsubscribe: ${unsubscribe_url}
        """
    
    def _get_progress_report_html_template(self) -> str:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Your Weekly Progress Report</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #27AE60; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9f9f9; }
                .stat-box { background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #27AE60; }
                .progress-bar { background: #ddd; height: 20px; border-radius: 10px; overflow: hidden; }
                .progress-fill { background: #27AE60; height: 100%; transition: width 0.3s; }
                .achievement { background: #FFF3CD; border: 1px solid #FFE69C; padding: 10px; margin: 10px 0; border-radius: 5px; }
                .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Your Learning Progress</h1>
                    <p>Week of ${week_start} - ${week_end}</p>
                </div>
                <div class="content">
                    <h2>Hello ${user_name},</h2>
                    
                    <p>Here's your learning progress for this week:</p>
                    
                    <div class="stat-box">
                        <h3>📚 Topics Completed</h3>
                        <p><strong>${topics_completed}</strong> topics this week</p>
                    </div>
                    
                    <div class="stat-box">
                        <h3>⏱️ Study Time</h3>
                        <p><strong>${total_study_time}</strong> total this week</p>
                    </div>
                    
                    <div class="stat-box">
                        <h3>🔥 Current Streak</h3>
                        <p><strong>${current_streak}</strong> days of consistent learning</p>
                    </div>
                    
                    <div class="stat-box">
                        <h3>📈 Overall Progress</h3>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${progress_percentage}%;"></div>
                        </div>
                        <p>${progress_percentage}% complete</p>
                    </div>
                    
                    ${achievements_earned}
                    
                    <div class="stat-box">
                        <h3>🎯 Next Milestone</h3>
                        <p>${next_milestone}</p>
                    </div>
                    
                    <p>Keep up the excellent work! Your dedication to learning Python is impressive.</p>
                </div>
                <div class="footer">
                    <p>&copy; ${current_year} ${platform_name}. All rights reserved.</p>
                    <p><a href="${unsubscribe_url}">Unsubscribe</a></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_progress_report_text_template(self) -> str:
        return """
        Your Learning Progress Report
        Week of ${week_start} - ${week_end}
        
        Hello ${user_name},
        
        Here's your learning progress for this week:
        
        📚 Topics Completed: ${topics_completed} topics this week
        ⏱️ Study Time: ${total_study_time} total this week
        🔥 Current Streak: ${current_streak} days of consistent learning
        📈 Overall Progress: ${progress_percentage}% complete
        
        ${achievements_earned}
        
        🎯 Next Milestone: ${next_milestone}
        
        Keep up the excellent work! Your dedication to learning Python is impressive.
        
        --
        © ${current_year} ${platform_name}. All rights reserved.
        Unsubscribe: ${unsubscribe_url}
        """
    
    def _get_achievement_html_template(self) -> str:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Achievement Unlocked!</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #F39C12; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9f9f9; text-align: center; }
                .achievement-box { background: white; padding: 30px; margin: 20px 0; border-radius: 10px; border: 3px solid #F39C12; }
                .badge { font-size: 48px; margin: 10px 0; }
                .points { background: #F39C12; color: white; padding: 5px 15px; border-radius: 20px; display: inline-block; margin: 10px 0; }
                .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏆 Achievement Unlocked!</h1>
                </div>
                <div class="content">
                    <h2>Congratulations ${user_name}!</h2>
                    
                    <div class="achievement-box">
                        <div class="badge">${achievement_badge}</div>
                        <h3>${achievement_name}</h3>
                        <p>${achievement_description}</p>
                        <div class="points">+${achievement_points} points</div>
                    </div>
                    
                    <p>You now have <strong>${total_points}</strong> total achievement points!</p>
                    
                    <p>Your dedication to learning is paying off. Keep pushing forward on your Python journey!</p>
                </div>
                <div class="footer">
                    <p>&copy; ${current_year} ${platform_name}. All rights reserved.</p>
                    <p><a href="${unsubscribe_url}">Unsubscribe</a></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_achievement_text_template(self) -> str:
        return """
        🏆 Achievement Unlocked!
        
        Congratulations ${user_name}!
        
        ${achievement_badge} ${achievement_name}
        ${achievement_description}
        
        +${achievement_points} points earned!
        Total points: ${total_points}
        
        Your dedication to learning is paying off. Keep pushing forward on your Python journey!
        
        --
        © ${current_year} ${platform_name}. All rights reserved.
        Unsubscribe: ${unsubscribe_url}
        """
    
    def _get_reminder_html_template(self) -> str:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Continue Your Python Journey</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #E74C3C; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9f9f9; }
                .suggestion-box { background: white; padding: 20px; margin: 15px 0; border-left: 4px solid #E74C3C; }
                .button { display: inline-block; background: #E74C3C; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
                .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Missing You!</h1>
                    <p>Don't let your streak break</p>
                </div>
                <div class="content">
                    <h2>Hi ${user_name},</h2>
                    
                    <p>It's been ${days_since_last_activity} days since your last learning session. Your current ${current_streak}-day streak is waiting for you!</p>
                    
                    <div class="suggestion-box">
                        <h3>Quick Learning Suggestion</h3>
                        <p><strong>Topic:</strong> ${suggested_topic}</p>
                        <p><strong>Estimated Time:</strong> ${estimated_time}</p>
                        <p>Perfect for a quick session to keep your momentum going!</p>
                    </div>
                    
                    <p>Or continue with your next module: <strong>${next_module}</strong></p>
                    
                    <p><a href="${platform_url}/learn" class="button">Continue Learning</a></p>
                    
                    <p>Remember, consistency is key to mastering Python. Even 10 minutes a day makes a difference!</p>
                </div>
                <div class="footer">
                    <p>&copy; ${current_year} ${platform_name}. All rights reserved.</p>
                    <p><a href="${unsubscribe_url}">Unsubscribe</a></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_reminder_text_template(self) -> str:
        return """
        Missing You! Don't let your streak break
        
        Hi ${user_name},
        
        It's been ${days_since_last_activity} days since your last learning session. Your current ${current_streak}-day streak is waiting for you!
        
        Quick Learning Suggestion:
        Topic: ${suggested_topic}
        Estimated Time: ${estimated_time}
        
        Perfect for a quick session to keep your momentum going!
        
        Or continue with your next module: ${next_module}
        
        Continue Learning: ${platform_url}/learn
        
        Remember, consistency is key to mastering Python. Even 10 minutes a day makes a difference!
        
        --
        © ${current_year} ${platform_name}. All rights reserved.
        Unsubscribe: ${unsubscribe_url}
        """
    
    def _get_completion_html_template(self) -> str:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Module Complete!</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #8E44AD; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9f9f9; text-align: center; }
                .completion-box { background: white; padding: 30px; margin: 20px 0; border-radius: 10px; border: 3px solid #8E44AD; }
                .stats { display: flex; justify-content: space-around; margin: 20px 0; }
                .stat { background: white; padding: 15px; border-radius: 8px; }
                .button { display: inline-block; background: #8E44AD; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; margin: 10px; }
                .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Congratulations!</h1>
                    <p>You completed ${module_name}!</p>
                </div>
                <div class="content">
                    <h2>Amazing work, ${user_name}!</h2>
                    
                    <div class="completion-box">
                        <h3>${module_name}</h3>
                        <p>Completed on ${completion_date}</p>
                        
                        <div class="stats">
                            <div class="stat">
                                <strong>${total_time}</strong><br>
                                Total Time
                            </div>
                            <div class="stat">
                                <strong>${topics_completed}</strong><br>
                                Topics Mastered
                            </div>
                            <div class="stat">
                                <strong>${final_score}%</strong><br>
                                Final Score
                            </div>
                        </div>
                    </div>
                    
                    <p>You've made significant progress in your Python journey!</p>
                    
                    <p>Ready for the next challenge?</p>
                    <p><strong>Recommended Next:</strong> ${next_recommended_module}</p>
                    
                    <a href="${certificate_url}" class="button">Download Certificate</a>
                    <a href="${platform_url}/learn" class="button">Continue Learning</a>
                </div>
                <div class="footer">
                    <p>&copy; ${current_year} ${platform_name}. All rights reserved.</p>
                    <p><a href="${unsubscribe_url}">Unsubscribe</a></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_completion_text_template(self) -> str:
        return """
        🎉 Congratulations! You completed ${module_name}!
        
        Amazing work, ${user_name}!
        
        ${module_name}
        Completed on ${completion_date}
        
        Your Stats:
        - Total Time: ${total_time}
        - Topics Mastered: ${topics_completed}
        - Final Score: ${final_score}%
        
        You've made significant progress in your Python journey!
        
        Ready for the next challenge?
        Recommended Next: ${next_recommended_module}
        
        Download Certificate: ${certificate_url}
        Continue Learning: ${platform_url}/learn
        
        --
        © ${current_year} ${platform_name}. All rights reserved.
        Unsubscribe: ${unsubscribe_url}
        """
    
    def _get_streak_milestone_html_template(self) -> str:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Streak Milestone Achieved!</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #FF6B35; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9f9f9; text-align: center; }
                .milestone-box { background: white; padding: 30px; margin: 20px 0; border-radius: 10px; border: 3px solid #FF6B35; }
                .flame { font-size: 60px; margin: 10px 0; }
                .stats { background: white; padding: 20px; margin: 15px 0; border-radius: 8px; }
                .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔥 Streak Milestone!</h1>
                </div>
                <div class="content">
                    <h2>Incredible ${user_name}!</h2>
                    
                    <div class="milestone-box">
                        <div class="flame">🔥</div>
                        <h3>${streak_days}-Day Learning Streak!</h3>
                        <p><strong>${milestone_type}</strong> milestone achieved</p>
                    </div>
                    
                    <div class="stats">
                        <h3>Your Learning Stats</h3>
                        <p><strong>Total Topics:</strong> ${total_topics}</p>
                        <p><strong>Total Time:</strong> ${total_time}</p>
                        <p><strong>Next Milestone:</strong> ${next_milestone}</p>
                    </div>
                    
                    <p>${encouragement_message}</p>
                    
                    <p>Your consistency is inspiring! Keep the flame burning!</p>
                </div>
                <div class="footer">
                    <p>&copy; ${current_year} ${platform_name}. All rights reserved.</p>
                    <p><a href="${unsubscribe_url}">Unsubscribe</a></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_streak_milestone_text_template(self) -> str:
        return """
        🔥 Streak Milestone Achieved!
        
        Incredible ${user_name}!
        
        ${streak_days}-Day Learning Streak!
        ${milestone_type} milestone achieved
        
        Your Learning Stats:
        - Total Topics: ${total_topics}
        - Total Time: ${total_time}
        - Next Milestone: ${next_milestone}
        
        ${encouragement_message}
        
        Your consistency is inspiring! Keep the flame burning!
        
        --
        © ${current_year} ${platform_name}. All rights reserved.
        Unsubscribe: ${unsubscribe_url}
        """
    
    def save_template_to_file(self, template_id: str, format_type: str = 'json') -> None:
        """Save template to file for external editing."""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        if format_type == 'json':
            file_path = self.template_dir / f"{template_id}.json"
            template_data = {
                'id': template.id,
                'name': template.name,
                'subject_template': template.subject_template,
                'html_template': template.html_template,
                'text_template': template.text_template,
                'variables': template.variables,
                'category': template.category,
                'description': template.description,
                'tags': template.tags or []
            }
            
            with file_path.open('w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved template {template_id} to {file_path}")
    
    def load_template_from_file(self, file_path: Union[str, Path]) -> EmailTemplate:
        """Load template from file."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Template file not found: {path}")
        
        with path.open('r', encoding='utf-8') as f:
            data = json.load(f)
        
        template = EmailTemplate(
            id=data['id'],
            name=data['name'],
            subject_template=data['subject_template'],
            html_template=data['html_template'],
            text_template=data['text_template'],
            variables=data['variables'],
            category=data['category'],
            description=data.get('description'),
            tags=data.get('tags', [])
        )
        
        self.register_template(template)
        return template


class EmailRenderer:
    """Utility class for rendering emails with common patterns."""
    
    def __init__(self, template_manager: EmailTemplateManager):
        self.template_manager = template_manager
    
    def render_welcome_email(self, user_name: str, user_email: str) -> Dict[str, str]:
        """Render welcome email for new user."""
        variables = {
            'user_name': user_name,
            'user_email': user_email
        }
        return self.template_manager.render_email('welcome', variables, 'both')
    
    def render_progress_report(
        self,
        user_name: str,
        week_start: datetime,
        week_end: datetime,
        topics_completed: int,
        total_study_time: str,
        current_streak: int,
        achievements: List[Dict[str, Any]],
        next_milestone: str,
        progress_percentage: float
    ) -> Dict[str, str]:
        """Render weekly progress report."""
        
        # Format achievements section
        achievements_html = ""
        achievements_text = ""
        
        if achievements:
            achievements_html = '<div class="achievement"><h3>🏆 New Achievements</h3><ul>'
            achievements_text = "\n🏆 New Achievements:\n"
            
            for achievement in achievements:
                achievements_html += f"<li>{achievement.get('badge', '🏆')} {achievement.get('name', 'Achievement')}</li>"
                achievements_text += f"- {achievement.get('badge', '🏆')} {achievement.get('name', 'Achievement')}\n"
            
            achievements_html += '</ul></div>'
        
        variables = {
            'user_name': user_name,
            'week_start': week_start.strftime('%B %d'),
            'week_end': week_end.strftime('%B %d'),
            'topics_completed': str(topics_completed),
            'total_study_time': total_study_time,
            'current_streak': str(current_streak),
            'achievements_earned': achievements_html if achievements else '',
            'next_milestone': next_milestone,
            'progress_percentage': str(int(progress_percentage))
        }
        
        return self.template_manager.render_email('progress_report', variables, 'both')
    
    def render_achievement_notification(
        self,
        user_name: str,
        achievement_name: str,
        achievement_description: str,
        achievement_badge: str,
        achievement_points: int,
        total_points: int
    ) -> Dict[str, str]:
        """Render achievement notification email."""
        variables = {
            'user_name': user_name,
            'achievement_name': achievement_name,
            'achievement_description': achievement_description,
            'achievement_badge': achievement_badge,
            'achievement_points': str(achievement_points),
            'total_points': str(total_points)
        }
        return self.template_manager.render_email('achievement_notification', variables, 'both')
    
    def render_learning_reminder(
        self,
        user_name: str,
        days_since_last_activity: int,
        current_streak: int,
        suggested_topic: str,
        estimated_time: str,
        next_module: str
    ) -> Dict[str, str]:
        """Render learning reminder email."""
        variables = {
            'user_name': user_name,
            'days_since_last_activity': str(days_since_last_activity),
            'current_streak': str(current_streak),
            'suggested_topic': suggested_topic,
            'estimated_time': estimated_time,
            'next_module': next_module
        }
        return self.template_manager.render_email('learning_reminder', variables, 'both')
    
    def render_course_completion(
        self,
        user_name: str,
        module_name: str,
        completion_date: datetime,
        total_time: str,
        topics_completed: int,
        final_score: float,
        next_recommended_module: str,
        certificate_url: str
    ) -> Dict[str, str]:
        """Render course completion email."""
        variables = {
            'user_name': user_name,
            'module_name': module_name,
            'completion_date': completion_date.strftime('%B %d, %Y'),
            'total_time': total_time,
            'topics_completed': str(topics_completed),
            'final_score': str(int(final_score)),
            'next_recommended_module': next_recommended_module,
            'certificate_url': certificate_url
        }
        return self.template_manager.render_email('course_completion', variables, 'both')
    
    def render_streak_milestone(
        self,
        user_name: str,
        streak_days: int,
        milestone_type: str,
        total_topics: int,
        total_time: str,
        next_milestone: str,
        encouragement_message: str
    ) -> Dict[str, str]:
        """Render streak milestone email."""
        variables = {
            'user_name': user_name,
            'streak_days': str(streak_days),
            'milestone_type': milestone_type,
            'total_topics': str(total_topics),
            'total_time': total_time,
            'next_milestone': next_milestone,
            'encouragement_message': encouragement_message
        }
        return self.template_manager.render_email('streak_milestone', variables, 'both')


class EmailPreferences:
    """Manages user email preferences."""
    
    def __init__(self):
        self.default_preferences = {
            'welcome': True,
            'progress_report': True,
            'achievement_notification': True,
            'learning_reminder': True,
            'course_completion': True,
            'streak_milestone': True,
            'frequency_reminders': 'weekly',  # daily, weekly, monthly, never
            'frequency_reports': 'weekly',    # weekly, monthly, never
            'format_preference': 'html'       # html, text, both
        }
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get email preferences for user."""
        # In a real implementation, this would load from database
        return self.default_preferences.copy()
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> None:
        """Update email preferences for user."""
        # In a real implementation, this would save to database
        logger.info(f"Updated email preferences for user {user_id}")
    
    def should_send_email(self, user_id: str, email_type: str) -> bool:
        """Check if email should be sent based on user preferences."""
        preferences = self.get_user_preferences(user_id)
        return preferences.get(email_type, False)


# Convenience functions
def create_email_manager() -> EmailTemplateManager:
    """Create default email template manager."""
    return EmailTemplateManager()


def render_welcome_email(user_name: str, user_email: str) -> Dict[str, str]:
    """Quick function to render welcome email."""
    manager = EmailTemplateManager()
    renderer = EmailRenderer(manager)
    return renderer.render_welcome_email(user_name, user_email)


def render_achievement_email(
    user_name: str,
    achievement_name: str,
    achievement_description: str,
    achievement_badge: str,
    achievement_points: int,
    total_points: int
) -> Dict[str, str]:
    """Quick function to render achievement email."""
    manager = EmailTemplateManager()
    renderer = EmailRenderer(manager)
    return renderer.render_achievement_notification(
        user_name, achievement_name, achievement_description,
        achievement_badge, achievement_points, total_points
    )


# Email validation utilities
def validate_email_variables(template_id: str, variables: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate that all required variables are provided for template."""
    manager = EmailTemplateManager()
    template = manager.get_template(template_id)
    
    if not template:
        return False, [f"Template not found: {template_id}"]
    
    missing_vars = []
    for required_var in template.variables:
        if required_var not in variables:
            missing_vars.append(required_var)
    
    return len(missing_vars) == 0, missing_vars


def preview_email(template_id: str, variables: Dict[str, Any]) -> str:
    """Generate HTML preview of email."""
    manager = EmailTemplateManager()
    rendered = manager.render_email(template_id, variables, 'html')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Email Preview: {rendered.get('subject', 'No Subject')}</title>
        <style>
            .preview-header {{ 
                background: #f0f0f0; 
                padding: 20px; 
                border-bottom: 2px solid #ddd; 
                font-family: Arial, sans-serif;
            }}
        </style>
    </head>
    <body>
        <div class="preview-header">
            <h2>Email Preview</h2>
            <p><strong>Subject:</strong> {rendered.get('subject', 'No Subject')}</p>
            <p><strong>Template:</strong> {template_id}</p>
        </div>
        {rendered.get('html_body', 'No content')}
    </body>
    </html>
    """