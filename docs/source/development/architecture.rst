# File Location: docs/source/development/architecture.rst

System Architecture
===================

This document provides a comprehensive overview of Python Mastery Hub's architecture, design patterns, and technical decisions. Understanding this architecture is essential for contributors and developers working on the platform.

.. note::
   This document assumes familiarity with modern web development concepts, 
   Python frameworks, and software architecture patterns.

Architecture Overview
--------------------

Python Mastery Hub follows a **microservices-inspired modular monolith** architecture that provides the benefits of modular design while maintaining the simplicity of a single deployable unit.

High-Level Architecture
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
   │   Web Client    │    │   Mobile App    │    │   CLI Client    │
   │   (React)       │    │   (React Native)│    │   (Python)      │
   └─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
             │                      │                      │
             └──────────────────────┼──────────────────────┘
                                    │
                              ┌─────▼─────┐
                              │ API Gateway│
                              │ (FastAPI)  │
                              └─────┬─────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │                         │                          │
    ┌────▼────┐              ┌─────▼─────┐              ┌─────▼─────┐
    │  Auth   │              │  Learning │              │  Admin    │
    │ Service │              │  Service  │              │  Service  │
    └────┬────┘              └─────┬─────┘              └─────┬─────┘
         │                         │                          │
         └──────────────────┬──────┴──────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Shared Core   │
                    │   Services     │
                    └───────┬────────┘
                            │
      ┌─────────────────────┼─────────────────────┐
      │                     │                     │
 ┌────▼────┐          ┌─────▼─────┐         ┌─────▼─────┐
 │Database │          │   Cache   │         │   Queue   │
 │(PostgreSQL)        │  (Redis)  │         │ (Celery)  │
 └─────────┘          └───────────┘         └───────────┘

Core Principles
~~~~~~~~~~~~~~~

**1. Domain-Driven Design (DDD)**

The system is organized around business domains rather than technical layers:

- **User Management**: Authentication, profiles, preferences
- **Learning Content**: Courses, lessons, exercises, assessments
- **Progress Tracking**: Achievements, analytics, recommendations
- **Community**: Forums, peer review, collaboration
- **Administration**: Content management, user administration

**2. Separation of Concerns**

Clear boundaries between different responsibilities:

- **Presentation Layer**: UI components and API endpoints
- **Business Logic Layer**: Core domain logic and workflows
- **Data Access Layer**: Database operations and caching
- **Infrastructure Layer**: External services and utilities

**3. Dependency Inversion**

High-level modules don't depend on low-level modules:

.. code-block:: python

   # Abstract interface
   class UserRepository(ABC):
       async def get_user(self, user_id: str) -> User:
           pass
   
   # Business logic depends on abstraction
   class UserService:
       def __init__(self, user_repo: UserRepository):
           self.user_repo = user_repo
   
   # Concrete implementation
   class SQLUserRepository(UserRepository):
       async def get_user(self, user_id: str) -> User:
           # Database implementation
           pass

**4. Event-Driven Architecture**

Loose coupling through domain events:

.. code-block:: python

   # Event definition
   class UserCompletedExerciseEvent:
       user_id: str
       exercise_id: str
       score: int
       completed_at: datetime
   
   # Event handlers
   async def update_progress(event: UserCompletedExerciseEvent):
       # Update user progress
       pass
   
   async def check_achievements(event: UserCompletedExerciseEvent):
       # Check for new achievements
       pass

Directory Structure and Organization
-----------------------------------

