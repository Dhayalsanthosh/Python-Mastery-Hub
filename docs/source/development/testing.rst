# File Location: docs/source/development/testing.rst

Testing Guide
=============

This comprehensive testing guide covers all aspects of testing in Python Mastery Hub, from unit tests to end-to-end testing, performance testing, and quality assurance practices.

.. note::
   Our testing philosophy emphasizes confidence, maintainability, and fast feedback. 
   We follow the testing pyramid principle with a strong foundation of unit tests.

Testing Philosophy and Strategy
------------------------------

Testing Principles
~~~~~~~~~~~~~~~~~

**1. Test Pyramid Structure**

.. code-block:: text

                    ┌─────────────────┐
                    │   E2E Tests     │  ← 5-10% (High confidence, slow)
                    │   (Playwright)  │
                    └─────────────────┘
                           │
               ┌─────────────────────────┐
               │  Integration Tests      │  ← 15-25% (Medium confidence, medium speed)
               │  (FastAPI TestClient)   │
               └─────────────────────────┘
                           │
          ┌─────────────────────────────────┐
          │      Unit Tests                 │  ← 70-80% (Fast, isolated, numerous)
          │   (pytest + mocks/fakes)       │
          └─────────────────────────────────┘

**2. Test Quality Metrics**

- **Coverage Target**: Minimum 80% line coverage, 90% for critical paths
- **Speed Target**: Unit tests < 1s total, integration tests < 30s
- **Reliability**: Tests should be deterministic and not flaky
- **Maintainability**: Tests should be readable and easy to update

**3. Testing Scope**

.. list-table:: Testing Scope by Layer
   :header-rows: 1
   :widths: 30 35 35

   * - Test Type
     - What to Test
     - What NOT to Test
   * - Unit Tests
     - Business logic, algorithms, validations
     - Database queries, HTTP calls, file I/O
   * - Integration Tests
     - API endpoints, database operations, service interactions
     - UI rendering, external service responses
   * - E2E Tests
     - Complete user workflows, critical user journeys
     - Edge cases, error handling, performance

Test Environment Setup
----------------------

Development Environment
~~~~~~~~~~~~~~~~~~~~~~~

**Install Testing Dependencies:**

.. code-block:: bash

   # Install all development dependencies
   pip install -e ".[dev]"
   
   # Or install testing dependencies specifically
   pip install pytest pytest-asyncio pytest-cov pytest-mock
   pip install httpx # For FastAPI testing
   pip install factory-boy # For test data generation
   pip install faker # For fake data generation

**Configuration:**

.. code-block:: ini

   # pytest.ini
   [tool:pytest]
   testpaths = tests
   python_files = test_*.py
   python_classes = Test*
   python_functions = test_*
   addopts = 
       --strict-markers
       --strict-config
       --cov=src/python_mastery_hub
       --cov-report=html
       --cov-report=term-missing
       --cov-fail-under=80
   markers =
       unit: Unit tests
       integration: Integration tests
       e2e: End-to-end tests
       slow: Tests that take more than 1 second
       database: Tests that require database
       external: Tests that call external services

**Test Database Setup:**

.. code-block:: python

   # tests/conftest.py
   import pytest
   import asyncio
   from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
   from sqlalchemy.orm import sessionmaker
   from python_mastery_hub.web.config.database import Base

   @pytest.fixture(scope="session")
   def event_loop():
       """Create an instance of the default event loop for the test session."""
       loop = asyncio.get_event_loop_policy().new_event_loop()
       yield loop
       loop.close()

   @pytest.fixture(scope="session")
   async def test_engine():
       """Create test database engine."""
       engine = create_async_engine(
           "sqlite+aiosqlite:///./test.db",
           echo=False
       )
       
       async with engine.begin() as conn:
           await conn.run_sync(Base.metadata.create_all)
       
       yield engine
       
       async with engine.begin() as conn:
           await conn.run_sync(Base.metadata.drop_all)
       
       await engine.dispose()

   @pytest.fixture
   async def db_session(test_engine):
       """Create clean database session for each test."""
       async_session = sessionmaker(
           test_engine, class_=AsyncSession, expire_on_commit=False
       )
       
       async with async_session() as session:
           yield session
           await session.rollback()

Unit Testing
------------

Business Logic Testing
~~~~~~~~~~~~~~~~~~~~~~

**Testing Core Domain Models:**

