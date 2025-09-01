"""
Microservice Architecture Exercise for Web Development Learning.

Design and implement a microservices system with FastAPI, service communication,
distributed data management, and resilience patterns.
"""

from typing import Dict, Any


def get_exercise() -> Dict[str, Any]:
    """Get the complete microservices architecture exercise."""
    return {
        "title": "Microservice Architecture",
        "description": "Design and implement a distributed e-commerce system using microservices architecture",
        "difficulty": "expert",
        "estimated_time": "8-12 hours",
        "learning_objectives": [
            "Design microservice architecture and service boundaries",
            "Implement inter-service communication patterns",
            "Handle distributed data management and consistency",
            "Add service discovery and API gateway patterns",
            "Implement monitoring, logging, and observability",
            "Handle failure scenarios and implement resilience patterns",
            "Deploy services with containerization",
            "Manage configuration and secrets across services"
        ],
        "requirements": [
            "FastAPI for service implementation",
            "Docker for containerization",
            "Redis for caching and pub/sub",
            "PostgreSQL for persistent storage",
            "nginx for API gateway",
            "httpx for async HTTP client",
            "python-multipart for file uploads",
            "prometheus-client for metrics"
        ],
        "system_architecture": '''
# E-Commerce Microservices Architecture

## Services Overview
1. **API Gateway** (nginx/FastAPI) - Single entry point, routing, auth
2. **User Service** - User management, authentication, profiles
3. **Product Service** - Product catalog, inventory, search
4. **Order Service** - Order processing, cart management
5. **Payment Service** - Payment processing, billing
6. **Notification Service** - Email, SMS, push notifications
7. **Analytics Service** - User behavior, sales analytics

## Communication Patterns
- **Synchronous**: HTTP/REST for real-time queries
- **Asynchronous**: Message queues for events
- **Database per Service**: Each service owns its data

## Technology Stack
- FastAPI for all services
- PostgreSQL for persistent storage
- Redis for caching and message broker
- Docker for containerization
- nginx for API gateway and load balancing
''',
        "starter_code": '''
"""
Microservices E-Commerce System - Starter Code

Complete the TODO sections to build a distributed microservices system.
"""

# ==============================================================================
# SHARED MODELS AND UTILITIES (shared/models.py)
# ==============================================================================

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

# Shared response models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ServiceHealth(BaseModel):
    service: str
    status: str
    timestamp: datetime
    version: str
    dependencies: List[str]

# ==============================================================================
# API GATEWAY SERVICE (gateway/main.py)
# ==============================================================================

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
from typing import Dict

# TODO: Implement API Gateway
class APIGateway:
    """Central API Gateway for routing requests to microservices."""
    
    def __init__(self):
        # TODO: Initialize service registry
        self.services = {
            "user": "http://user-service:8001",
            "product": "http://product-service:8002", 
            "order": "http://order-service:8003",
            "payment": "http://payment-service:8004",
            "notification": "http://notification-service:8005",
            "analytics": "http://analytics-service:8006"
        }
        self.client = httpx.AsyncClient()
    
    async def route_request(self, service: str, path: str, method: str, **kwargs):
        """Route request to appropriate microservice."""
        # TODO: Implement request routing
        # 1. Check if service exists
        # 2. Build full URL
        # 3. Add authentication headers
        # 4. Make request to service
        # 5. Handle service failures
        # 6. Return response
        pass
    
    async def health_check_services(self):
        """Check health of all registered services."""
        # TODO: Implement health checking
        # 1. Query each service health endpoint
        # 2. Collect status information
        # 3. Return overall system health
        pass

app = FastAPI(title="E-Commerce API Gateway")

# TODO: Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gateway = APIGateway()

# TODO: Implement gateway routes
@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def user_service_proxy(request: Request, path: str):
    """Proxy requests to user service."""
    # TODO: Implement user service proxy
    pass

@app.api_route("/api/products/{path:path}", methods=["GET", "POST", "PUT", "DELETE"]) 
async def product_service_proxy(request: Request, path: str):
    """Proxy requests to product service."""
    # TODO: Implement product service proxy
    pass

@app.api_route("/api/orders/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def order_service_proxy(request: Request, path: str):
    """Proxy requests to order service."""
    # TODO: Implement order service proxy
    pass

@app.get("/health")
async def gateway_health():
    """Gateway health check."""
    # TODO: Return gateway and service health
    pass

# ==============================================================================
# USER SERVICE (user_service/main.py)
# ==============================================================================

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
import jwt

# TODO: Implement User Service
app = FastAPI(title="User Service")

# Database setup
DATABASE_URL = "postgresql://user:password@user-db:5432/users"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# TODO: Implement user management endpoints
@app.post("/register")
async def register_user():
    """Register new user."""
    # TODO: Implement user registration
    pass

@app.post("/login")
async def login_user():
    """Authenticate user."""
    # TODO: Implement user authentication
    pass

@app.get("/profile/{user_id}")
async def get_user_profile(user_id: int):
    """Get user profile."""
    # TODO: Implement profile retrieval
    pass

@app.get("/health")
async def user_service_health():
    """User service health check."""
    return ServiceHealth(
        service="user-service",
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        dependencies=["user-db"]
    )

# ==============================================================================
# PRODUCT SERVICE (product_service/main.py)  
# ==============================================================================

from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import Column, Integer, String, Float, Text, Boolean
import redis

# TODO: Implement Product Service
app = FastAPI(title="Product Service")

# Database and cache setup
DATABASE_URL = "postgresql://user:password@product-db:5432/products"
redis_client = redis.Redis(host='redis', port=6379, db=0)

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    stock_quantity = Column(Integer)
    category = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# TODO: Implement product management
@app.get("/products")
async def list_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    """List products with filtering and pagination."""
    # TODO: Implement product listing with caching
    pass

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    """Get product details."""
    # TODO: Implement product retrieval with caching
    pass

@app.post("/products")
async def create_product():
    """Create new product."""
    # TODO: Implement product creation
    pass

@app.put("/products/{product_id}/stock")
async def update_stock(product_id: int, quantity: int):
    """Update product stock."""
    # TODO: Implement stock management
    # Important: Handle concurrent updates properly
    pass

# ==============================================================================
# ORDER SERVICE (order_service/main.py)
# ==============================================================================

from fastapi import FastAPI, BackgroundTasks
import httpx
import json

# TODO: Implement Order Service
app = FastAPI(title="Order Service")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    total_amount = Column(Float)
    status = Column(String, default=OrderStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer)
    product_id = Column(Integer)
    quantity = Column(Integer)
    price = Column(Float)

# TODO: Implement order management
@app.post("/orders")
async def create_order(background_tasks: BackgroundTasks):
    """Create new order."""
    # TODO: Implement order creation
    # 1. Validate products and stock
    # 2. Calculate total amount
    # 3. Create order and items
    # 4. Reserve inventory
    # 5. Trigger payment processing
    # 6. Send notifications
    pass

@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    """Get order details."""
    # TODO: Implement order retrieval
    pass

@app.put("/orders/{order_id}/status")
async def update_order_status(order_id: int, status: OrderStatus):
    """Update order status."""
    # TODO: Implement status update with event publishing
    pass

# ==============================================================================
# PAYMENT SERVICE (payment_service/main.py)
# ==============================================================================

from fastapi import FastAPI
import asyncio

# TODO: Implement Payment Service  
app = FastAPI(title="Payment Service")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, unique=True, index=True)
    amount = Column(Float)
    status = Column(String, default=PaymentStatus.PENDING)
    payment_method = Column(String)
    transaction_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# TODO: Implement payment processing
@app.post("/payments")
async def process_payment():
    """Process payment for order."""
    # TODO: Implement payment processing
    # 1. Validate payment details
    # 2. Call external payment gateway
    # 3. Handle success/failure
    # 4. Update payment status
    # 5. Notify order service
    pass

@app.get("/payments/{payment_id}")
async def get_payment(payment_id: int):
    """Get payment details."""
    # TODO: Implement payment retrieval
    pass

# ==============================================================================
# NOTIFICATION SERVICE (notification_service/main.py)
# ==============================================================================

from fastapi import FastAPI, BackgroundTasks
import smtplib
from email.mime.text import MimeText

# TODO: Implement Notification Service
app = FastAPI(title="Notification Service")

class NotificationService:
    """Handle various types of notifications."""
    
    async def send_email(self, to: str, subject: str, body: str):
        """Send email notification."""
        # TODO: Implement email sending
        pass
    
    async def send_sms(self, phone: str, message: str):
        """Send SMS notification."""
        # TODO: Implement SMS sending
        pass

notification_service = NotificationService()

@app.post("/notifications/email")
async def send_email_notification(background_tasks: BackgroundTasks):
    """Send email notification."""
    # TODO: Queue email for background processing
    pass

@app.post("/notifications/order-status")
async def notify_order_status():
    """Send order status notification."""
    # TODO: Send appropriate notification based on order status
    pass

# ==============================================================================
# ANALYTICS SERVICE (analytics_service/main.py)
# ==============================================================================

from fastapi import FastAPI
import pandas as pd

# TODO: Implement Analytics Service
app = FastAPI(title="Analytics Service")

@app.get("/analytics/sales")
async def get_sales_analytics():
    """Get sales analytics."""
    # TODO: Aggregate sales data from order service
    pass

@app.get("/analytics/products")
async def get_product_analytics():
    """Get product performance analytics."""
    # TODO: Analyze product performance metrics
    pass

# ==============================================================================
# DOCKER CONFIGURATION
# ==============================================================================

# Dockerfile template for each service:
"""
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

# docker-compose.yml for the entire system:
"""
version: '3.8'

services:
  # Databases
  user-db:
    image: postgres:13
    environment:
      POSTGRES_DB: users
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password

  product-db:
    image: postgres:13
    environment:
      POSTGRES_DB: products
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password

  redis:
    image: redis:6-alpine

  # Services
  user-service:
    build: ./user_service
    ports:
      - "8001:8000"
    depends_on:
      - user-db

  product-service:
    build: ./product_service
    ports:
      - "8002:8000"
    depends_on:
      - product-db
      - redis

  order-service:
    build: ./order_service
    ports:
      - "8003:8000"

  payment-service:
    build: ./payment_service
    ports:
      - "8004:8000"

  notification-service:
    build: ./notification_service
    ports:
      - "8005:8000"

  analytics-service:
    build: ./analytics_service
    ports:
      - "8006:8000"

  api-gateway:
    build: ./gateway
    ports:
      - "8000:8000"
    depends_on:
      - user-service
      - product-service
      - order-service
      - payment-service
      - notification-service
      - analytics-service
"""
''',
        "implementation_guide": [
            "Start with the shared models and API response formats",
            "Implement each service independently with its own database",
            "Begin with the User Service for authentication foundation",
            "Add the Product Service with caching for performance",
            "Implement Order Service with proper transaction handling",
            "Create Payment Service with external gateway simulation",
            "Add Notification Service for asynchronous messaging",
            "Build Analytics Service for cross-service data aggregation",
            "Implement the API Gateway for request routing",
            "Add monitoring, logging, and health checks",
            "Containerize all services with Docker",
            "Set up service communication and error handling"
        ],
        "testing_guide": '''
# Testing Microservices System

## 1. Local Development Setup
```bash
# Clone repository and setup environment
git clone <repository>
cd microservices-ecommerce

# Start all services with Docker Compose
docker-compose up -d

# Check service health
curl http://localhost:8000/health
```

## 2. Service Integration Testing
```python
import httpx
import asyncio

async def test_service_integration():
    async with httpx.AsyncClient() as client:
        # Register user
        user_response = await client.post("http://localhost:8000/api/users/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        })
        
        # Create product
        product_response = await client.post("http://localhost:8000/api/products", json={
            "name": "Test Product",
            "price": 29.99,
            "stock_quantity": 100
        })
        
        # Create order
        order_response = await client.post("http://localhost:8000/api/orders", json={
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 2}]
        })
        
        print("Integration test completed successfully")

asyncio.run(test_service_integration())
```

## 3. Load Testing
```bash
# Install artillery for load testing
npm install -g artillery

# Create load test configuration
cat > load-test.yml << EOF
config:
  target: 'http://localhost:8000'
  phases:
    - duration: 60
      arrivalRate: 10

scenarios:
  - name: "Product browsing"
    requests:
      - get:
          url: "/api/products"
      - get:
          url: "/api/products/1"
EOF

# Run load test
artillery run load-test.yml
```

## 4. Service Health Monitoring
```bash
# Check all service health endpoints
for port in 8001 8002 8003 8004 8005 8006; do
  echo "Checking service on port $port"
  curl -s http://localhost:$port/health | jq '.'
done
```
''',
        "resilience_patterns": [
            "Circuit Breaker: Prevent cascading failures between services",
            "Retry Logic: Automatic retry with exponential backoff",
            "Timeout Handling: Set appropriate timeouts for service calls",
            "Bulkhead Pattern: Isolate critical resources",
            "Fallback Mechanisms: Graceful degradation when services fail",
            "Health Checks: Regular service health monitoring",
            "Load Balancing: Distribute load across service instances",
            "Rate Limiting: Protect services from overload"
        ],
        "monitoring_requirements": [
            "Service health endpoints returning status and dependencies",
            "Application metrics (requests/sec, response times, error rates)",
            "Business metrics (orders created, revenue, user registrations)",
            "Log aggregation across all services",
            "Distributed tracing for request flows",
            "Database performance monitoring",
            "Infrastructure metrics (CPU, memory, disk, network)"
        ],
        "bonus_challenges": [
            "Implement distributed tracing with OpenTelemetry",
            "Add API versioning and backward compatibility",
            "Create automated integration testing pipeline",
            "Implement saga pattern for distributed transactions",
            "Add service mesh with Istio for advanced networking",
            "Create auto-scaling based on metrics",
            "Implement blue-green deployments",
            "Add comprehensive security with OAuth2 and service-to-service auth",
            "Create data synchronization between services",
            "Implement event sourcing for audit trails"
        ],
        "common_pitfalls": [
            "Not handling partial failures in distributed transactions",
            "Tight coupling between services through shared databases",
            "Missing proper error handling and circuit breakers",
            "Insufficient monitoring and observability",
            "Not implementing proper service boundaries",
            "Ignoring network latency and reliability issues",
            "Poor data consistency strategies",
            "Inadequate security between services"
        ]
    }