Project Structure Deep Dive
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   python_mastery_hub/
   ├── src/python_mastery_hub/
   │   ├── core/                    # Core business logic
   │   │   ├── domain/              # Domain models and entities
   │   │   ├── services/            # Business services
   │   │   ├── repositories/        # Data access interfaces
   │   │   └── events/              # Domain events
   │   ├── web/                     # Web application
   │   │   ├── api/                 # REST API endpoints
   │   │   ├── models/              # Pydantic models
   │   │   ├── middleware/          # HTTP middleware
   │   │   ├── services/            # Web-specific services
   │   │   └── config/              # Configuration
   │   ├── cli/                     # Command-line interface
   │   │   ├── commands/            # CLI commands
   │   │   ├── interactive/         # Interactive features
   │   │   └── utils/               # CLI utilities
   │   ├── infrastructure/          # Infrastructure layer
   │   │   ├── database/            # Database implementations
   │   │   ├── cache/               # Caching implementations
   │   │   ├── queue/               # Queue implementations
   │   │   └── external/            # External service clients
   │   └── utils/                   # Shared utilities
   ├── tests/                       # Test suite
   │   ├── unit/                    # Unit tests
   │   ├── integration/             # Integration tests
   │   ├── e2e/                     # End-to-end tests
   │   └── fixtures/                # Test fixtures
   ├── frontend/                    # React frontend
   ├── docs/                        # Documentation
   └── deployment/                  # Deployment configs

Core Layer Architecture
~~~~~~~~~~~~~~~~~~~~~~

**Domain Models** (``core/domain/``)

Pure business logic without external dependencies:

.. code-block:: python

   # User domain model
   class User:
       def __init__(self, user_id: str, email: str):
           self.user_id = user_id
           self.email = email
           self.progress = Progress()
           self.achievements = []
       
       def complete_exercise(self, exercise: Exercise) -> ExerciseResult:
           """Business logic for exercise completion."""
           result = exercise.evaluate(self.submission)
           self.progress.update(exercise, result)
           return result

**Services** (``core/services/``)

Orchestrate business workflows:

.. code-block:: python

   class LearningService:
       def __init__(
           self, 
           user_repo: UserRepository,
           exercise_repo: ExerciseRepository,
           event_bus: EventBus
       ):
           self.user_repo = user_repo
           self.exercise_repo = exercise_repo
           self.event_bus = event_bus
       
       async def submit_exercise(
           self, 
           user_id: str, 
           exercise_id: str, 
           code: str
       ) -> ExerciseResult:
           user = await self.user_repo.get_user(user_id)
           exercise = await self.exercise_repo.get_exercise(exercise_id)
           
           result = user.complete_exercise(exercise, code)
           await self.user_repo.save_user(user)
           
           # Publish event for other services
           await self.event_bus.publish(
               UserCompletedExerciseEvent(user_id, exercise_id, result)
           )
           
           return result

**Repositories** (``core/repositories/``)

Abstract data access interfaces:

.. code-block:: python

   class UserRepository(ABC):
       @abstractmethod
       async def get_user(self, user_id: str) -> User:
           pass
       
       @abstractmethod
       async def save_user(self, user: User) -> None:
           pass
       
       @abstractmethod
       async def find_users_by_criteria(self, criteria: UserCriteria) -> List[User]:
           pass

Web Layer Architecture
~~~~~~~~~~~~~~~~~~~~~

**API Endpoints** (``web/api/``)

FastAPI routers with clean separation:

.. code-block:: python

   @router.post("/exercises/{exercise_id}/submit")
   async def submit_exercise(
       exercise_id: str,
       submission: ExerciseSubmission,
       current_user: User = Depends(get_current_user),
       learning_service: LearningService = Depends(get_learning_service)
   ) -> ExerciseResult:
       """Submit an exercise solution for evaluation."""
       return await learning_service.submit_exercise(
           current_user.user_id,
           exercise_id,
           submission.code
       )

**Models** (``web/models/``)

Pydantic models for API contracts:

.. code-block:: python

   class ExerciseSubmission(BaseModel):
       code: str = Field(..., description="Python code solution")
       test_mode: bool = Field(False, description="Run in test mode")
       
       @validator('code')
       def validate_code(cls, v):
           if len(v.strip()) == 0:
               raise ValueError("Code cannot be empty")
           return v

**Middleware** (``web/middleware/``)

Cross-cutting concerns:

.. code-block:: python

   class RateLimitingMiddleware:
       async def __call__(self, request: Request, call_next):
           client_ip = request.client.host
           if await self.rate_limiter.is_rate_limited(client_ip):
               raise HTTPException(429, "Rate limit exceeded")
           return await call_next(request)