.. code-block:: python

   # tests/unit/core/test_user_domain.py
   import pytest
   from datetime import datetime
   from python_mastery_hub.core.domain.user import User, UserProgress
   from python_mastery_hub.core.domain.exercise import Exercise, ExerciseResult

   class TestUser:
       def test_user_creation(self):
           """Test user creation with valid data."""
           user = User(
               user_id="123",
               email="test@example.com",
               full_name="Test User"
           )
           
           assert user.user_id == "123"
           assert user.email == "test@example.com"
           assert user.full_name == "Test User"
           assert user.created_at is not None
           assert len(user.achievements) == 0

       def test_complete_exercise_success(self):
           """Test successful exercise completion."""
           user = User(user_id="123", email="test@example.com")
           exercise = Exercise(
               exercise_id="ex1",
               title="Basic Python",
               content="Write a hello world function"
           )
           
           result = user.complete_exercise(exercise, "def hello(): return 'Hello World'")
           
           assert result.success is True
           assert result.score > 0
           assert len(user.progress) == 1
           assert user.progress[0].exercise_id == "ex1"

       def test_complete_exercise_failure(self):
           """Test exercise completion with incorrect solution."""
           user = User(user_id="123", email="test@example.com")
           exercise = Exercise(
               exercise_id="ex1",
               title="Basic Python",
               content="Write a hello world function"
           )
           
           result = user.complete_exercise(exercise, "invalid python code")
           
           assert result.success is False
           assert result.score == 0
           assert result.error is not None

**Testing Service Layer:**

.. code-block:: python

   # tests/unit/core/services/test_learning_service.py
   import pytest
   from unittest.mock import Mock, AsyncMock
   from python_mastery_hub.core.services.learning_service import LearningService
   from python_mastery_hub.core.domain.user import User
   from python_mastery_hub.core.domain.exercise import Exercise

   class TestLearningService:
       @pytest.fixture
       def mock_user_repo(self):
           return Mock()

       @pytest.fixture  
       def mock_exercise_repo(self):
           return Mock()

       @pytest.fixture
       def mock_event_bus(self):
           return Mock()

       @pytest.fixture
       def learning_service(self, mock_user_repo, mock_exercise_repo, mock_event_bus):
           return LearningService(
               user_repo=mock_user_repo,
               exercise_repo=mock_exercise_repo,
               event_bus=mock_event_bus
           )

       async def test_submit_exercise_success(
           self, 
           learning_service, 
           mock_user_repo, 
           mock_exercise_repo,
           mock_event_bus
       ):
           """Test successful exercise submission."""
           # Arrange
           user = User(user_id="123", email="test@example.com")
           exercise = Exercise(exercise_id="ex1", title="Test Exercise")
           code = "def hello(): return 'Hello World'"
           
           mock_user_repo.get_user = AsyncMock(return_value=user)
           mock_exercise_repo.get_exercise = AsyncMock(return_value=exercise)
           mock_user_repo.save_user = AsyncMock()
           mock_event_bus.publish = AsyncMock()
           
           # Act
           result = await learning_service.submit_exercise("123", "ex1", code)
           
           # Assert
           assert result.success is True
           mock_user_repo.get_user.assert_called_once_with("123")
           mock_exercise_repo.get_exercise.assert_called_once_with("ex1")
           mock_user_repo.save_user.assert_called_once_with(user)
           mock_event_bus.publish.assert_called_once()

**Testing Utilities and Helpers:**

.. code-block:: python

   # tests/unit/utils/test_validation.py
   import pytest
   from python_mastery_hub.utils.validation import (
       validate_email, 
       validate_password, 
       ValidationError
   )

   class TestValidation:
       def test_validate_email_success(self):
           """Test email validation with valid emails."""
           valid_emails = [
               "test@example.com",
               "user.name+tag@domain.co.uk",
               "firstname.lastname@subdomain.domain.com"
           ]
           
           for email in valid_emails:
               assert validate_email(email) is True

       def test_validate_email_failure(self):
           """Test email validation with invalid emails."""
           invalid_emails = [
               "invalid-email",
               "@domain.com",
               "user@",
               "spaces @domain.com"
           ]
           
           for email in invalid_emails:
               with pytest.raises(ValidationError):
                   validate_email(email)

       @pytest.mark.parametrize("password,expected", [
           ("Str0ng!Pass", True),
           ("weak", False),
           ("NoNumbers!", False),
           ("nonumbers123", False),
           ("NOLOWERCASE123!", False)
       ])
       def test_validate_password(self, password, expected):
           """Test password validation with various inputs."""
           if expected:
               assert validate_password(password) is True
           else:
               with pytest.raises(ValidationError):
                   validate_password(password)

Test Data Factories
~~~~~~~~~~~~~~~~~~

**Using Factory Boy for Test Data:**

