# Location: src/python_mastery_hub/web/services/email_service.py

"""
Email Service

Handles email sending, templating, and notification management
for user communications, verification, and marketing.
"""

import smtplib
import ssl
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
import jinja2
from enum import Enum

from python_mastery_hub.web.models.user import User
from python_mastery_hub.utils.logging_config import get_logger
from python_mastery_hub.core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class EmailProvider(str, Enum):
    """Email provider enumeration."""
    SMTP = "smtp"
    SENDGRID = "sendgrid"
    AWS_SES = "aws_ses"
    MAILGUN = "mailgun"
    GMAIL = "gmail"


class EmailPriority(str, Enum):
    """Email priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class EmailType(str, Enum):
    """Email type enumeration."""
    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"
    WELCOME = "welcome"
    NOTIFICATION = "notification"
    ACHIEVEMENT = "achievement"
    REMINDER = "reminder"
    NEWSLETTER = "newsletter"
    MARKETING = "marketing"
    SYSTEM = "system"


@dataclass
class EmailAttachment:
    """Email attachment data."""
    filename: str
    content: bytes
    content_type: str = "application/octet-stream"


@dataclass
class EmailTemplate:
    """Email template data."""
    name: str
    subject: str
    html_template: str
    text_template: Optional[str] = None
    variables: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = {}


@dataclass
class EmailMessage:
    """Email message data."""
    to: Union[str, List[str]]
    subject: str
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    reply_to: Optional[str] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    attachments: Optional[List[EmailAttachment]] = None
    template_name: Optional[str] = None
    template_variables: Optional[Dict[str, Any]] = None
    priority: EmailPriority = EmailPriority.NORMAL
    email_type: EmailType = EmailType.NOTIFICATION
    send_at: Optional[datetime] = None
    
    def __post_init__(self):
        if isinstance(self.to, str):
            self.to = [self.to]
        if self.template_variables is None:
            self.template_variables = {}
        if self.attachments is None:
            self.attachments = []


class EmailTemplateManager:
    """Manages email templates."""
    
    def __init__(self, templates_dir: str = "templates/email"):
        self.templates_dir = Path(templates_dir)
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, EmailTemplate]:
        """Load email templates from files."""
        templates = {}
        
        # Built-in templates
        templates.update({
            'welcome': EmailTemplate(
                name='welcome',
                subject='Welcome to Python Mastery Hub!',
                html_template='''
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h1 style="color: #2c3e50;">Welcome to Python Mastery Hub!</h1>
                        <p>Hi {{ user.full_name }},</p>
                        <p>Thank you for joining Python Mastery Hub! We're excited to help you on your Python learning journey.</p>
                        <p>Here's what you can do to get started:</p>
                        <ul>
                            <li>Complete your profile setup</li>
                            <li>Take our skill assessment quiz</li>
                            <li>Browse our learning modules</li>
                            <li>Start with your first exercise</li>
                        </ul>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{ dashboard_url }}" style="background-color: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Go to Dashboard</a>
                        </div>
                        <p>If you have any questions, feel free to contact our support team.</p>
                        <p>Happy coding!</p>
                        <p>The Python Mastery Hub Team</p>
                    </div>
                </body>
                </html>
                ''',
                text_template='''
                Welcome to Python Mastery Hub!
                
                Hi {{ user.full_name }},
                
                Thank you for joining Python Mastery Hub! We're excited to help you on your Python learning journey.
                
                Here's what you can do to get started:
                • Complete your profile setup
                • Take our skill assessment quiz
                • Browse our learning modules
                • Start with your first exercise
                
                Visit your dashboard: {{ dashboard_url }}
                
                If you have any questions, feel free to contact our support team.
                
                Happy coding!
                The Python Mastery Hub Team
                '''
            ),
            
            'email_verification': EmailTemplate(
                name='email_verification',
                subject='Verify your email address',
                html_template='''
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h1 style="color: #2c3e50;">Verify Your Email Address</h1>
                        <p>Hi {{ user.full_name }},</p>
                        <p>Please click the button below to verify your email address and activate your account:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{ verification_url }}" style="background-color: #27ae60; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Verify Email</a>
                        </div>
                        <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                        <p style="word-break: break-all;">{{ verification_url }}</p>
                        <p>This verification link will expire in 24 hours.</p>
                        <p>If you didn't create an account with us, please ignore this email.</p>
                        <p>Best regards,<br>The Python Mastery Hub Team</p>
                    </div>
                </body>
                </html>
                ''',
                text_template='''
                Verify Your Email Address
                
                Hi {{ user.full_name }},
                
                Please visit the following link to verify your email address and activate your account:
                
                {{ verification_url }}
                
                This verification link will expire in 24 hours.
                
                If you didn't create an account with us, please ignore this email.
                
                Best regards,
                The Python Mastery Hub Team
                '''
            ),
            
            'password_reset': EmailTemplate(
                name='password_reset',
                subject='Reset your password',
                html_template='''
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h1 style="color: #2c3e50;">Reset Your Password</h1>
                        <p>Hi {{ user.full_name }},</p>
                        <p>We received a request to reset your password. Click the button below to create a new password:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{ reset_url }}" style="background-color: #e74c3c; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
                        </div>
                        <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                        <p style="word-break: break-all;">{{ reset_url }}</p>
                        <p>This password reset link will expire in 1 hour for security reasons.</p>
                        <p>If you didn't request a password reset, please ignore this email or contact support if you're concerned about your account security.</p>
                        <p>Best regards,<br>The Python Mastery Hub Team</p>
                    </div>
                </body>
                </html>
                ''',
                text_template='''
                Reset Your Password
                
                Hi {{ user.full_name }},
                
                We received a request to reset your password. Visit the following link to create a new password:
                
                {{ reset_url }}
                
                This password reset link will expire in 1 hour for security reasons.
                
                If you didn't request a password reset, please ignore this email or contact support if you're concerned about your account security.
                
                Best regards,
                The Python Mastery Hub Team
                '''
            ),
            
            'achievement_unlocked': EmailTemplate(
                name='achievement_unlocked',
                subject='Achievement Unlocked: {{ achievement.title }}!',
                html_template='''
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h1 style="color: #f39c12;">🏆 Achievement Unlocked!</h1>
                        <p>Hi {{ user.full_name }},</p>
                        <p>Congratulations! You've just unlocked a new achievement:</p>
                        <div style="background-color: #f8f9fa; border-left: 4px solid #f39c12; padding: 20px; margin: 20px 0;">
                            <h2 style="margin: 0; color: #f39c12;">{{ achievement.title }}</h2>
                            <p style="margin: 10px 0 0 0;">{{ achievement.description }}</p>
                            <p style="margin: 10px 0 0 0;"><strong>Points earned: {{ achievement.points }}</strong></p>
                        </div>
                        <p>Keep up the great work! Check out your profile to see all your achievements.</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{ profile_url }}" style="background-color: #f39c12; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">View Profile</a>
                        </div>
                        <p>Happy learning!</p>
                        <p>The Python Mastery Hub Team</p>
                    </div>
                </body>
                </html>
                '''
            )
        })
        
        return templates
    
    def get_template(self, name: str) -> Optional[EmailTemplate]:
        """Get email template by name."""
        return self.templates.get(name)
    
    def render_template(self, template_name: str, variables: Dict[str, Any]) -> Dict[str, str]:
        """Render email template with variables."""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Merge template variables with provided variables
        all_variables = {**template.variables, **variables}
        
        # Render templates
        html_template = jinja2.Template(template.html_template)
        html_content = html_template.render(all_variables)
        
        text_content = None
        if template.text_template:
            text_template = jinja2.Template(template.text_template)
            text_content = text_template.render(all_variables)
        
        # Render subject
        subject_template = jinja2.Template(template.subject)
        subject = subject_template.render(all_variables)
        
        return {
            'subject': subject,
            'html_content': html_content,
            'text_content': text_content
        }


class SMTPEmailProvider:
    """SMTP email provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 587)
        self.username = config.get('username')
        self.password = config.get('password')
        self.use_tls = config.get('use_tls', True)
        self.timeout = config.get('timeout', 30)
    
    async def send_email(self, message: EmailMessage) -> bool:
        """Send email via SMTP."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = f"{message.from_name} <{message.from_email}>" if message.from_name else message.from_email
            msg['To'] = ', '.join(message.to)
            
            if message.cc:
                msg['Cc'] = ', '.join(message.cc)
            
            if message.reply_to:
                msg['Reply-To'] = message.reply_to
            
            # Add content
            if message.text_content:
                text_part = MIMEText(message.text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            if message.html_content:
                html_part = MIMEText(message.html_content, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Add attachments
            for attachment in message.attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.content)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment.filename}'
                )
                msg.attach(part)
            
            # Connect and send
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.host, self.port, timeout=self.timeout) as server:
                if self.use_tls:
                    server.starttls(context=context)
                
                if self.username and self.password:
                    server.login(self.username, self.password)
                
                # Prepare recipient list
                recipients = message.to[:]
                if message.cc:
                    recipients.extend(message.cc)
                if message.bcc:
                    recipients.extend(message.bcc)
                
                server.send_message(msg, to_addrs=recipients)
                
                logger.info(f"Email sent successfully to {len(message.to)} recipients")
                return True
        
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {e}")
            return False


class EmailService:
    """Main email service."""
    
    def __init__(self):
        self.template_manager = EmailTemplateManager()
        self.provider = self._get_email_provider()
        self.default_from_email = getattr(settings, 'default_from_email', 'noreply@pythonmasteryhub.com')
        self.default_from_name = getattr(settings, 'default_from_name', 'Python Mastery Hub')
        
        # Email sending statistics
        self.emails_sent = 0
        self.emails_failed = 0
        self.last_send_time = None
    
    def _get_email_provider(self):
        """Get configured email provider."""
        provider_type = getattr(settings, 'email_provider', 'smtp')
        
        if provider_type == EmailProvider.SMTP:
            config = {
                'host': getattr(settings, 'smtp_host', 'localhost'),
                'port': getattr(settings, 'smtp_port', 587),
                'username': getattr(settings, 'smtp_username', None),
                'password': getattr(settings, 'smtp_password', None),
                'use_tls': getattr(settings, 'smtp_use_tls', True),
                'timeout': getattr(settings, 'smtp_timeout', 30)
            }
            return SMTPEmailProvider(config)
        
        # Add other providers here (SendGrid, AWS SES, etc.)
        else:
            # Default to SMTP
            return SMTPEmailProvider({
                'host': 'localhost',
                'port': 587,
                'use_tls': True
            })
    
    async def send_email(self, message: EmailMessage) -> bool:
        """Send an email message."""
        try:
            # Set defaults if not provided
            if not message.from_email:
                message.from_email = self.default_from_email
            if not message.from_name:
                message.from_name = self.default_from_name
            
            # Render template if specified
            if message.template_name:
                rendered = self.template_manager.render_template(
                    message.template_name,
                    message.template_variables
                )
                message.subject = rendered['subject']
                message.html_content = rendered['html_content']
                message.text_content = rendered['text_content']
            
            # Validate message
            if not message.to:
                raise ValueError("No recipients specified")
            
            if not message.subject:
                raise ValueError("No subject specified")
            
            if not message.html_content and not message.text_content:
                raise ValueError("No content specified")
            
            # Send email
            success = await self.provider.send_email(message)
            
            # Update statistics
            if success:
                self.emails_sent += 1
                logger.info(f"Email sent: {message.subject} to {len(message.to)} recipients")
            else:
                self.emails_failed += 1
                logger.error(f"Email failed: {message.subject}")
            
            self.last_send_time = datetime.now()
            
            return success
        
        except Exception as e:
            self.emails_failed += 1
            logger.error(f"Email sending error: {e}")
            return False
    
    async def send_welcome_email(self, user: User) -> bool:
        """Send welcome email to new user."""
        message = EmailMessage(
            to=[user.email],
            template_name='welcome',
            template_variables={
                'user': user,
                'dashboard_url': f"{settings.frontend_url}/dashboard"
            },
            email_type=EmailType.WELCOME
        )
        
        return await self.send_email(message)
    
    async def send_verification_email(self, user: User, verification_token: str) -> bool:
        """Send email verification email."""
        verification_url = f"{settings.frontend_url}/verify-email?token={verification_token}"
        
        message = EmailMessage(
            to=[user.email],
            template_name='email_verification',
            template_variables={
                'user': user,
                'verification_url': verification_url
            },
            email_type=EmailType.VERIFICATION,
            priority=EmailPriority.HIGH
        )
        
        return await self.send_email(message)
    
    async def send_password_reset_email(self, user: User, reset_token: str) -> bool:
        """Send password reset email."""
        reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"
        
        message = EmailMessage(
            to=[user.email],
            template_name='password_reset',
            template_variables={
                'user': user,
                'reset_url': reset_url
            },
            email_type=EmailType.PASSWORD_RESET,
            priority=EmailPriority.HIGH
        )
        
        return await self.send_email(message)
    
    async def send_achievement_email(self, user: User, achievement: Dict[str, Any]) -> bool:
        """Send achievement notification email."""
        if not user.preferences.email_notifications:
            return True  # User has disabled email notifications
        
        profile_url = f"{settings.frontend_url}/profile"
        
        message = EmailMessage(
            to=[user.email],
            template_name='achievement_unlocked',
            template_variables={
                'user': user,
                'achievement': achievement,
                'profile_url': profile_url
            },
            email_type=EmailType.ACHIEVEMENT
        )
        
        return await self.send_email(message)
    
    async def send_reminder_email(self, user: User, reminder_type: str, data: Dict[str, Any]) -> bool:
        """Send reminder email."""
        if not user.preferences.email_notifications:
            return True
        
        # Different reminder types
        if reminder_type == 'streak_risk':
            subject = "Don't break your learning streak!"
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Hi {user.full_name},</h2>
                <p>You're on a {data.get('streak_days', 0)}-day learning streak! 
                Don't let it end today.</p>
                <p>Take just 10 minutes to complete an exercise and keep your streak alive.</p>
                <a href="{settings.frontend_url}/exercises" 
                   style="background-color: #3498db; color: white; padding: 10px 20px; 
                          text-decoration: none; border-radius: 5px;">Continue Learning</a>
            </body>
            </html>
            """
        
        elif reminder_type == 'weekly_goal':
            subject = "Weekly goal reminder"
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Hi {user.full_name},</h2>
                <p>You're {data.get('progress_percent', 0)}% towards your weekly learning goal.</p>
                <p>You need {data.get('remaining_minutes', 0)} more minutes to reach your goal.</p>
                <a href="{settings.frontend_url}/dashboard" 
                   style="background-color: #27ae60; color: white; padding: 10px 20px; 
                          text-decoration: none; border-radius: 5px;">View Progress</a>
            </body>
            </html>
            """
        
        else:
            return False  # Unknown reminder type
        
        message = EmailMessage(
            to=[user.email],
            subject=subject,
            html_content=html_content,
            email_type=EmailType.REMINDER
        )
        
        return await self.send_email(message)
    
    async def send_bulk_email(self, recipients: List[str], message: EmailMessage) -> Dict[str, Any]:
        """Send email to multiple recipients."""
        results = {
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        # Send in batches to avoid overwhelming the email server
        batch_size = 50
        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i + batch_size]
            
            batch_message = EmailMessage(
                to=batch,
                subject=message.subject,
                html_content=message.html_content,
                text_content=message.text_content,
                template_name=message.template_name,
                template_variables=message.template_variables,
                email_type=message.email_type,
                priority=message.priority
            )
            
            try:
                success = await self.send_email(batch_message)
                if success:
                    results['sent'] += len(batch)
                else:
                    results['failed'] += len(batch)
                    results['errors'].append(f"Batch {i//batch_size + 1} failed")
            
            except Exception as e:
                results['failed'] += len(batch)
                results['errors'].append(f"Batch {i//batch_size + 1} error: {str(e)}")
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get email service statistics."""
        return {
            'emails_sent': self.emails_sent,
            'emails_failed': self.emails_failed,
            'success_rate': (
                self.emails_sent / (self.emails_sent + self.emails_failed) * 100
                if (self.emails_sent + self.emails_failed) > 0 else 0
            ),
            'last_send_time': self.last_send_time,
            'provider_type': type(self.provider).__name__
        }
    
    async def test_email_configuration(self) -> Dict[str, Any]:
        """Test email configuration."""
        test_message = EmailMessage(
            to=[self.default_from_email],
            subject="Test Email Configuration",
            text_content="This is a test email to verify email configuration.",
            html_content="""
            <html>
            <body>
                <h2>Email Configuration Test</h2>
                <p>This is a test email to verify email configuration.</p>
                <p>If you receive this email, your email service is working correctly.</p>
            </body>
            </html>
            """,
            email_type=EmailType.SYSTEM
        )
        
        try:
            success = await self.send_email(test_message)
            return {
                'success': success,
                'message': 'Test email sent successfully' if success else 'Test email failed',
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Test email error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def add_template(self, template: EmailTemplate) -> None:
        """Add a custom email template."""
        self.template_manager.templates[template.name] = template
        logger.info(f"Added email template: {template.name}")
    
    def get_template_names(self) -> List[str]:
        """Get list of available template names."""
        return list(self.template_manager.templates.keys())
    
    async def queue_email(self, message: EmailMessage, send_at: Optional[datetime] = None) -> str:
        """Queue email for later sending."""
        # TODO: Implement email queue with database storage
        # This would typically store the email in a queue table
        # and be processed by a background worker
        
        import uuid
        queue_id = str(uuid.uuid4())
        
        # For now, just log the queued email
        logger.info(f"Email queued with ID {queue_id}, scheduled for {send_at or 'immediate'}")
        
        return queue_id
    
    async def cancel_queued_email(self, queue_id: str) -> bool:
        """Cancel a queued email."""
        # TODO: Implement queue cancellation
        logger.info(f"Cancelled queued email: {queue_id}")
        return True