Data Layer Architecture
----------------------

Database Design
~~~~~~~~~~~~~~~

**Entity Relationship Diagram:**

.. code-block:: text

   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
   │    Users    │────▶│  Progress   │◀────│ Exercises   │
   │             │     │             │     │             │
   │ - user_id   │     │ - user_id   │     │ - exercise_id│
   │ - email     │     │ - exercise_id│    │ - title     │
   │ - profile   │     │ - score     │     │ - content   │
   └─────────────┘     │ - completed │     │ - tests     │
           │           └─────────────┘     └─────────────┘
           │                 │
           │                 │
           ▼                 ▼
   ┌─────────────┐     ┌─────────────┐
   │Achievements │     │ Submissions │
   │             │     │             │
   │ - achievement_id   │ - submission_id
   │ - user_id   │     │ - user_id   │
   │ - earned_at │     │ - exercise_id│
   └─────────────┘     │ - code      │
                       │ - result    │
                       └─────────────┘

**Database Schema:**

.. code-block:: sql

   -- Users table
   CREATE TABLE users (
       user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       email VARCHAR(255) UNIQUE NOT NULL,
       password_hash VARCHAR(255) NOT NULL,
       full_name VARCHAR(255),
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       is_active BOOLEAN DEFAULT TRUE,
       profile JSONB DEFAULT '{}'
   );

   -- Exercises table
   CREATE TABLE exercises (
       exercise_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       title VARCHAR(255) NOT NULL,
       description TEXT,
       difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 5),
       category VARCHAR(100),
       content JSONB NOT NULL,
       tests JSONB NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   -- User progress table
   CREATE TABLE user_progress (
       progress_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
       exercise_id UUID REFERENCES exercises(exercise_id) ON DELETE CASCADE,
       score INTEGER,
       completed_at TIMESTAMP,
       attempts INTEGER DEFAULT 0,
       best_score INTEGER,
       time_spent_seconds INTEGER,
       UNIQUE(user_id, exercise_id)
   );

   -- Submissions table
   CREATE TABLE submissions (
       submission_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
       exercise_id UUID REFERENCES exercises(exercise_id) ON DELETE CASCADE,
       code TEXT NOT NULL,
       result JSONB,
       submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       execution_time_ms INTEGER,
       memory_usage_mb REAL
   );

**Migration Strategy:**

.. code-block:: python

   # Alembic migration example
   def upgrade():
       op.create_table(
           'users',
           sa.Column('user_id', sa.UUID(), nullable=False),
           sa.Column('email', sa.String(255), nullable=False),
           sa.Column('password_hash', sa.String(255), nullable=False),
           sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
           sa.PrimaryKeyConstraint('user_id'),
           sa.UniqueConstraint('email')
       )
       
       op.create_index('idx_users_email', 'users', ['email'])

Caching Strategy
~~~~~~~~~~~~~~~

**Multi-Level Caching:**

.. code-block:: python

   class CacheManager:
       def __init__(self):
           self.l1_cache = LRUCache(maxsize=1000)  # In-memory
           self.l2_cache = RedisCache()            # Distributed
           self.l3_cache = DatabaseCache()         # Persistent
       
       async def get(self, key: str) -> Any:
           # Try L1 cache first
           if value := self.l1_cache.get(key):
               return value
           
           # Try L2 cache
           if value := await self.l2_cache.get(key):
               self.l1_cache.set(key, value)
               return value
           
           # Try L3 cache
           if value := await self.l3_cache.get(key):
               self.l1_cache.set(key, value)
               await self.l2_cache.set(key, value)
               return value
           
           return None

**Cache Invalidation:**

.. code-block:: python

   class CacheInvalidationService:
       async def on_user_updated(self, event: UserUpdatedEvent):
           """Invalidate user-related cache entries."""
           patterns = [
               f"user:{event.user_id}:*",
               f"progress:{event.user_id}:*",
               "leaderboard:*"
           ]
           
           for pattern in patterns:
               await self.cache.delete_pattern(pattern)

Security Architecture
--------------------

