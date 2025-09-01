"""
Observer Pattern exercise for the OOP module.
Implement a comprehensive news publisher-subscriber system using the Observer pattern.
"""

from typing import Dict, Any


def get_observer_pattern_exercise() -> Dict[str, Any]:
    """Get the Observer Pattern exercise."""
    return {
        "title": "News Publisher-Subscriber System with Observer Pattern",
        "difficulty": "hard",
        "estimated_time": "2-3 hours",
        "instructions": """
Build a comprehensive news publishing system that demonstrates the Observer design pattern.
Your system should allow multiple types of subscribers to receive notifications when
news is published, with different filtering and notification preferences.

This exercise focuses on implementing a loose coupling between publishers and subscribers,
allowing dynamic subscription management and demonstrating how design patterns solve
real-world architectural problems.
""",
        "learning_objectives": [
            "Implement the Observer design pattern correctly",
            "Understand loose coupling between objects",
            "Practice abstract base classes and interfaces",
            "Handle dynamic subscription management",
            "Build extensible notification systems"
        ],
        "tasks": [
            {
                "step": 1,
                "title": "Create Observer Interface",
                "description": "Design abstract Observer and Subject interfaces",
                "requirements": [
                    "Create abstract Observer class with update() method",
                    "Create Subject class with attach/detach/notify methods",
                    "Define clear interfaces for publisher-subscriber communication",
                    "Add observer management functionality"
                ]
            },
            {
                "step": 2,
                "title": "Implement News Publisher",
                "description": "Create concrete NewsPublisher that extends Subject",
                "requirements": [
                    "Inherit from Subject base class",
                    "Manage news articles and categories",
                    "Implement notification logic for new articles",
                    "Add filtering by category and priority"
                ]
            },
            {
                "step": 3,
                "title": "Create Subscriber Types",
                "description": "Implement different types of news subscribers",
                "requirements": [
                    "EmailSubscriber for email notifications",
                    "SMSSubscriber for text message alerts",
                    "MobileAppSubscriber for push notifications",
                    "Each with different filtering preferences"
                ]
            },
            {
                "step": 4,
                "title": "Add Advanced Features",
                "description": "Extend with sophisticated subscription features",
                "requirements": [
                    "Priority-based notifications",
                    "Category-based filtering",
                    "Subscription preferences and settings",
                    "Notification history and analytics"
                ]
            },
            {
                "step": 5,
                "title": "Implement Analytics and Monitoring",
                "description": "Add system monitoring and subscriber analytics",
                "requirements": [
                    "Track notification delivery rates",
                    "Monitor subscriber engagement",
                    "Generate subscription reports",
                    "Handle failed notifications and retries"
                ]
            }
        ],
        "starter_code": '''
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class NewsCategory(Enum):
    """News category enumeration."""
    BREAKING = "breaking"
    POLITICS = "politics"
    TECHNOLOGY = "technology"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    BUSINESS = "business"

class NewsPriority(Enum):
    """News priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class Observer(ABC):
    """Abstract observer interface."""
    
    @abstractmethod
    def update(self, subject, news_data: Dict[str, Any]) -> None:
        """Receive notification of news update."""
        pass

class Subject(ABC):
    """Abstract subject interface."""
    
    def __init__(self):
        # TODO: Initialize observer list and management
        pass
    
    def attach(self, observer: Observer) -> str:
        """Add an observer."""
        # TODO: Implement observer attachment
        pass
    
    def detach(self, observer: Observer) -> str:
        """Remove an observer."""
        # TODO: Implement observer detachment
        pass
    
    def notify(self, news_data: Dict[str, Any]) -> None:
        """Notify all observers."""
        # TODO: Implement notification logic
        pass

class NewsPublisher(Subject):
    """Concrete news publisher."""
    
    def __init__(self, name: str):
        # TODO: Initialize publisher with subject functionality
        pass
    
    def publish_news(self, headline: str, content: str, 
                    category: NewsCategory, priority: NewsPriority) -> str:
        """Publish a news article."""
        # TODO: Implement news publishing and notification
        pass
    
    def get_subscriber_count(self) -> int:
        """Get total number of subscribers."""
        # TODO: Return subscriber count
        pass

class EmailSubscriber(Observer):
    """Email notification subscriber."""
    
    def __init__(self, email: str, name: str):
        # TODO: Initialize email subscriber
        pass
    
    def update(self, subject, news_data: Dict[str, Any]) -> None:
        """Receive news notification via email."""
        # TODO: Implement email notification logic
        pass
    
    def set_preferences(self, categories: List[NewsCategory], 
                       min_priority: NewsPriority) -> None:
        """Set subscription preferences."""
        # TODO: Implement preference setting
        pass

class SMSSubscriber(Observer):
    """SMS notification subscriber."""
    
    def __init__(self, phone: str, name: str):
        # TODO: Initialize SMS subscriber
        pass
    
    def update(self, subject, news_data: Dict[str, Any]) -> None:
        """Receive news notification via SMS."""
        # TODO: Implement SMS notification logic
        pass

class MobileAppSubscriber(Observer):
    """Mobile app push notification subscriber."""
    
    def __init__(self, device_id: str, user_name: str):
        # TODO: Initialize mobile app subscriber
        pass
    
    def update(self, subject, news_data: Dict[str, Any]) -> None:
        """Receive news notification via push notification."""
        # TODO: Implement push notification logic
        pass

# Test your implementation
if __name__ == "__main__":
    # Create news publisher
    news_publisher = NewsPublisher("Daily Tech News")
    
    # Create subscribers
    email_sub = EmailSubscriber("alice@email.com", "Alice")
    sms_sub = SMSSubscriber("+1234567890", "Bob")
    app_sub = MobileAppSubscriber("device_123", "Carol")
    
    # Subscribe to news
    print(news_publisher.attach(email_sub))
    print(news_publisher.attach(sms_sub))
    print(news_publisher.attach(app_sub))
    
    # Publish news
    news_publisher.publish_news(
        "AI Breakthrough Announced",
        "Scientists achieve major AI milestone...",
        NewsCategory.TECHNOLOGY,
        NewsPriority.HIGH
    )
    
    print(f"Total subscribers: {news_publisher.get_subscriber_count()}")
''',
        "hints": [
            "Use a list to store observers in the Subject class",
            "Pass news data as dictionary to maintain flexibility",
            "Implement filtering in each subscriber type based on preferences",
            "Consider using weak references to prevent memory leaks",
            "Add error handling for notification failures",
            "Use timestamps to track when notifications are sent",
            "Consider thread safety for concurrent notifications"
        ],
        "solution": '''
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from enum import Enum
import uuid
import weakref

class NewsCategory(Enum):
    """News category enumeration."""
    BREAKING = "breaking"
    POLITICS = "politics"
    TECHNOLOGY = "technology"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    BUSINESS = "business"
    HEALTH = "health"
    SCIENCE = "science"

class NewsPriority(Enum):
    """News priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class NotificationStatus(Enum):
    """Notification delivery status."""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    FILTERED = "filtered"

class Observer(ABC):
    """Abstract observer interface for news notifications."""
    
    @abstractmethod
    def update(self, subject, news_data: Dict[str, Any]) -> NotificationStatus:
        """Receive notification of news update."""
        pass
    
    @abstractmethod
    def get_subscriber_id(self) -> str:
        """Get unique subscriber identifier."""
        pass
    
    @abstractmethod
    def get_subscriber_info(self) -> Dict[str, Any]:
        """Get subscriber information."""
        pass

class Subject(ABC):
    """Abstract subject interface for publisher."""
    
    def __init__(self):
        self._observers: List[Observer] = []
        self._notification_history: List[Dict[str, Any]] = []
    
    def attach(self, observer: Observer) -> str:
        """Add an observer."""
        if not isinstance(observer, Observer):
            raise TypeError("Observer must implement Observer interface")
        
        if observer not in self._observers:
            self._observers.append(observer)
            return f"Subscribed {observer.get_subscriber_info()['name']} to notifications"
        return f"Observer {observer.get_subscriber_info()['name']} already subscribed"
    
    def detach(self, observer: Observer) -> str:
        """Remove an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
            return f"Unsubscribed {observer.get_subscriber_info()['name']} from notifications"
        return f"Observer {observer.get_subscriber_info()['name']} not found in subscription list"
    
    def notify(self, news_data: Dict[str, Any]) -> Dict[str, int]:
        """Notify all observers and return delivery statistics."""
        notification_id = str(uuid.uuid4())
        results = {
            'delivered': 0,
            'failed': 0,
            'filtered': 0,
            'total_observers': len(self._observers)
        }
        
        notification_log = {
            'notification_id': notification_id,
            'timestamp': datetime.now().isoformat(),
            'news_data': news_data,
            'results': {}
        }
        
        for observer in self._observers[:]:  # Create copy to avoid modification during iteration
            try:
                status = observer.update(self, news_data)
                notification_log['results'][observer.get_subscriber_id()] = status.value
                
                if status == NotificationStatus.DELIVERED:
                    results['delivered'] += 1
                elif status == NotificationStatus.FAILED:
                    results['failed'] += 1
                elif status == NotificationStatus.FILTERED:
                    results['filtered'] += 1
                    
            except Exception as e:
                results['failed'] += 1
                notification_log['results'][observer.get_subscriber_id()] = f"error: {str(e)}"
        
        self._notification_history.append(notification_log)
        return results
    
    def get_notification_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent notification history."""
        return self._notification_history[-limit:]
    
    def get_observer_count(self) -> int:
        """Get number of attached observers."""
        return len(self._observers)
    
    def get_observers_info(self) -> List[Dict[str, Any]]:
        """Get information about all observers."""
        return [observer.get_subscriber_info() for observer in self._observers]

class NewsArticle:
    """Represents a news article."""
    
    def __init__(self, headline: str, content: str, category: NewsCategory, 
                 priority: NewsPriority, author: str = "Unknown"):
        self.id = str(uuid.uuid4())
        self.headline = headline
        self.content = content
        self.category = category
        self.priority = priority
        self.author = author
        self.published_at = datetime.now()
        self.view_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert article to dictionary."""
        return {
            'id': self.id,
            'headline': self.headline,
            'content': self.content,
            'category': self.category.value,
            'priority': self.priority.value,
            'author': self.author,
            'published_at': self.published_at.isoformat(),
            'view_count': self.view_count
        }
    
    def __str__(self) -> str:
        return f"[{self.category.value.upper()}] {self.headline}"

class NewsPublisher(Subject):
    """Concrete news publisher implementing Subject interface."""
    
    def __init__(self, name: str):
        super().__init__()
        if not name or not name.strip():
            raise ValueError("Publisher name cannot be empty")
        
        self.name = name.strip()
        self.articles: List[NewsArticle] = []
        self.categories_published: Set[NewsCategory] = set()
        self.publication_stats = {
            'total_articles': 0,
            'total_notifications': 0,
            'successful_deliveries': 0,
            'failed_deliveries': 0
        }
    
    def publish_news(self, headline: str, content: str, category: NewsCategory, 
                    priority: NewsPriority, author: str = "Unknown") -> str:
        """Publish a news article and notify subscribers."""
        if not headline or not headline.strip():
            raise ValueError("Headline cannot be empty")
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")
        
        # Create article
        article = NewsArticle(headline.strip(), content.strip(), category, priority, author)
        self.articles.append(article)
        self.categories_published.add(category)
        
        # Update statistics
        self.publication_stats['total_articles'] += 1
        
        # Prepare notification data
        news_data = article.to_dict()
        news_data['publisher'] = self.name
        
        # Notify observers
        notification_results = self.notify(news_data)
        
        # Update delivery statistics
        self.publication_stats['total_notifications'] += notification_results['total_observers']
        self.publication_stats['successful_deliveries'] += notification_results['delivered']
        self.publication_stats['failed_deliveries'] += notification_results['failed']
        
        return (f"Published: {headline} | "
                f"Delivered: {notification_results['delivered']}, "
                f"Failed: {notification_results['failed']}, "
                f"Filtered: {notification_results['filtered']}")
    
    def get_articles_by_category(self, category: NewsCategory) -> List[NewsArticle]:
        """Get all articles in a specific category."""
        return [article for article in self.articles if article.category == category]
    
    def get_recent_articles(self, limit: int = 10) -> List[NewsArticle]:
        """Get most recent articles."""
        return sorted(self.articles, key=lambda a: a.published_at, reverse=True)[:limit]
    
    def get_publisher_stats(self) -> Dict[str, Any]:
        """Get comprehensive publisher statistics."""
        if not self.articles:
            return {"message": "No articles published yet"}
        
        # Category breakdown
        category_counts = {}
        priority_counts = {}
        
        for article in self.articles:
            category_counts[article.category.value] = category_counts.get(article.category.value, 0) + 1
            priority_counts[article.priority.value] = priority_counts.get(article.priority.value, 0) + 1
        
        # Calculate delivery rates
        total_notifications = self.publication_stats['total_notifications']
        delivery_rate = (self.publication_stats['successful_deliveries'] / total_notifications * 100 
                        if total_notifications > 0 else 0)
        
        return {
            'publisher_name': self.name,
            'total_articles': len(self.articles),
            'total_subscribers': self.get_observer_count(),
            'categories_published': len(self.categories_published),
            'category_breakdown': category_counts,
            'priority_breakdown': priority_counts,
            'delivery_stats': {
                'total_notifications_sent': total_notifications,
                'successful_deliveries': self.publication_stats['successful_deliveries'],
                'failed_deliveries': self.publication_stats['failed_deliveries'],
                'delivery_rate_percentage': f"{delivery_rate:.1f}%"
            }
        }
    
    def get_subscriber_count(self) -> int:
        """Get total number of subscribers."""
        return self.get_observer_count()
    
    def __str__(self) -> str:
        return f"NewsPublisher '{self.name}' ({len(self.articles)} articles, {self.get_observer_count()} subscribers)"

class SubscriberPreferences:
    """Manages subscriber preferences and filtering."""
    
    def __init__(self):
        self.categories: Set[NewsCategory] = set(NewsCategory)  # Subscribe to all by default
        self.min_priority: NewsPriority = NewsPriority.LOW
        self.keywords: Set[str] = set()
        self.blocked_keywords: Set[str] = set()
        self.max_notifications_per_hour: int = 50
        self.quiet_hours: Optional[tuple] = None  # (start_hour, end_hour)
    
    def should_receive_notification(self, news_data: Dict[str, Any]) -> bool:
        """Check if notification should be sent based on preferences."""
        # Check category filter
        article_category = NewsCategory(news_data['category'])
        if article_category not in self.categories:
            return False
        
        # Check priority filter
        article_priority = NewsPriority(news_data['priority'])
        if article_priority.value < self.min_priority.value:
            return False
        
        # Check keyword filters
        content_text = f"{news_data['headline']} {news_data['content']}".lower()
        
        # If keywords are specified, at least one must match
        if self.keywords and not any(keyword.lower() in content_text for keyword in self.keywords):
            return False
        
        # Check blocked keywords
        if any(blocked.lower() in content_text for blocked in self.blocked_keywords):
            return False
        
        # Check quiet hours
        if self.quiet_hours:
            current_hour = datetime.now().hour
            start_hour, end_hour = self.quiet_hours
            if start_hour <= current_hour <= end_hour:
                return False
        
        return True

class EmailSubscriber(Observer):
    """Email notification subscriber."""
    
    def __init__(self, email: str, name: str):
        if not email or "@" not in email:
            raise ValueError("Invalid email address")
        if not name or not name.strip():
            raise ValueError("Name cannot be empty")
        
        self.subscriber_id = str(uuid.uuid4())
        self.email = email.strip().lower()
        self.name = name.strip()
        self.preferences = SubscriberPreferences()
        self.notifications_received = 0
        self.last_notification = None
        self.subscription_date = datetime.now()
    
    def update(self, subject, news_data: Dict[str, Any]) -> NotificationStatus:
        """Receive news notification via email."""
        if not self.preferences.should_receive_notification(news_data):
            return NotificationStatus.FILTERED
        
        try:
            # Simulate email sending
            email_content = self._format_email(news_data)
            
            # In real implementation, this would send actual email
            print(f"EMAIL to {self.email}: {news_data['headline']}")
            
            self.notifications_received += 1
            self.last_notification = datetime.now()
            return NotificationStatus.DELIVERED
            
        except Exception as e:
            print(f"Failed to send email to {self.email}: {str(e)}")
            return NotificationStatus.FAILED
    
    def _format_email(self, news_data: Dict[str, Any]) -> str:
        """Format news data as email content."""
        return f"""
Subject: [{news_data['category'].upper()}] {news_data['headline']}

Dear {self.name},

{news_data['content']}

Priority: {news_data['priority']}
Author: {news_data['author']}
Published: {news_data['published_at']}

Best regards,
{news_data['publisher']}
"""
    
    def set_preferences(self, categories: List[NewsCategory] = None, 
                       min_priority: NewsPriority = None,
                       keywords: List[str] = None,
                       blocked_keywords: List[str] = None) -> str:
        """Set subscription preferences."""
        updates = []
        
        if categories is not None:
            self.preferences.categories = set(categories)
            updates.append(f"categories: {[c.value for c in categories]}")
        
        if min_priority is not None:
            self.preferences.min_priority = min_priority
            updates.append(f"min_priority: {min_priority.value}")
        
        if keywords is not None:
            self.preferences.keywords = set(keywords)
            updates.append(f"keywords: {keywords}")
        
        if blocked_keywords is not None:
            self.preferences.blocked_keywords = set(blocked_keywords)
            updates.append(f"blocked_keywords: {blocked_keywords}")
        
        return f"Updated preferences for {self.name}: {', '.join(updates)}"
    
    def get_subscriber_id(self) -> str:
        """Get unique subscriber identifier."""
        return self.subscriber_id
    
    def get_subscriber_info(self) -> Dict[str, Any]:
        """Get subscriber information."""
        return {
            'id': self.subscriber_id,
            'name': self.name,
            'email': self.email,
            'type': 'EmailSubscriber',
            'notifications_received': self.notifications_received,
            'subscription_date': self.subscription_date.isoformat(),
            'last_notification': self.last_notification.isoformat() if self.last_notification else None,
            'subscribed_categories': [cat.value for cat in self.preferences.categories],
            'min_priority': self.preferences.min_priority.value
        }
    
    def __str__(self) -> str:
        return f"EmailSubscriber({self.name} - {self.email})"

class SMSSubscriber(Observer):
    """SMS notification subscriber."""
    
    def __init__(self, phone: str, name: str):
        if not phone or len(phone.replace("+", "").replace("-", "").replace(" ", "")) < 10:
            raise ValueError("Invalid phone number")
        if not name or not name.strip():
            raise ValueError("Name cannot be empty")
        
        self.subscriber_id = str(uuid.uuid4())
        self.phone = phone.strip()
        self.name = name.strip()
        self.preferences = SubscriberPreferences()
        self.preferences.min_priority = NewsPriority.MEDIUM  # SMS typically for important news
        self.notifications_received = 0
        self.last_notification = None
        self.subscription_date = datetime.now()
    
    def update(self, subject, news_data: Dict[str, Any]) -> NotificationStatus:
        """Receive news notification via SMS."""
        if not self.preferences.should_receive_notification(news_data):
            return NotificationStatus.FILTERED
        
        try:
            # Format as SMS (shorter content)
            sms_content = self._format_sms(news_data)
            
            # In real implementation, this would send actual SMS
            print(f"SMS to {self.phone}: {sms_content}")
            
            self.notifications_received += 1
            self.last_notification = datetime.now()
            return NotificationStatus.DELIVERED
            
        except Exception as e:
            print(f"Failed to send SMS to {self.phone}: {str(e)}")
            return NotificationStatus.FAILED
    
    def _format_sms(self, news_data: Dict[str, Any]) -> str:
        """Format news data as SMS content (shorter)."""
        # SMS should be concise
        priority_prefix = "🚨" if news_data['priority'] >= 3 else ""
        return f"{priority_prefix}[{news_data['category'].upper()}] {news_data['headline'][:80]}..."
    
    def get_subscriber_id(self) -> str:
        """Get unique subscriber identifier."""
        return self.subscriber_id
    
    def get_subscriber_info(self) -> Dict[str, Any]:
        """Get subscriber information."""
        return {
            'id': self.subscriber_id,
            'name': self.name,
            'phone': self.phone,
            'type': 'SMSSubscriber',
            'notifications_received': self.notifications_received,
            'subscription_date': self.subscription_date.isoformat(),
            'last_notification': self.last_notification.isoformat() if self.last_notification else None,
            'subscribed_categories': [cat.value for cat in self.preferences.categories],
            'min_priority': self.preferences.min_priority.value
        }
    
    def __str__(self) -> str:
        return f"SMSSubscriber({self.name} - {self.phone})"

class MobileAppSubscriber(Observer):
    """Mobile app push notification subscriber."""
    
    def __init__(self, device_id: str, user_name: str, app_version: str = "1.0"):
        if not device_id or not device_id.strip():
            raise ValueError("Device ID cannot be empty")
        if not user_name or not user_name.strip():
            raise ValueError("User name cannot be empty")
        
        self.subscriber_id = str(uuid.uuid4())
        self.device_id = device_id.strip()
        self.user_name = user_name.strip()
        self.app_version = app_version
        self.preferences = SubscriberPreferences()
        self.notifications_received = 0
        self.last_notification = None
        self.subscription_date = datetime.now()
        self.is_app_active = True
    
    def update(self, subject, news_data: Dict[str, Any]) -> NotificationStatus:
        """Receive news notification via push notification."""
        if not self.is_app_active:
            return NotificationStatus.FAILED
        
        if not self.preferences.should_receive_notification(news_data):
            return NotificationStatus.FILTERED
        
        try:
            # Format as push notification
            push_content = self._format_push_notification(news_data)
            
            # In real implementation, this would send to FCM/APNS
            print(f"PUSH to device {self.device_id}: {push_content['title']}")
            
            self.notifications_received += 1
            self.last_notification = datetime.now()
            return NotificationStatus.DELIVERED
            
        except Exception as e:
            print(f"Failed to send push notification to {self.device_id}: {str(e)}")
            return NotificationStatus.FAILED
    
    def _format_push_notification(self, news_data: Dict[str, Any]) -> Dict[str, str]:
        """Format news data as push notification."""
        return {
            'title': f"[{news_data['category'].upper()}] Breaking News",
            'body': news_data['headline'],
            'data': {
                'article_id': news_data['id'],
                'category': news_data['category'],
                'priority': str(news_data['priority'])
            }
        }
    
    def set_app_status(self, is_active: bool) -> str:
        """Set app active status."""
        self.is_app_active = is_active
        status = "active" if is_active else "inactive"
        return f"Set app status for {self.user_name} to {status}"
    
    def get_subscriber_id(self) -> str:
        """Get unique subscriber identifier."""
        return self.subscriber_id
    
    def get_subscriber_info(self) -> Dict[str, Any]:
        """Get subscriber information."""
        return {
            'id': self.subscriber_id,
            'user_name': self.user_name,
            'device_id': self.device_id,
            'app_version': self.app_version,
            'type': 'MobileAppSubscriber',
            'notifications_received': self.notifications_received,
            'subscription_date': self.subscription_date.isoformat(),
            'last_notification': self.last_notification.isoformat() if self.last_notification else None,
            'is_app_active': self.is_app_active,
            'subscribed_categories': [cat.value for cat in self.preferences.categories],
            'min_priority': self.preferences.min_priority.value
        }
    
    def __str__(self) -> str:
        return f"MobileAppSubscriber({self.user_name} - {self.device_id})"

class NewsAnalytics:
    """Analytics system for news publishing and subscriptions."""
    
    def __init__(self, publisher: NewsPublisher):
        self.publisher = publisher
    
    def get_engagement_report(self) -> Dict[str, Any]:
        """Generate subscriber engagement report."""
        subscribers = self.publisher.get_observers_info()
        if not subscribers:
            return {"message": "No subscribers to analyze"}
        
        # Calculate engagement metrics
        total_notifications = sum(sub['notifications_received'] for sub in subscribers)
        active_subscribers = len([sub for sub in subscribers if sub['notifications_received'] > 0])
        
        # Subscriber type breakdown
        type_counts = {}
        for subscriber in subscribers:
            sub_type = subscriber['type']
            type_counts[sub_type] = type_counts.get(sub_type, 0) + 1
        
        # Most engaged subscribers
        most_engaged = sorted(subscribers, 
                             key=lambda s: s['notifications_received'], 
                             reverse=True)[:5]
        
        return {
            'total_subscribers': len(subscribers),
            'active_subscribers': active_subscribers,
            'engagement_rate': f"{active_subscribers/len(subscribers)*100:.1f}%" if subscribers else "0%",
            'total_notifications_delivered': total_notifications,
            'avg_notifications_per_subscriber': total_notifications / len(subscribers) if subscribers else 0,
            'subscriber_type_breakdown': type_counts,
            'most_engaged_subscribers': [
                {'name': sub.get('name', sub.get('user_name', 'Unknown')), 
                 'notifications': sub['notifications_received']} 
                for sub in most_engaged[:3]
            ]
        }
    
    def get_content_performance(self) -> Dict[str, Any]:
        """Analyze content performance by category and priority."""
        articles = self.publisher.articles
        if not articles:
            return {"message": "No articles to analyze"}
        
        # Category performance
        category_stats = {}
        priority_stats = {}
        
        for article in articles:
            cat = article.category.value
            pri = article.priority.value
            
            if cat not in category_stats:
                category_stats[cat] = {'count': 0, 'total_views': 0}
            category_stats[cat]['count'] += 1
            category_stats[cat]['total_views'] += article.view_count
            
            if pri not in priority_stats:
                priority_stats[pri] = {'count': 0, 'total_views': 0}
            priority_stats[pri]['count'] += 1
            priority_stats[pri]['total_views'] += article.view_count
        
        # Calculate averages
        for stats in category_stats.values():
            stats['avg_views'] = stats['total_views'] / stats['count'] if stats['count'] > 0 else 0
        
        for stats in priority_stats.values():
            stats['avg_views'] = stats['total_views'] / stats['count'] if stats['count'] > 0 else 0
        
        return {
            'total_articles': len(articles),
            'category_performance': category_stats,
            'priority_performance': priority_stats,
            'most_recent_articles': [
                {'headline': a.headline, 'category': a.category.value, 'views': a.view_count}
                for a in sorted(articles, key=lambda x: x.published_at, reverse=True)[:5]
            ]
        }

# Comprehensive demonstration
def demonstrate_observer_pattern():
    """Demonstrate the complete Observer pattern news system."""
    print("=== Observer Pattern News System Demo ===\\n")
    
    # Create news publisher
    publisher = NewsPublisher("Global News Network")
    print(f"Created: {publisher}")
    
    # Create subscribers with different preferences
    print("\\n--- Creating Subscribers ---")
    
    # Email subscribers
    alice_email = EmailSubscriber("alice@example.com", "Alice Johnson")
    alice_email.set_preferences(
        categories=[NewsCategory.TECHNOLOGY, NewsCategory.SCIENCE],
        min_priority=NewsPriority.MEDIUM
    )
    
    bob_email = EmailSubscriber("bob@example.com", "Bob Smith")
    bob_email.set_preferences(
        categories=[NewsCategory.SPORTS, NewsCategory.ENTERTAINMENT],
        min_priority=NewsPriority.LOW
    )
    
    # SMS subscriber (prefers urgent news)
    carol_sms = SMSSubscriber("+1-555-0123", "Carol Brown")
    carol_sms.preferences.min_priority = NewsPriority.HIGH
    
    # Mobile app subscribers
    david_app = MobileAppSubscriber("device_android_001", "David Wilson")
    emma_app = MobileAppSubscriber("device_iphone_002", "Emma Davis")
    emma_app.preferences.categories = {NewsCategory.BREAKING, NewsCategory.POLITICS}
    
    # Subscribe everyone
    subscribers = [alice_email, bob_email, carol_sms, david_app, emma_app]
    print("\\n--- Subscribing to Publisher ---")
    for subscriber in subscribers:
        result = publisher.attach(subscriber)
        print(f"  {result}")
    
    print(f"\\nTotal subscribers: {publisher.get_subscriber_count()}")
    
    # Publish various news articles
    print("\\n--- Publishing News Articles ---")
    
    news_articles = [
        ("Tech Giant Announces Breakthrough", "Major advancement in quantum computing...", 
         NewsCategory.TECHNOLOGY, NewsPriority.HIGH),
        ("Local Sports Team Wins Championship", "The city celebrates victory...", 
         NewsCategory.SPORTS, NewsPriority.MEDIUM),
        ("BREAKING: Market Crash Alert", "Stock markets plummet worldwide...", 
         NewsCategory.BREAKING, NewsPriority.URGENT),
        ("New Movie Release", "Hollywood's latest blockbuster hits theaters...", 
         NewsCategory.ENTERTAINMENT, NewsPriority.LOW),
        ("Political Election Results", "Surprising outcomes in local elections...", 
         NewsCategory.POLITICS, NewsPriority.HIGH)
    ]
    
    for headline, content, category, priority in news_articles:
        print(f"\\n{publisher.publish_news(headline, content, category, priority)}")
    
    # Show subscriber engagement
    print("\\n--- Subscriber Engagement ---")
    analytics = NewsAnalytics(publisher)
    engagement_report = analytics.get_engagement_report()
    
    print(f"Engagement Rate: {engagement_report['engagement_rate']}")
    print(f"Total Notifications Delivered: {engagement_report['total_notifications_delivered']}")
    print("\\nSubscriber Types:")
    for sub_type, count in engagement_report['subscriber_type_breakdown'].items():
        print(f"  {sub_type}: {count}")
    
    print("\\nMost Engaged Subscribers:")
    for subscriber in engagement_report['most_engaged_subscribers']:
        print(f"  {subscriber['name']}: {subscriber['notifications']} notifications")
    
    # Test unsubscribing
    print("\\n--- Testing Unsubscribe ---")
    print(publisher.detach(carol_sms))
    
    # Publish one more article to see the difference
    print("\\n--- Publishing After Unsubscribe ---")
    result = publisher.publish_news(
        "Emergency Weather Alert", 
        "Severe storm approaching the area...", 
        NewsCategory.BREAKING, 
        NewsPriority.URGENT
    )
    print(result)
    
    # Show final statistics
    print("\\n--- Final Publisher Statistics ---")
    stats = publisher.get_publisher_stats()
    print(f"Publisher: {stats['publisher_name']}")
    print(f"Total Articles: {stats['total_articles']}")
    print(f"Total Subscribers: {stats['total_subscribers']}")
    print(f"Delivery Rate: {stats['delivery_stats']['delivery_rate_percentage']}")
    
    print("\\nCategory Breakdown:")
    for category, count in stats['category_breakdown'].items():
        print(f"  {category}: {count} articles")
    
    # Test advanced features
    print("\\n--- Testing Advanced Features ---")
    
    # Set app to inactive
    print(david_app.set_app_status(False))
    
    # Test keyword filtering
    alice_email.set_preferences(keywords=["quantum", "AI"])
    print("Set Alice's keywords to: quantum, AI")
    
    # Publish article that should be filtered
    print("\\n--- Testing Keyword Filtering ---")
    result = publisher.publish_news(
        "New Restaurant Opens Downtown", 
        "A new Italian restaurant has opened...", 
        NewsCategory.ENTERTAINMENT, 
        NewsPriority.LOW
    )
    print(result)
    
    # Publish article that should match keywords
    result = publisher.publish_news(
        "AI Revolution in Healthcare", 
        "Artificial intelligence transforms medical diagnosis...", 
        NewsCategory.TECHNOLOGY, 
        NewsPriority.MEDIUM
    )
    print(result)
    
    print("\\n--- Demo Complete ---")

if __name__ == "__main__":
    demonstrate_observer_pattern()
'''
    }