.. code-block:: python

   # tests/factories.py
   import factory
   from factory import fuzzy
   from datetime import datetime, timedelta
   from python_mastery_hub.core.domain.user import User
   from python_mastery_hub.core.domain.exercise import Exercise

   class UserFactory(factory.Factory):
       class Meta:
           model = User

       user_id = factory.Sequence(lambda n: f"user_{n}")
       email = factory.LazyAttribute(lambda obj: f"{obj.user_id}@example.com")
       full_name = factory.Faker("name")
       created_at = factory.LazyFunction(datetime.utcnow)
       is_active = True

   class ExerciseFactory(factory.Factory):
       class Meta:
           model = Exercise

       exercise_id = factory.Sequence(lambda n: f"exercise_{n}")
       title = factory.Faker("sentence", nb_words=3)
       description = factory.Faker("text", max_nb_chars=200)
       difficulty_level = fuzzy.FuzzyInteger(1, 5)
       category = fuzzy.FuzzyChoice(["basics", "algorithms", "data_structures"])

   # Usage in tests
   class TestUserService:
       def test_create_user_analytics(self):
           user = UserFactory()
           exercises = ExerciseFactory.create_batch(5)
           
           # Test logic here
           assert len(exercises) == 5

Integration Testing
------------------

API Endpoint Testing
~~~~~~~~~~~~~~~~~~~

**FastAPI Test Client Setup:**

.. code-block:: python

   # tests/integration/conftest.py
   import pytest
   from httpx import AsyncClient
   from python_mastery_hub.web.main import app
   from python_mastery_hub.web.config.database import get_db

   @pytest.fixture
   async def test_client(db_session):
       """Create test client with database dependency override."""
       
       async def override_get_db():
           yield db_session
       
       app.dependency_overrides[get_db] = override_get_db
       
       async with AsyncClient(app=app, base_url="http://test") as client:
           yield client
       
       app.dependency_overrides.clear()

**Authentication Testing:**

.. code-block:: python

   # tests/integration/api/test_auth.py
   import pytest
   from httpx import AsyncClient

   class TestAuthAPI:
       async def test_register_user_success(self, test_client: AsyncClient):
           """Test successful user registration."""
           user_data = {
               "email": "newuser@example.com",
               "password": "SecurePass123!",
               "full_name": "New User"
           }
           
           response = await test_client.post("/api/auth/register", json=user_data)
           
           assert response.status_code == 201
           data = response.json()
           assert data["email"] == user_data["email"]
           assert data["full_name"] == user_data["full_name"]
           assert "user_id" in data
           assert "password" not in data  # Password should not be returned

       async def test_register_user_duplicate_email(self, test_client: AsyncClient):
           """Test registration with existing email."""
           user_data = {
               "email": "duplicate@example.com",
               "password": "SecurePass123!",
               "full_name": "First User"
           }
           
           # Register first user
           await test_client.post("/api/auth/register", json=user_data)
           
           # Try to register again with same email
           response = await test_client.post("/api/auth/register", json=user_data)
           
           assert response.status_code == 400
           data = response.json()
           assert "email already registered" in data["detail"].lower()

       async def test_login_success(self, test_client: AsyncClient):
           """Test successful login."""
           # First register a user
           user_data = {
               "email": "logintest@example.com",
               "password": "SecurePass123!",
               "full_name": "Login Test"
           }
           await test_client.post("/api/auth/register", json=user_data)
           
           # Then login
           login_data = {
               "email": "logintest@example.com",
               "password": "SecurePass123!"
           }
           response = await test_client.post("/api/auth/login", json=login_data)
           
           assert response.status_code == 200
           data = response.json()
           assert "access_token" in data
           assert "refresh_token" in data
           assert data["token_type"] == "bearer"

**Exercise API Testing:**

.. code-block:: python

   # tests/integration/api/test_exercises.py
   import pytest
   from httpx import AsyncClient
   from tests.factories import UserFactory, ExerciseFactory

   class TestExerciseAPI:
       @pytest.fixture
       async def authenticated_client(self, test_client, db_session):
           """Create authenticated test client."""
           # Create user
           user = UserFactory()
           db_session.add(user)
           await db_session.commit()
           
           # Login to get token
           login_data = {
               "email": user.email,
               "password": "password123"
           }
           response = await test_client.post("/api/auth/login", json=login_data)
           token = response.json()["access_token"]
           
           # Add auth header
           test_client.headers.update({"Authorization": f"Bearer {token}"})
           return test_client

       async def test_get_exercises_list(self, authenticated_client):
           """Test retrieving list of exercises."""
           response = await authenticated_client.get("/api/exercises/")
           
           assert response.status_code == 200
           data = response.json()
           assert "exercises" in data
           assert "total" in data
           assert isinstance(data["exercises"], list)

       async def test_submit_exercise_success(self, authenticated_client, db_session):
           """Test successful exercise submission."""
           # Create exercise
           exercise = ExerciseFactory()
           db_session.add(exercise)
           await db_session.commit()
           
           submission_data = {
               "code": "def hello_world():\n    return 'Hello, World!'",
               "language": "python"
           }
           
           response = await authenticated_client.post(
               f"/api/exercises/{exercise.exercise_id}/submit",
               json=submission_data
           )
           
           assert response.status_code == 200
           data = response.json()
           assert "result" in data
           assert "execution_time" in data
           assert data["result"]["success"] is True