Authentication and Authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**JWT Token Strategy:**

.. code-block:: python

   class JWTTokenService:
       def create_access_token(self, user_id: str, permissions: List[str]) -> str:
           payload = {
               "sub": user_id,
               "permissions": permissions,
               "exp": datetime.utcnow() + timedelta(minutes=15),
               "type": "access"
           }
           return jwt.encode(payload, self.secret_key, algorithm="HS256")
       
       def create_refresh_token(self, user_id: str) -> str:
           payload = {
               "sub": user_id,
               "exp": datetime.utcnow() + timedelta(days=7),
               "type": "refresh"
           }
           return jwt.encode(payload, self.secret_key, algorithm="HS256")

**Role-Based Access Control (RBAC):**

.. code-block:: python

   class Permission(Enum):
       READ_EXERCISES = "read:exercises"
       SUBMIT_EXERCISES = "submit:exercises"
       MANAGE_USERS = "manage:users"
       ADMIN_ACCESS = "admin:access"

   class Role(Enum):
       STUDENT = "student"
       INSTRUCTOR = "instructor"
       ADMIN = "admin"

   ROLE_PERMISSIONS = {
       Role.STUDENT: [
           Permission.READ_EXERCISES,
           Permission.SUBMIT_EXERCISES
       ],
       Role.INSTRUCTOR: [
           Permission.READ_EXERCISES,
           Permission.SUBMIT_EXERCISES,
           Permission.MANAGE_USERS
       ],
       Role.ADMIN: [perm for perm in Permission]
   }

**Security Middleware:**

.. code-block:: python

   class SecurityMiddleware:
       async def __call__(self, request: Request, call_next):
           # HTTPS redirect
           if not request.url.scheme == "https" and self.force_https:
               https_url = request.url.replace(scheme="https")
               return RedirectResponse(https_url, status_code=301)
           
           # Security headers
           response = await call_next(request)
           response.headers["X-Content-Type-Options"] = "nosniff"
           response.headers["X-Frame-Options"] = "DENY"
           response.headers["X-XSS-Protection"] = "1; mode=block"
           response.headers["Strict-Transport-Security"] = "max-age=31536000"
           
           return response

Code Execution Security
~~~~~~~~~~~~~~~~~~~~~

**Sandboxed Execution:**

.. code-block:: python

   class SecureCodeExecutor:
       def __init__(self):
           self.docker_client = docker.from_env()
           self.execution_timeout = 30
           self.memory_limit = "128m"
       
       async def execute_code(self, code: str, test_cases: List[TestCase]) -> ExecutionResult:
           """Execute user code in secure sandbox."""
           # Create temporary directory for code
           with tempfile.TemporaryDirectory() as temp_dir:
               code_file = Path(temp_dir) / "solution.py"
               code_file.write_text(code)
               
               # Run in Docker container
               container = self.docker_client.containers.run(
                   image="python:3.9-alpine",
                   command=f"python /app/solution.py",
                   volumes={temp_dir: {"bind": "/app", "mode": "ro"}},
                   memory=self.memory_limit,
                   cpu_quota=50000,  # 50% CPU
                   network_disabled=True,
                   remove=True,
                   detach=True
               )
               
               try:
                   result = container.wait(timeout=self.execution_timeout)
                   output = container.logs().decode()
                   return ExecutionResult(
                       success=result["StatusCode"] == 0,
                       output=output,
                       execution_time=result["execution_time"]
                   )
               except TimeoutError:
                   container.kill()
                   return ExecutionResult(
                       success=False,
                       error="Execution timeout",
                       execution_time=self.execution_timeout
                   )

Performance Architecture
-----------------------

Asynchronous Processing
~~~~~~~~~~~~~~~~~~~~~~

**Background Tasks:**

.. code-block:: python

   from celery import Celery

   celery_app = Celery("python_mastery_hub")

   @celery_app.task
   async def generate_progress_report(user_id: str):
       """Generate comprehensive progress report."""
       user_service = get_user_service()
       progress_service = get_progress_service()
       
       user = await user_service.get_user(user_id)
       report = await progress_service.generate_report(user)
       
       # Send email notification
       email_service = get_email_service()
       await email_service.send_progress_report(user.email, report)

