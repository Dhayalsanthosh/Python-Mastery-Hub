"""
Observer Pattern Testing Exercise.

This exercise demonstrates testing design patterns, specifically the Observer pattern.
Students will test event-driven systems, subscription mechanisms, and notification flows.
Focus on testing behavior, state changes, and interaction between components.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from enum import Enum
import time


class EventType(Enum):
    """Types of events in the system."""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"
    ORDER_CREATED = "order_created"
    ORDER_COMPLETED = "order_completed"
    ORDER_CANCELLED = "order_cancelled"
    PAYMENT_PROCESSED = "payment_processed"
    PAYMENT_FAILED = "payment_failed"


class Event:
    """Event data structure."""
    
    def __init__(self, event_type: EventType, data: Dict[str, Any], source: str = ""):
        self.event_type = event_type
        self.data = data
        self.source = source
        self.timestamp = time.time()
        self.event_id = f"{event_type.value}_{int(self.timestamp * 1000)}"
    
    def __str__(self):
        return f"Event({self.event_type.value}, {self.data}, {self.source})"
    
    def __eq__(self, other):
        if not isinstance(other, Event):
            return False
        return (self.event_type == other.event_type and 
                self.data == other.data and 
                self.source == other.source)


# Observer Pattern Base Classes
class Observer(ABC):
    """Abstract observer interface."""
    
    @abstractmethod
    def update(self, event: Event) -> None:
        """Handle an event notification."""
        pass


class Subject(ABC):
    """Abstract subject interface."""
    
    @abstractmethod
    def subscribe(self, observer: Observer, event_type: Optional[EventType] = None) -> None:
        """Subscribe an observer to events."""
        pass
    
    @abstractmethod
    def unsubscribe(self, observer: Observer, event_type: Optional[EventType] = None) -> None:
        """Unsubscribe an observer from events."""
        pass
    
    @abstractmethod
    def notify(self, event: Event) -> None:
        """Notify observers of an event."""
        pass


# Exercise Implementation Classes - IMPLEMENT THESE
class EventPublisher(Subject):
    """Event publisher that manages observers and notifications."""
    
    def __init__(self):
        """Initialize the event publisher."""
        # TODO: Initialize observer storage
        pass
    
    def subscribe(self, observer: Observer, event_type: Optional[EventType] = None) -> None:
        """Subscribe an observer to specific event types or all events."""
        # TODO: Implement subscription logic
        pass
    
    def unsubscribe(self, observer: Observer, event_type: Optional[EventType] = None) -> None:
        """Unsubscribe an observer from specific event types or all events."""
        # TODO: Implement unsubscription logic
        pass
    
    def notify(self, event: Event) -> None:
        """Notify all relevant observers of an event."""
        # TODO: Implement notification logic
        pass
    
    def get_observer_count(self, event_type: Optional[EventType] = None) -> int:
        """Get count of observers for a specific event type or all events."""
        # TODO: Implement observer counting
        pass


class EmailNotificationService(Observer):
    """Email notification service that observes events."""
    
    def __init__(self, email_service=None):
        """Initialize with optional email service dependency."""
        self.email_service = email_service or MockEmailService()
        self.sent_emails = []
        self.processed_events = []
    
    def update(self, event: Event) -> None:
        """Process events and send appropriate emails."""
        # TODO: Implement email notification logic based on event type
        pass
    
    def get_sent_email_count(self) -> int:
        """Get count of emails sent."""
        return len(self.sent_emails)


class AuditLogger(Observer):
    """Audit logger that records all system events."""
    
    def __init__(self, log_file: str = "audit.log"):
        self.log_file = log_file
        self.logged_events = []
    
    def update(self, event: Event) -> None:
        """Log the event to audit trail."""
        # TODO: Implement audit logging
        pass
    
    def get_logged_event_count(self) -> int:
        """Get count of logged events."""
        return len(self.logged_events)


class MetricsCollector(Observer):
    """Metrics collector that tracks event statistics."""
    
    def __init__(self):
        self.event_counts = {}
        self.last_event_time = {}
    
    def update(self, event: Event) -> None:
        """Collect metrics from events."""
        # TODO: Implement metrics collection
        pass
    
    def get_event_count(self, event_type: EventType) -> int:
        """Get count for specific event type."""
        # TODO: Return count for event type
        pass
    
    def get_total_events(self) -> int:
        """Get total event count across all types."""
        # TODO: Return total count
        pass


class UserService:
    """User service that publishes events."""
    
    def __init__(self, event_publisher: EventPublisher):
        self.event_publisher = event_publisher
        self.users = {}
    
    def register_user(self, username: str, email: str) -> Dict[str, Any]:
        """Register a new user and publish event."""
        # TODO: Implement user registration with event publishing
        pass
    
    def login_user(self, username: str) -> bool:
        """Login user and publish event."""
        # TODO: Implement user login with event publishing
        pass
    
    def logout_user(self, username: str) -> bool:
        """Logout user and publish event."""
        # TODO: Implement user logout with event publishing
        pass


class OrderService:
    """Order service that publishes events."""
    
    def __init__(self, event_publisher: EventPublisher):
        self.event_publisher = event_publisher
        self.orders = {}
        self.next_order_id = 1
    
    def create_order(self, user_id: str, items: List[Dict]) -> Dict[str, Any]:
        """Create order and publish event."""
        # TODO: Implement order creation with event publishing
        pass
    
    def complete_order(self, order_id: str) -> bool:
        """Complete order and publish event."""
        # TODO: Implement order completion with event publishing
        pass
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel order and publish event."""
        # TODO: Implement order cancellation with event publishing
        pass