Database Integration Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Repository Testing:**

.. code-block:: python

   # tests/integration/repositories/test_user_repository.py
   import pytest
   from python_mastery_hub.infrastructure.database.user_repository import SQLUserRepository
   from tests.factories import UserFactory

   class TestSQLUserRepository:
       @pytest.fixture
       def user_repository(self, db_session):
           return SQLUserRepository(db_session)

       async def test_create_user(self, user_repository, db_session):
           """Test creating a user in database."""
           user_data = {
               "email": "test@example.com",
               "password_hash": "hashed_password",
               "full_name": "Test User"
           }
           
           user = await user_repository.create_user(user_data)
           
           assert user.user_id is not None
           assert user.email == "test@example.com"
           assert user.full_name == "Test User"
           
           # Verify user exists in database
           retrieved_user = await user_repository.get_user(user.user_id)
           assert retrieved_user.email == user.email

       async def test_update_user_progress(self, user_repository, db_session):
           """Test updating user progress."""
           user = UserFactory()
           await user_repository.create_user(user)
           
           progress_data = {
               "exercise_id": "ex1",
               "score": 85,
               "completed_at": datetime.utcnow()
           }
           
           await user_repository.update_progress(user.user_id, progress_data)
           
           # Verify progress was saved
           user_with_progress = await user_repository.get_user_with_progress(user.user_id)
           assert len(user_with_progress.progress) == 1
           assert user_with_progress.progress[0].score == 85

End-to-End Testing
-----------------

Browser Testing with Playwright
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Setup and Configuration:**

.. code-block:: python

   # tests/e2e/conftest.py
   import pytest
   from playwright.async_api import async_playwright

   @pytest.fixture(scope="session")
   async def browser():
       """Create browser instance for E2E tests."""
       async with async_playwright() as p:
           browser = await p.chromium.launch(headless=True)
           yield browser
           await browser.close()

   @pytest.fixture
   async def page(browser):
       """Create new page for each test."""
       context = await browser.new_context()
       page = await context.new_page()
       yield page
       await context.close()

**User Journey Testing:**

.. code-block:: python

   # tests/e2e/test_user_journey.py
   import pytest
   from playwright.async_api import Page, expect

   class TestUserJourney:
       async def test_complete_learning_workflow(self, page: Page):
           """Test complete user learning workflow."""
           
           # Step 1: Navigate to homepage
           await page.goto("http://localhost:3000")
           await expect(page.locator("h1")).to_contain_text("Python Mastery Hub")
           
           # Step 2: Register new user
           await page.click("text=Sign Up")
           await page.fill('input[name="email"]', "e2e@example.com")
           await page.fill('input[name="password"]', "SecurePass123!")
           await page.fill('input[name="fullName"]', "E2E Test User")
           await page.click('button[type="submit"]')
           
           # Step 3: Verify redirect to dashboard
           await expect(page).to_have_url("http://localhost:3000/dashboard")
           await expect(page.locator("h2")).to_contain_text("Welcome")
           
           # Step 4: Start first exercise
           await page.click("text=Start Learning")
           await page.click("text=Python Basics")
           await page.click("text=Variables and Types")
           
           # Step 5: Complete exercise
           code_editor = page.locator(".monaco-editor")
           await code_editor.click()
           await page.keyboard.type("name = 'Python'\nage = 25")
           await page.click("text=Run Tests")
           
           # Step 6: Verify success
           await expect(page.locator(".test-results")).to_contain_text("All tests passed")
           await page.click("text=Submit Solution")
           
           # Step 7: Check progress update
           await page.goto("http://localhost:3000/progress")
           await expect(page.locator(".progress-bar")).to_have_attribute("value", "1")

       async def test_code_execution_workflow(self, page: Page):
           """Test code execution and feedback workflow."""
           
           # Login and navigate to exercise
           await self._login_user(page, "test@example.com", "password123")
           await page.goto("http://localhost:3000/exercises/basic-functions")
           
           # Test incorrect solution
           await page.fill(".code-editor", "def add(a, b): return a - b")
           await page.click("text=Run Tests")
           
           # Verify error feedback
           await expect(page.locator(".test-failure")).to_be_visible()
           await expect(page.locator(".error-message")).to_contain_text("Expected")
           
           # Test correct solution
           await page.fill(".code-editor", "def add(a, b): return a + b")
           await page.click("text=Run Tests")
           
           # Verify success
           await expect(page.locator(".test-success")).to_be_visible()
           await expect(page.locator(".success-message")).to_contain_text("All tests passed")

       async def _login_user(self, page: Page, email: str, password: str):
           """Helper method to login user."""
           await page.goto("http://localhost:3000/login")
           await page.fill('input[name="email"]', email)
           await page.fill('input[name="password"]', password)
           await page.click('button[type="submit"]')
           await expect(page).to_have_url("http://localhost:3000/dashboard")