**Event Processing:**

.. code-block:: python

   class EventProcessor:
       def __init__(self):
           self.handlers = defaultdict(list)
       
       def register_handler(self, event_type: type, handler: Callable):
           self.handlers[event_type].append(handler)
       
       async def process_event(self, event: DomainEvent):
           handlers = self.handlers[type(event)]
           
           # Process handlers concurrently
           tasks = [handler(event) for handler in handlers]
           await asyncio.gather(*tasks, return_exceptions=True)

Database Optimization
~~~~~~~~~~~~~~~~~~~~

**Query Optimization:**

.. code-block:: python

   class OptimizedUserRepository:
       async def get_user_with_progress(self, user_id: str) -> UserWithProgress:
           """Optimized query with proper joins and indexing."""
           query = (
               select(User, Progress, Exercise)
               .join(Progress, User.user_id == Progress.user_id)
               .join(Exercise, Progress.exercise_id == Exercise.exercise_id)
               .where(User.user_id == user_id)
               .options(
                   selectinload(User.achievements),
                   selectinload(User.submissions)
               )
           )
           
           result = await self.session.execute(query)
           return result.unique().scalar_one_or_none()

**Connection Pooling:**

.. code-block:: python

   from sqlalchemy.pool import QueuePool

   engine = create_async_engine(
       database_url,
       poolclass=QueuePool,
       pool_size=10,
       max_overflow=20,
       pool_pre_ping=True,
       pool_recycle=3600
   )

Monitoring and Observability
---------------------------

Logging Strategy
~~~~~~~~~~~~~~~

**Structured Logging:**

.. code-block:: python

   import structlog

   logger = structlog.get_logger()

   class UserService:
       async def create_user(self, user_data: CreateUserRequest) -> User:
           logger.info(
               "Creating new user",
               email=user_data.email,
               user_agent=user_data.user_agent,
               ip_address=user_data.ip_address
           )
           
           try:
               user = await self.user_repo.create_user(user_data)
               
               logger.info(
                   "User created successfully",
                   user_id=user.user_id,
                   email=user.email
               )
               
               return user
           except Exception as e:
               logger.error(
                   "Failed to create user",
                   email=user_data.email,
                   error=str(e),
                   error_type=type(e).__name__
               )
               raise

**Metrics Collection:**

.. code-block:: python

   from prometheus_client import Counter, Histogram, Gauge

   # Define metrics
   REQUEST_COUNT = Counter(
       'http_requests_total',
       'Total HTTP requests',
       ['method', 'endpoint', 'status_code']
   )

   REQUEST_DURATION = Histogram(
       'http_request_duration_seconds',
       'HTTP request duration',
       ['method', 'endpoint']
   )

   ACTIVE_USERS = Gauge(
       'active_users_total',
       'Number of active users'
   )

   # Middleware for automatic metrics collection
   class MetricsMiddleware:
       async def __call__(self, request: Request, call_next):
           start_time = time.time()
           
           response = await call_next(request)
           
           REQUEST_COUNT.labels(
               method=request.method,
               endpoint=request.url.path,
               status_code=response.status_code
           ).inc()
           
           REQUEST_DURATION.labels(
               method=request.method,
               endpoint=request.url.path
           ).observe(time.time() - start_time)
           
           return response

Health Checks
~~~~~~~~~~~~

.. code-block:: python

   class HealthCheckService:
       def __init__(
           self,
           database: Database,
           cache: CacheManager,
           queue: QueueManager
       ):
           self.database = database
           self.cache = cache
           self.queue = queue
       
       async def check_health(self) -> HealthStatus:
           checks = {
               "database": self._check_database(),
               "cache": self._check_cache(),
               "queue": self._check_queue()
           }
           
           results = await asyncio.gather(
               *checks.values(),
               return_exceptions=True
           )
           
           health_checks = dict(zip(checks.keys(), results))
           
           return HealthStatus(
               status="healthy" if all(
                   check.status == "healthy" 
                   for check in health_checks.values()
               ) else "unhealthy",
               checks=health_checks
           )