# Mock Services for Testing
class MockEmailService:
    """Mock email service for testing."""
    
    def __init__(self):
        self.sent_emails = []
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Mock email sending."""
        email = {
            "to": to,
            "subject": subject,
            "body": body,
            "timestamp": time.time()
        }
        self.sent_emails.append(email)
        return True


# Test Cases - Complete These Exercises
class TestEventPublisher(unittest.TestCase):
    """Test the EventPublisher implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.publisher = EventPublisher()
        self.observer1 = Mock(spec=Observer)
        self.observer2 = Mock(spec=Observer)
        self.test_event = Event(EventType.USER_LOGIN, {"user_id": "123"}, "test")
    
    def test_subscribe_observer(self):
        """Exercise 1: Test subscribing an observer to all events."""
        # TODO: Test that observer is properly subscribed
        # 1. Subscribe observer to all events
        # 2. Verify observer count increases
        # 3. Verify observer can receive notifications
        pass
    
    def test_subscribe_observer_to_specific_event(self):
        """Exercise 2: Test subscribing observer to specific event type."""
        # TODO: Test event-specific subscription
        # 1. Subscribe observer to USER_LOGIN events only
        # 2. Send USER_LOGIN event - should notify observer
        # 3. Send USER_LOGOUT event - should NOT notify observer
        pass
    
    def test_unsubscribe_observer(self):
        """Exercise 3: Test unsubscribing an observer."""
        # TODO: Test unsubscription
        # 1. Subscribe observer
        # 2. Verify it receives notifications
        # 3. Unsubscribe observer
        # 4. Verify it no longer receives notifications
        pass
    
    def test_notify_multiple_observers(self):
        """Exercise 4: Test notifying multiple observers."""
        # TODO: Test multiple observer notification
        # 1. Subscribe multiple observers
        # 2. Send event
        # 3. Verify all observers are notified
        pass
    
    def test_observer_receives_correct_event(self):
        """Exercise 5: Test that observers receive the correct event object."""
        # TODO: Test event data integrity
        # 1. Subscribe observer
        # 2. Send specific event
        # 3. Verify observer receives exact event object
        pass


class TestEmailNotificationService(unittest.TestCase):
    """Test the EmailNotificationService implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_email_service = MockEmailService()
        self.notification_service = EmailNotificationService(self.mock_email_service)
    
    def test_sends_welcome_email_on_user_registration(self):
        """Exercise 6: Test welcome email on user registration."""
        # TODO: Test registration email
        # 1. Create user registration event
        # 2. Send to notification service
        # 3. Verify welcome email is sent
        # 4. Verify email content is appropriate
        pass
    
    def test_sends_login_notification_email(self):
        """Exercise 7: Test login notification email."""
        # TODO: Test login email
        # 1. Create user login event
        # 2. Send to notification service
        # 3. Verify login notification email is sent
        pass
    
    def test_sends_order_confirmation_email(self):
        """Exercise 8: Test order confirmation email."""
        # TODO: Test order email
        # 1. Create order created event
        # 2. Send to notification service
        # 3. Verify order confirmation email is sent
        pass
    
    def test_ignores_irrelevant_events(self):
        """Exercise 9: Test that service ignores events it doesn't handle."""
        # TODO: Test event filtering
        # 1. Send events that shouldn't trigger emails
        # 2. Verify no emails are sent
        pass


class TestAuditLogger(unittest.TestCase):
    """Test the AuditLogger implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.audit_logger = AuditLogger("test_audit.log")
    
    def test_logs_all_events(self):
        """Exercise 10: Test that all events are logged."""
        # TODO: Test comprehensive logging
        # 1. Send various event types
        # 2. Verify all events are logged
        # 3. Verify log format is consistent
        pass
    
    def test_log_contains_event_details(self):
        """Exercise 11: Test that logs contain complete event information."""
        # TODO: Test log content
        # 1. Send event with specific data
        # 2. Verify logged entry contains all event details
        pass


class TestMetricsCollector(unittest.TestCase):
    """Test the MetricsCollector implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.metrics_collector = MetricsCollector()
    
    def test_counts_events_by_type(self):
        """Exercise 12: Test event counting by type."""
        # TODO: Test metrics collection
        # 1. Send multiple events of different types
        # 2. Verify counts are accurate for each type
        pass
    
    def test_tracks_total_events(self):
        """Exercise 13: Test total event tracking."""
        # TODO: Test total counting
        # 1. Send various events
        # 2. Verify total count is correct
        pass