Performance Testing
-------------------

Load Testing with Locust
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # tests/performance/locustfile.py
   from locust import HttpUser, task, between
   import json

   class PythonMasteryHubUser(HttpUser):
       wait_time = between(1, 3)
       
       def on_start(self):
           """Login user at start of test."""
           login_data = {
               "email": "loadtest@example.com",
               "password": "password123"
           }
           response = self.client.post("/api/auth/login", json=login_data)
           if response.status_code == 200:
               token = response.json()["access_token"]
               self.client.headers.update({"Authorization": f"Bearer {token}"})

       @task(3)
       def view_exercises(self):
           """Simulate viewing exercises list."""
           self.client.get("/api/exercises/")

       @task(2)
       def view_exercise_detail(self):
           """Simulate viewing exercise details."""
           self.client.get("/api/exercises/python-basics")

       @task(1)
       def submit_exercise(self):
           """Simulate submitting exercise solution."""
           submission_data = {
               "code": "def hello(): return 'Hello World'",
               "language": "python"
           }
           self.client.post(
               "/api/exercises/python-basics/submit",
               json=submission_data
           )

       @task(2)
       def view_progress(self):
           """Simulate viewing progress dashboard."""
           self.client.get("/api/progress/dashboard")

       @task(1)
       def view_leaderboard(self):
           """Simulate viewing leaderboard."""
           self.client.get("/api/progress/leaderboard")

**Running Performance Tests:**

.. code-block:: bash

   # Install locust
   pip install locust
   
   # Run load test
   locust -f tests/performance/locustfile.py --host=http://localhost:8000
   
   # Run headless with specific parameters
   locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
          --users 100 --spawn-rate 10 --run-time 300s --headless

Database Performance Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # tests/performance/test_database_performance.py
   import pytest
   import asyncio
   import time
   from python_mastery_hub.infrastructure.database.user_repository import SQLUserRepository
   from tests.factories import UserFactory

   class TestDatabasePerformance:
       @pytest.mark.slow
       async def test_bulk_user_creation_performance(self, db_session):
           """Test performance of bulk user creation."""
           repository = SQLUserRepository(db_session)
           
           start_time = time.time()
           
           # Create 1000 users
           tasks = []
           for i in range(1000):
               user_data = {
                   "email": f"user{i}@example.com",
                   "password_hash": "hashed_password",
                   "full_name": f"User {i}"
               }
               tasks.append(repository.create_user(user_data))
           
           await asyncio.gather(*tasks)
           
           execution_time = time.time() - start_time
           
           # Should complete in under 10 seconds
           assert execution_time < 10.0
           print(f"Created 1000 users in {execution_time:.2f} seconds")

       @pytest.mark.slow
       async def test_query_performance_with_large_dataset(self, db_session):
           """Test query performance with large dataset."""
           repository = SQLUserRepository(db_session)
           
           # Create test data
           users = [UserFactory() for _ in range(5000)]
           db_session.add_all(users)
           await db_session.commit()
           
           # Test complex query performance
           start_time = time.time()
           
           result = await repository.get_users_with_progress_summary(
               limit=100,
               filters={"min_exercises_completed": 5}
           )
           
           execution_time = time.time() - start_time
           
           # Complex query should complete in under 1 second
           assert execution_time < 1.0
           assert len(result) <= 100

Security Testing
---------------

Authentication and Authorization Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # tests/security/test_auth_security.py
   import pytest
   from httpx import AsyncClient
   from python_mastery_hub.web.main import app

   class TestAuthSecurity:
       async def test_jwt_token_expiry(self, test_client: AsyncClient):
           """Test JWT token expiry handling."""
           # Register and login
           user_data = {
               "email": "security@example.com",
               "password": "SecurePass123!",
               "full_name": "Security Test"
           }
           await test_client.post("/api/auth/register", json=user_data)
           
           login_response = await test_client.post("/api/auth/login", json={
               "email": "security@example.com",
               "password": "SecurePass123!"
           })
           
           token = login_response.json()["access_token"]
           
           # Use token immediately (should work)
           response = await test_client.get(
               "/api/user/profile",
               headers={"Authorization": f"Bearer {token}"}
           )
           assert response.status_code == 200
           
           # Mock token expiry and test
           import jwt
           expired_token = jwt.encode(
               {"sub": "user123", "exp": 0},  # Expired timestamp
               "secret",
               algorithm="HS256"
           )
           
           response = await test_client.get(
               "/api/user/profile",
               headers={"Authorization": f"Bearer {expired_token}"}
           )
           assert response.status_code == 401

       async def test_unauthorized_access_prevention(self, test_client: AsyncClient):
           """Test that protected endpoints require authentication."""
           protected_endpoints = [
               "/api/exercises/submit",
               "/api/user/profile",
               "/api/progress/dashboard",
               "/api/admin/users"
           ]
           
           for endpoint in protected_endpoints:
               response = await test_client.get(endpoint)
               assert response.status_code == 401

       async def test_role_based_access_control(self, test_client: AsyncClient):
           """Test role-based access control."""
           # Create regular user
           user_data = {
               "email": "student@example.com",
               "password": "SecurePass123!",
               "full_name": "Student User"
           }
           await test_client.post("/api/auth/register", json=user_data)
           
           # Login as student
           login_response = await test_client.post("/api/auth/login", json={
               "email": "student@example.com",
               "password": "SecurePass123!"
           })
           student_token = login_response.json()["access_token"]
           
           # Try to access admin endpoint (should fail)
           response = await test_client.get(
               "/api/admin/users",
               headers={"Authorization": f"Bearer {student_token}"}
           )
           assert response.status_code == 403