Deployment Architecture
----------------------

Container Strategy
~~~~~~~~~~~~~~~~~

**Multi-stage Docker Build:**

.. code-block:: dockerfile

   # Build stage
   FROM python:3.9-slim as builder
   WORKDIR /app
   
   COPY pyproject.toml poetry.lock ./
   RUN pip install poetry && \
       poetry config virtualenvs.create false && \
       poetry install --no-dev --no-root
   
   # Runtime stage
   FROM python:3.9-slim as runtime
   WORKDIR /app
   
   COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
   COPY --from=builder /usr/local/bin /usr/local/bin
   
   COPY src/ ./src/
   COPY alembic.ini ./
   
   EXPOSE 8000
   CMD ["uvicorn", "python_mastery_hub.web.main:app", "--host", "0.0.0.0", "--port", "8000"]

**Kubernetes Deployment:**

.. code-block:: yaml

   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: python-mastery-hub
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: python-mastery-hub
     template:
       metadata:
         labels:
           app: python-mastery-hub
       spec:
         containers:
         - name: app
           image: python-mastery-hub:latest
           ports:
           - containerPort: 8000
           env:
           - name: DATABASE_URL
             valueFrom:
               secretKeyRef:
                 name: db-secret
                 key: url
           resources:
             requests:
               memory: "256Mi"
               cpu: "250m"
             limits:
               memory: "512Mi"
               cpu: "500m"
           livenessProbe:
             httpGet:
               path: /health
               port: 8000
             initialDelaySeconds: 30
             periodSeconds: 10
           readinessProbe:
             httpGet:
               path: /ready
               port: 8000
             initialDelaySeconds: 5
             periodSeconds: 5

Testing Strategy
---------------

**Test Pyramid:**

.. code-block:: text

              ┌─────────────────┐
              │   E2E Tests     │  ← Few, slow, high confidence
              │   (Playwright)  │
              └─────────────────┘
                      │
           ┌─────────────────────────┐
           │  Integration Tests      │  ← Some, medium speed
           │  (pytest + TestClient) │
           └─────────────────────────┘
                      │
        ┌─────────────────────────────────┐
        │      Unit Tests                 │  ← Many, fast, isolated
        │   (pytest + mocks)             │
        └─────────────────────────────────┘

**Testing Architecture:**

.. code-block:: python

   # Unit test example
   @pytest.fixture
   def mock_user_repository():
       return Mock(spec=UserRepository)

   @pytest.fixture
   def user_service(mock_user_repository):
       return UserService(user_repository=mock_user_repository)

   async def test_create_user_success(user_service, mock_user_repository):
       # Arrange
       user_data = CreateUserRequest(email="test@example.com")
       expected_user = User(user_id="123", email="test@example.com")
       mock_user_repository.create_user.return_value = expected_user
       
       # Act
       result = await user_service.create_user(user_data)
       
       # Assert
       assert result == expected_user
       mock_user_repository.create_user.assert_called_once_with(user_data)

Future Architecture Considerations
---------------------------------

**Microservices Migration Path:**

When the monolith grows too large, these modules can be extracted:

1. **Authentication Service**: User management and authentication
2. **Content Service**: Learning materials and exercises
3. **Progress Service**: Progress tracking and analytics
4. **Notification Service**: Email and push notifications
5. **Code Execution Service**: Sandboxed code execution

**Event Sourcing:**

For better auditability and scalability:

.. code-block:: python

   class UserAggregate:
       def __init__(self):
           self.events = []
       
       def create_user(self, email: str):
           event = UserCreatedEvent(email=email, timestamp=datetime.utcnow())
           self.apply_event(event)
           self.events.append(event)
       
       def apply_event(self, event: DomainEvent):
           if isinstance(event, UserCreatedEvent):
               self.user_id = event.user_id
               self.email = event.email

This architecture provides a solid foundation for the Python Mastery Hub platform that can scale from a small educational tool to a comprehensive learning platform used by thousands of students worldwide.