class TestIntegratedEventSystem(unittest.TestCase):
    """Test the complete integrated event system."""
    
    def setUp(self):
        """Set up complete system for integration testing."""
        self.publisher = EventPublisher()
        self.email_service = EmailNotificationService()
        self.audit_logger = AuditLogger()
        self.metrics_collector = MetricsCollector()
        self.user_service = UserService(self.publisher)
        self.order_service = OrderService(self.publisher)
        
        # Subscribe all observers
        self.publisher.subscribe(self.email_service)
        self.publisher.subscribe(self.audit_logger)
        self.publisher.subscribe(self.metrics_collector)
    
    def test_user_registration_workflow(self):
        """Exercise 14: Test complete user registration workflow."""
        # TODO: Test end-to-end user registration
        # 1. Register a user
        # 2. Verify event is published
        # 3. Verify all observers are notified
        # 4. Verify email is sent
        # 5. Verify event is logged
        # 6. Verify metrics are updated
        pass
    
    def test_order_lifecycle_workflow(self):
        """Exercise 15: Test complete order lifecycle."""
        # TODO: Test end-to-end order workflow
        # 1. Create order
        # 2. Complete order
        # 3. Verify events are published for each step
        # 4. Verify all observers handle events appropriately
        pass
    
    def test_observer_isolation(self):
        """Exercise 16: Test that observer failures don't affect others."""
        # TODO: Test fault isolation
        # 1. Mock one observer to raise exception
        # 2. Send event
        # 3. Verify other observers still receive notifications
        # 4. Verify system continues to function
        pass
    
    def test_unsubscribe_during_notification(self):
        """Exercise 17: Test unsubscribing during event notification."""
        # TODO: Test edge case handling
        # 1. Subscribe multiple observers
        # 2. Have one observer unsubscribe itself during notification
        # 3. Verify system handles this gracefully
        pass


class TestObserverPatternWithMocks(unittest.TestCase):
    """Test observer pattern using mocks and advanced testing techniques."""
    
    def test_observer_call_order(self):
        """Exercise 18: Test that observers are called in correct order."""
        # TODO: Test notification order
        # 1. Subscribe observers with specific priorities
        # 2. Send event
        # 3. Verify observers are called in expected order
        pass
    
    def test_observer_receives_event_copy(self):
        """Exercise 19: Test that observers receive immutable event data."""
        # TODO: Test data immutability
        # 1. Send event to observer
        # 2. Have observer attempt to modify event
        # 3. Verify original event is unchanged
        pass
    
    @patch('time.time')
    def test_event_timing(self, mock_time):
        """Exercise 20: Test event timing and sequencing."""
        # TODO: Test with time mocking
        # 1. Mock time.time() to return specific values
        # 2. Send events
        # 3. Verify event timestamps are correct
        # 4. Verify event ordering
        pass


# Reference Implementation for Solutions
class EventPublisherSolution(Subject):
    """Complete EventPublisher implementation for reference."""
    
    def __init__(self):
        self._observers = {}  # event_type -> list of observers
        self._global_observers = []  # observers for all events
    
    def subscribe(self, observer: Observer, event_type: Optional[EventType] = None) -> None:
        if event_type is None:
            if observer not in self._global_observers:
                self._global_observers.append(observer)
        else:
            if event_type not in self._observers:
                self._observers[event_type] = []
            if observer not in self._observers[event_type]:
                self._observers[event_type].append(observer)
    
    def unsubscribe(self, observer: Observer, event_type: Optional[EventType] = None) -> None:
        if event_type is None:
            if observer in self._global_observers:
                self._global_observers.remove(observer)
            # Also remove from all specific event types
            for observers in self._observers.values():
                if observer in observers:
                    observers.remove(observer)
        else:
            if event_type in self._observers and observer in self._observers[event_type]:
                self._observers[event_type].remove(observer)
    
    def notify(self, event: Event) -> None:
        # Notify global observers
        for observer in self._global_observers:
            try:
                observer.update(event)
            except Exception as e:
                # Log error but don't stop other notifications
                print(f"Error notifying observer: {e}")
        
        # Notify specific event type observers
        if event.event_type in self._observers:
            for observer in self._observers[event.event_type]:
                try:
                    observer.update(event)
                except Exception as e:
                    print(f"Error notifying observer: {e}")
    
    def get_observer_count(self, event_type: Optional[EventType] = None) -> int:
        if event_type is None:
            total = len(self._global_observers)
            for observers in self._observers.values():
                total += len(observers)
            return total
        else:
            return len(self._observers.get(event_type, []))


def run_observer_pattern_tests():
    """Run all observer pattern tests."""
    print("Observer Pattern Testing Exercise")
    print("=" * 50)
    print("Complete the TODO exercises in the test classes.")
    print("Test the observer pattern implementation thoroughly.")
    print("Focus on behavior, notifications, and edge cases.")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestEventPublisher))
    suite.addTest(unittest.makeSuite(TestEmailNotificationService))
    suite.addTest(unittest.makeSuite(TestAuditLogger))
    suite.addTest(unittest.makeSuite(TestMetricsCollector))
    suite.addTest(unittest.makeSuite(TestIntegratedEventSystem))
    suite.addTest(unittest.makeSuite(TestObserverPatternWithMocks))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    run_observer_pattern_tests()