Input Validation and Injection Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # tests/security/test_input_validation.py
   import pytest
   from httpx import AsyncClient

   class TestInputValidation:
       async def test_sql_injection_prevention(self, test_client: AsyncClient):
           """Test SQL injection prevention."""
           malicious_inputs = [
               "'; DROP TABLE users; --",
               "' OR '1'='1",
               "admin'/*",
               "' UNION SELECT * FROM users --"
           ]
           
           for malicious_input in malicious_inputs:
               response = await test_client.post("/api/auth/login", json={
                   "email": malicious_input,
                   "password": "password"
               })
               # Should return validation error, not 500
               assert response.status_code in [400, 401, 422]

       async def test_xss_prevention(self, test_client: AsyncClient):
           """Test XSS prevention in user inputs."""
           xss_payloads = [
               "<script>alert('xss')</script>",
               "javascript:alert('xss')",
               "<img src=x onerror=alert('xss')>",
               "';alert('xss');//"
           ]
           
           # Register user first
           await test_client.post("/api/auth/register", json={
               "email": "xsstest@example.com",
               "password": "SecurePass123!",
               "full_name": "XSS Test"
           })
           
           # Login to get token
           login_response = await test_client.post("/api/auth/login", json={
               "email": "xsstest@example.com",
               "password": "SecurePass123!"
           })
           token = login_response.json()["access_token"]
           
           for payload in xss_payloads:
               response = await test_client.put(
                   "/api/user/profile",
                   headers={"Authorization": f"Bearer {token}"},
                   json={"full_name": payload}
               )
               
               # Check that payload is sanitized in response
               if response.status_code == 200:
                   data = response.json()
                   assert "<script>" not in data.get("full_name", "")
                   assert "javascript:" not in data.get("full_name", "")

       async def test_code_injection_prevention(self, test_client: AsyncClient):
           """Test code injection prevention in exercise submissions."""
           # Login user
           await test_client.post("/api/auth/register", json={
               "email": "codetest@example.com",
               "password": "SecurePass123!",
               "full_name": "Code Test"
           })
           
           login_response = await test_client.post("/api/auth/login", json={
               "email": "codetest@example.com",
               "password": "SecurePass123!"
           })
           token = login_response.json()["access_token"]
           
           malicious_code = [
               "import os; os.system('rm -rf /')",
               "exec('import subprocess; subprocess.call([\"rm\", \"-rf\", \"/\"])')",
               "__import__('os').system('cat /etc/passwd')",
               "open('/etc/passwd').read()"
           ]
           
           for code in malicious_code:
               response = await test_client.post(
                   "/api/exercises/python-basics/submit",
                   headers={"Authorization": f"Bearer {token}"},
                   json={"code": code}
               )
               
               # Code should be safely executed in sandbox
               assert response.status_code in [200, 400]
               if response.status_code == 200:
                   result = response.json()
                   # Should not execute dangerous operations
                   assert "error" in result or not result.get("success", True)

Test Coverage and Quality
-------------------------

Coverage Analysis
~~~~~~~~~~~~~~~~

.. code-block:: python

   # tests/coverage/test_coverage_analysis.py
   import pytest
   import coverage
   import subprocess
   import sys

   class TestCoverage:
       def test_minimum_coverage_requirement(self):
           """Ensure minimum test coverage is met."""
           # Run coverage analysis
           result = subprocess.run([
               sys.executable, "-m", "pytest", 
               "--cov=src/python_mastery_hub",
               "--cov-report=json",
               "--quiet"
           ], capture_output=True, text=True)
           
           # Read coverage report
           with open("coverage.json") as f:
               coverage_data = json.load(f)
           
           total_coverage = coverage_data["totals"]["percent_covered"]
           
           # Assert minimum coverage
           assert total_coverage >= 80.0, f"Coverage {total_coverage}% is below 80%"

       def test_critical_path_coverage(self):
           """Ensure critical paths have high coverage."""
           critical_modules = [
               "src/python_mastery_hub/core/services/learning_service.py",
               "src/python_mastery_hub/core/services/auth_service.py",
               "src/python_mastery_hub/web/api/exercises.py",
               "src/python_mastery_hub/infrastructure/code_executor.py"
           ]
           
           with open("coverage.json") as f:
               coverage_data = json.load(f)
           
           for module in critical_modules:
               if module in coverage_data["files"]:
                   module_coverage = coverage_data["files"][module]["summary"]["percent_covered"]
                   assert module_coverage >= 90.0, f"{module} coverage {module_coverage}% is below 90%"

Test Quality Metrics
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # tests/quality/test_quality_metrics.py
   import pytest
   import ast
   import os
   from pathlib import Path

   class TestQuality:
       def test_no_skipped_tests(self):
           """Ensure no tests are skipped without good reason."""
           test_files = Path("tests").rglob("test_*.py")
           skipped_tests = []
           
           for test_file in test_files:
               with open(test_file) as f:
                   content = f.read()
                   if "@pytest.mark.skip" in content:
                       skipped_tests.append(str(test_file))
           
           # Allow some skipped tests but investigate if too many
           assert len(skipped_tests) <= 5, f"Too many skipped tests: {skipped_tests}"

       def test_test_isolation(self):
           """Ensure tests don't depend on each other."""
           # Run tests in random order to catch dependencies
           result = subprocess.run([
               sys.executable, "-m", "pytest",
               "--random-order",
               "--quiet"
           ], capture_output=True, text=True)
           
           assert result.returncode == 0, "Tests failed when run in random order"

       def test_no_print_statements_in_tests(self):
           """Ensure tests use proper logging instead of print."""
           test_files = Path("tests").rglob("test_*.py")
           files_with_prints = []
           
           for test_file in test_files:
               with open(test_file) as f:
                   tree = ast.parse(f.read())
                   
               for node in ast.walk(tree):
                   if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                       if node.func.id == "print":
                           files_with_prints.append(str(test_file))
                           break
           
           assert len(files_with_prints) == 0, f"Tests contain print statements: {files_with_prints}"

Continuous Integration Testing
-----------------------------

GitHub Actions Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # .github/workflows/test.yml
   name: Test Suite

   on:
     push:
       branches: [ main, develop ]
     pull_request:
       branches: [ main ]

   jobs:
     test:
       runs-on: ubuntu-latest
       strategy:
         matrix:
           python-version: [3.9, 3.10, 3.11]

       services:
         postgres:
           image: postgres:13
           env:
             POSTGRES_PASSWORD: postgres
             POSTGRES_DB: test_db
           options: >-
             --health-cmd pg_isready
             --health-interval 10s
             --health-timeout 5s
             --health-retries 5
         redis:
           image: redis:6
           options: >-
             --health-cmd "redis-cli ping"
             --health-interval 10s
             --health-timeout 5s
             --health-retries 5

       steps:
       - uses: actions/checkout@v3

       - name: Set up Python ${{ matrix.python-version }}
         uses: actions/setup-python@v3
         with:
           python-version: ${{ matrix.python-version }}

       - name: Install dependencies
         run: |
           python -m pip install --upgrade pip
           pip install -e ".[dev]"

       - name: Run pre-commit hooks
         run: pre-commit run --all-files

       - name: Run unit tests
         run: |
           pytest tests/unit/ -v --cov=src/python_mastery_hub --cov-report=xml

       - name: Run integration tests
         run: |
           pytest tests/integration/ -v
         env:
           DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
           REDIS_URL: redis://localhost:6379

       - name: Run security tests
         run: |
           pytest tests/security/ -v

       - name: Upload coverage to Codecov
         uses: codecov/codecov-action@v3
         with:
           file: ./coverage.xml

   e2e-tests:
     runs-on: ubuntu-latest
     needs: test

     steps:
     - uses: actions/checkout@v3

     - name: Set up Python
       uses: actions/setup-python@v3
       with:
         python-version: 3.9

     - name: Set up Node.js
       uses: actions/setup-node@v3
       with:
         node-version: 16

     - name: Install Python dependencies
       run: |
         pip install -e ".[dev]"

     - name: Install frontend dependencies
       run: |
         cd frontend
         npm install

     - name: Install Playwright
       run: |
         playwright install

     - name: Start application
       run: |
         python -m python_mastery_hub.web.main &
         cd frontend && npm start &
         sleep 30  # Wait for services to start

     - name: Run E2E tests
       run: |
         pytest tests/e2e/ -v

Testing Best Practices
----------------------

Test Organization
~~~~~~~~~~~~~~~~

**File Naming and Structure:**

.. code-block:: text

   tests/
   ├── unit/                    # Unit tests (fast, isolated)
   │   ├── core/               # Core business logic tests
   │   ├── web/                # Web layer tests
   │   └── utils/              # Utility function tests
   ├── integration/            # Integration tests (medium speed)
   │   ├── api/                # API endpoint tests
   │   ├── database/           # Database integration tests
   │   └── services/           # Service integration tests
   ├── e2e/                    # End-to-end tests (slow, high confidence)
   │   ├── user_journeys/      # Complete user workflow tests
   │   └── critical_paths/     # Critical business process tests
   ├── performance/            # Performance and load tests
   ├── security/               # Security and penetration tests
   ├── fixtures/               # Shared test data and fixtures
   └── conftest.py            # Global pytest configuration

**Test Naming Conventions:**

.. code-block:: python

   # Good test names - descriptive and specific
   def test_user_can_complete_exercise_with_correct_solution():
       pass

   def test_authentication_fails_with_invalid_credentials():
       pass

   def test_exercise_submission_updates_user_progress():
       pass

   # Bad test names - vague and unclear
   def test_user():
       pass

   def test_auth():
       pass

   def test_exercise():
       pass

**Test Structure (Arrange-Act-Assert):**

.. code-block:: python

   async def test_submit_exercise_success():
       # Arrange
       user = UserFactory()
       exercise = ExerciseFactory()
       service = LearningService(mock_repo, mock_event_bus)
       
       # Act
       result = await service.submit_exercise(
           user.user_id, 
           exercise.exercise_id, 
           "valid python code"
       )
       
       # Assert
       assert result.success is True
       assert result.score > 0
       assert user.progress[0].exercise_id == exercise.exercise_id

Debugging and Troubleshooting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Debug Mode Configuration:**

.. code-block:: python

   # pytest.ini - Debug configuration
   [tool:pytest]
   addopts = 
       --tb=short           # Shorter traceback format
       --strict-markers     # Strict marker checking
       --strict-config      # Strict config checking
       -v                   # Verbose output
       --no-header          # No pytest header
       --disable-warnings   # Disable warnings in normal runs

   # For debugging specific tests
   addopts = --tb=long --no-cov -s --log-cli-level=DEBUG

**Common Debugging Techniques:**

.. code-block:: python

   import pytest

   def test_complex_logic():
       # Use pytest.set_trace() for debugging
       result = complex_calculation()
       pytest.set_trace()  # Debugger will stop here
       assert result == expected_value

   # Use logging for debugging
   import logging
   logger = logging.getLogger(__name__)

   def test_with_logging():
       logger.debug("Starting test")
       result = function_under_test()
       logger.debug(f"Result: {result}")
       assert result is not None

**Fixing Flaky Tests:**

.. code-block:: python

   # Bad - time-dependent test
   def test_user_session_expiry():
       user = login_user()
       time.sleep(61)  # Wait for session to expire
       assert user.is_session_valid() is False

   # Good - explicit time manipulation
   def test_user_session_expiry():
       with freeze_time("2023-01-01 12:00:00") as frozen_time:
           user = login_user()
           frozen_time.tick(delta=timedelta(minutes=61))
           assert user.is_session_valid() is False

   # Bad - order-dependent test
   def test_user_count():
       users = get_all_users()
       assert len(users) == 5  # Depends on other tests

   # Good - isolated test
   def test_user_count(clean_database):
       UserFactory.create_batch(5)
       users = get_all_users()
       assert len(users) == 5

Test Documentation
~~~~~~~~~~~~~~~~~

**Docstring Standards:**

.. code-block:: python

   def test_complex_business_logic():
       """
       Test that complex business logic handles edge cases correctly.
       
       This test verifies that when a user submits an exercise solution:
       1. The code is safely executed in a sandbox
       2. Test cases are run against the solution
       3. Progress is updated based on the results
       4. Achievements are checked and awarded if applicable
       5. Events are published for other services to react
       
       Edge cases tested:
       - Empty code submission
       - Code with syntax errors
       - Code that times out
       - Code that uses too much memory
       """
       pass

**Test Documentation in README:**

.. code-block:: markdown

   # Testing Guide

   ## Running Tests

   ```bash
   # Run all tests
   pytest

   # Run specific test categories
   pytest tests/unit/          # Unit tests only
   pytest tests/integration/   # Integration tests only
   pytest tests/e2e/          # End-to-end tests only

   # Run tests with coverage
   pytest --cov=src/python_mastery_hub --cov-report=html

   # Run tests in parallel
   pytest -n auto

   # Run specific test
   pytest tests/unit/core/test_user.py::TestUser::test_create_user
   ```

   ## Test Categories

   - **Unit Tests**: Fast, isolated tests for individual functions and classes
   - **Integration Tests**: Tests that verify component interactions
   - **E2E Tests**: Full user workflow tests using browser automation
   - **Performance Tests**: Load and stress testing
   - **Security Tests**: Authentication, authorization, and input validation tests

This comprehensive testing guide ensures high-quality, maintainable code with excellent test coverage and confidence in the Python Mastery Hub platform.