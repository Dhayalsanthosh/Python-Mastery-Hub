# File Location: docs/source/development/deployment.rst

Deployment Guide
===============

This comprehensive deployment guide covers all aspects of deploying Python Mastery Hub from development to production environments, including containerization, orchestration, monitoring, and maintenance.

.. note::
   This guide assumes familiarity with Docker, Kubernetes, and modern DevOps practices. 
   For local development setup, see the :doc:`../tutorials/getting_started` guide.

Deployment Overview
------------------

Deployment Strategy
~~~~~~~~~~~~~~~~~~

Python Mastery Hub supports multiple deployment strategies to accommodate different environments and requirements:

**Environment Progression:**

.. code-block:: text

   Local Development → Staging → Production
        ↓               ↓           ↓
   Docker Compose → Kubernetes → Kubernetes + CDN
   SQLite/PostgreSQL → PostgreSQL → PostgreSQL (HA)
   In-memory cache → Redis → Redis Cluster
   Local storage → S3-compatible → Multi-region S3

**Deployment Architectures:**

1. **Single Server**: Simple Docker Compose setup for small deployments
2. **Kubernetes**: Scalable container orchestration for production
3. **Serverless**: Functions-as-a-Service for specific components
4. **Multi-Region**: Global deployment with load balancing

**Infrastructure Components:**

- **Application Servers**: FastAPI applications behind load balancers
- **Database**: PostgreSQL with read replicas for scaling
- **Cache**: Redis cluster for session and application caching  
- **Message Queue**: Celery with Redis for background tasks
- **File Storage**: S3-compatible storage for user uploads and assets
- **Monitoring**: Prometheus, Grafana, and centralized logging

Local Development Deployment
---------------------------

Docker Compose Setup
~~~~~~~~~~~~~~~~~~~

**Complete Docker Compose Configuration:**

.. code-block:: yaml

   # docker-compose.yml
   version: '3.8'

   services:
     app:
       build:
         context: .
         dockerfile: Dockerfile
         target: development
       ports:
         - "8000:8000"
       environment:
         - DATABASE_URL=postgresql://postgres:password@db:5432/python_mastery_hub
         - REDIS_URL=redis://redis:6379
         - SECRET_KEY=dev-secret-key-change-in-production
         - DEBUG=true
       volumes:
         - ./src:/app/src
         - ./tests:/app/tests
       depends_on:
         - db
         - redis
       command: uvicorn python_mastery_hub.web.main:app --host 0.0.0.0 --port 8000 --reload

     frontend:
       build:
         context: ./frontend
         dockerfile: Dockerfile
         target: development
       ports:
         - "3000:3000"
       environment:
         - REACT_APP_API_URL=http://localhost:8000/api
         - REACT_APP_WS_URL=ws://localhost:8000/ws
       volumes:
         - ./frontend/src:/app/src
         - ./frontend/public:/app/public
       command: npm start

     db:
       image: postgres:13-alpine
       environment:
         - POSTGRES_DB=python_mastery_hub
         - POSTGRES_USER=postgres
         - POSTGRES_PASSWORD=password
       volumes:
         - postgres_data:/var/lib/postgresql/data
         - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
       ports:
         - "5432:5432"

     redis:
       image: redis:6-alpine
       ports:
         - "6379:6379"
       volumes:
         - redis_data:/data

     worker:
       build:
         context: .
         dockerfile: Dockerfile
         target: development
       environment:
         - DATABASE_URL=postgresql://postgres:password@db:5432/python_mastery_hub
         - REDIS_URL=redis://redis:6379
         - SECRET_KEY=dev-secret-key-change-in-production
       depends_on:
         - db
         - redis
       command: celery -A python_mastery_hub.worker worker --loglevel=info

     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx/nginx.conf:/etc/nginx/nginx.conf
         - ./nginx/ssl:/etc/nginx/ssl
       depends_on:
         - app
         - frontend

   volumes:
     postgres_data:
     redis_data:

**Multi-stage Dockerfile:**

.. code-block:: dockerfile

   # Dockerfile
   # Build stage
   FROM python:3.9-slim as base

   WORKDIR /app

   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       build-essential \
       curl \
       && rm -rf /var/lib/apt/lists/*

   # Install Python dependencies
   COPY pyproject.toml poetry.lock ./
   RUN pip install poetry && \
       poetry config virtualenvs.create false && \
       poetry install --no-dev

   # Development stage
   FROM base as development

   # Install development dependencies
   RUN poetry install

   COPY . .

   # Create non-root user
   RUN adduser --disabled-password --gecos '' appuser && \
       chown -R appuser:appuser /app
   USER appuser

   EXPOSE 8000
   CMD ["uvicorn", "python_mastery_hub.web.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

   # Production stage
   FROM base as production

   COPY src/ ./src/
   COPY alembic.ini ./
   COPY alembic/ ./alembic/

   # Create non-root user
   RUN adduser --disabled-password --gecos '' appuser && \
       chown -R appuser:appuser /app
   USER appuser

   # Health check
   HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
       CMD curl -f http://localhost:8000/health || exit 1

   EXPOSE 8000
   CMD ["uvicorn", "python_mastery_hub.web.main:app", "--host", "0.0.0.0", "--port", "8000"]

**Running the Development Environment:**

.. code-block:: bash

   # Start all services
   docker-compose up -d

   # View logs
   docker-compose logs -f app

   # Run database migrations
   docker-compose exec app alembic upgrade head

   # Create superuser
   docker-compose exec app python -m python_mastery_hub.cli create-superuser

   # Run tests
   docker-compose exec app pytest

   # Access application
   # Frontend: http://localhost:3000
   # Backend API: http://localhost:8000
   # API Docs: http://localhost:8000/docs

Staging Environment
------------------

Staging Deployment with Kubernetes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Namespace Configuration:**

.. code-block:: yaml

   # k8s/staging/namespace.yaml
   apiVersion: v1
   kind: Namespace
   metadata:
     name: python-mastery-hub-staging
     labels:
       environment: staging
       app: python-mastery-hub

**ConfigMap for Environment Variables:**

.. code-block:: yaml

   # k8s/staging/configmap.yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: app-config
     namespace: python-mastery-hub-staging
   data:
     DATABASE_HOST: postgres-service
     DATABASE_PORT: "5432"
     DATABASE_NAME: python_mastery_hub_staging
     REDIS_HOST: redis-service
     REDIS_PORT: "6379"
     DEBUG: "false"
     LOG_LEVEL: "INFO"
     ENVIRONMENT: "staging"

**Secret Management:**

.. code-block:: yaml

   # k8s/staging/secrets.yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: app-secrets
     namespace: python-mastery-hub-staging
   type: Opaque
   data:
     # Base64 encoded values
     SECRET_KEY: <base64-encoded-secret-key>
     DATABASE_PASSWORD: <base64-encoded-db-password>
     JWT_SECRET_KEY: <base64-encoded-jwt-secret>
     REDIS_PASSWORD: <base64-encoded-redis-password>

**Application Deployment:**

.. code-block:: yaml

   # k8s/staging/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: python-mastery-hub-app
     namespace: python-mastery-hub-staging
     labels:
       app: python-mastery-hub
       component: backend
   spec:
     replicas: 2
     selector:
       matchLabels:
         app: python-mastery-hub
         component: backend
     template:
       metadata:
         labels:
           app: python-mastery-hub
           component: backend
       spec:
         containers:
         - name: app
           image: python-mastery-hub:staging-latest
           ports:
           - containerPort: 8000
           env:
           - name: DATABASE_URL
             value: "postgresql://$(DATABASE_USER):$(DATABASE_PASSWORD)@$(DATABASE_HOST):$(DATABASE_PORT)/$(DATABASE_NAME)"
           - name: DATABASE_USER
             value: postgres
           - name: DATABASE_PASSWORD
             valueFrom:
               secretKeyRef:
                 name: app-secrets
                 key: DATABASE_PASSWORD
           envFrom:
           - configMapRef:
               name: app-config
           - secretRef:
               name: app-secrets
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
             timeoutSeconds: 5
             failureThreshold: 3
           readinessProbe:
             httpGet:
               path: /ready
               port: 8000
             initialDelaySeconds: 5
             periodSeconds: 5
             timeoutSeconds: 3
             failureThreshold: 3
         imagePullSecrets:
         - name: registry-secret

**Service Configuration:**

.. code-block:: yaml

   # k8s/staging/service.yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: python-mastery-hub-service
     namespace: python-mastery-hub-staging
   spec:
     selector:
       app: python-mastery-hub
       component: backend
     ports:
     - name: http
       port: 80
       targetPort: 8000
       protocol: TCP
     type: ClusterIP

**Ingress Configuration:**

.. code-block:: yaml

   # k8s/staging/ingress.yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: python-mastery-hub-ingress
     namespace: python-mastery-hub-staging
     annotations:
       nginx.ingress.kubernetes.io/rewrite-target: /
       nginx.ingress.kubernetes.io/ssl-redirect: "true"
       cert-manager.io/cluster-issuer: letsencrypt-staging
   spec:
     tls:
     - hosts:
       - staging.pythonmasteryhub.com
       secretName: staging-tls-secret
     rules:
     - host: staging.pythonmasteryhub.com
       http:
         paths:
         - path: /api
           pathType: Prefix
           backend:
             service:
               name: python-mastery-hub-service
               port:
                 number: 80
         - path: /
           pathType: Prefix
           backend:
             service:
               name: frontend-service
               port:
                 number: 80

Database Deployment
~~~~~~~~~~~~~~~~~

**PostgreSQL StatefulSet:**

.. code-block:: yaml

   # k8s/staging/postgres.yaml
   apiVersion: apps/v1
   kind: StatefulSet
   metadata:
     name: postgres
     namespace: python-mastery-hub-staging
   spec:
     serviceName: postgres-service
     replicas: 1
     selector:
       matchLabels:
         app: postgres
     template:
       metadata:
         labels:
           app: postgres
       spec:
         containers:
         - name: postgres
           image: postgres:13-alpine
           env:
           - name: POSTGRES_DB
             valueFrom:
               configMapKeyRef:
                 name: app-config
                 key: DATABASE_NAME
           - name: POSTGRES_USER
             value: postgres
           - name: POSTGRES_PASSWORD
             valueFrom:
               secretKeyRef:
                 name: app-secrets
                 key: DATABASE_PASSWORD
           ports:
           - containerPort: 5432
           volumeMounts:
           - name: postgres-storage
             mountPath: /var/lib/postgresql/data
           resources:
             requests:
               memory: "256Mi"
               cpu: "250m"
             limits:
               memory: "1Gi"
               cpu: "500m"
     volumeClaimTemplates:
     - metadata:
         name: postgres-storage
       spec:
         accessModes: ["ReadWriteOnce"]
         resources:
           requests:
             storage: 20Gi

**Database Migration Job:**

.. code-block:: yaml

   # k8s/staging/migration-job.yaml
   apiVersion: batch/v1
   kind: Job
   metadata:
     name: db-migration
     namespace: python-mastery-hub-staging
   spec:
     template:
       spec:
         containers:
         - name: migration
           image: python-mastery-hub:staging-latest
           command: ["alembic", "upgrade", "head"]
           envFrom:
           - configMapRef:
               name: app-config
           - secretRef:
               name: app-secrets
         restartPolicy: OnFailure
     backoffLimit: 3

Production Deployment
--------------------

Production Kubernetes Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Production Namespace:**

.. code-block:: yaml

   # k8s/production/namespace.yaml
   apiVersion: v1
   kind: Namespace
   metadata:
     name: python-mastery-hub-prod
     labels:
       environment: production
       app: python-mastery-hub

**High Availability Deployment:**

.. code-block:: yaml

   # k8s/production/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: python-mastery-hub-app
     namespace: python-mastery-hub-prod
   spec:
     replicas: 6  # Higher replica count for production
     strategy:
       type: RollingUpdate
       rollingUpdate:
         maxSurge: 2
         maxUnavailable: 1
     selector:
       matchLabels:
         app: python-mastery-hub
         component: backend
     template:
       metadata:
         labels:
           app: python-mastery-hub
           component: backend
       spec:
         containers:
         - name: app
           image: python-mastery-hub:v1.2.3  # Tagged release
           ports:
           - containerPort: 8000
           env:
           - name: DATABASE_URL
             valueFrom:
               secretKeyRef:
                 name: database-secret
                 key: url
           resources:
             requests:
               memory: "512Mi"
               cpu: "500m"
             limits:
               memory: "1Gi"
               cpu: "1000m"
           livenessProbe:
             httpGet:
               path: /health
               port: 8000
             initialDelaySeconds: 60
             periodSeconds: 10
             timeoutSeconds: 5
             failureThreshold: 3
           readinessProbe:
             httpGet:
               path: /ready
               port: 8000
             initialDelaySeconds: 10
             periodSeconds: 5
             timeoutSeconds: 3
             failureThreshold: 3
         affinity:
           podAntiAffinity:
             preferredDuringSchedulingIgnoredDuringExecution:
             - weight: 100
               podAffinityTerm:
                 labelSelector:
                   matchExpressions:
                   - key: app
                     operator: In
                     values:
                     - python-mastery-hub
                 topologyKey: kubernetes.io/hostname

**Horizontal Pod Autoscaler:**

.. code-block:: yaml

   # k8s/production/hpa.yaml
   apiVersion: autoscaling/v2
   kind: HorizontalPodAutoscaler
   metadata:
     name: python-mastery-hub-hpa
     namespace: python-mastery-hub-prod
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: python-mastery-hub-app
     minReplicas: 3
     maxReplicas: 20
     metrics:
     - type: Resource
       resource:
         name: cpu
         target:
           type: Utilization
           averageUtilization: 70
     - type: Resource
       resource:
         name: memory
         target:
           type: Utilization
           averageUtilization: 80
     behavior:
       scaleDown:
         stabilizationWindowSeconds: 300
         policies:
         - type: Percent
           value: 10
           periodSeconds: 60
       scaleUp:
         stabilizationWindowSeconds: 60
         policies:
         - type: Percent
           value: 100
           periodSeconds: 15

Production Database Setup
~~~~~~~~~~~~~~~~~~~~~~~~

**PostgreSQL with Read Replicas:**

.. code-block:: yaml

   # k8s/production/postgres-primary.yaml
   apiVersion: postgresql.cnpg.io/v1
   kind: Cluster
   metadata:
     name: postgres-cluster
     namespace: python-mastery-hub-prod
   spec:
     instances: 3
     primaryUpdateStrategy: unsupervised
     
     postgresql:
       parameters:
         max_connections: "200"
         shared_buffers: "256MB"
         effective_cache_size: "1GB"
         work_mem: "4MB"
         maintenance_work_mem: "64MB"
         
     bootstrap:
       initdb:
         database: python_mastery_hub
         owner: app_user
         secret:
           name: postgres-credentials
           
     storage:
       size: 100Gi
       storageClass: fast-ssd
       
     monitoring:
       enabled: true
       
     backup:
       retentionPolicy: "7d"
       barmanObjectStore:
         destinationPath: "s3://backups/postgres"
         s3Credentials:
           accessKeyId:
             name: backup-credentials
             key: ACCESS_KEY_ID
           secretAccessKey:
             name: backup-credentials  
             key: SECRET_ACCESS_KEY
         wal:
           retention: "1d"
         data:
           retention: "7d"

**Redis Cluster:**

.. code-block:: yaml

   # k8s/production/redis-cluster.yaml
   apiVersion: redis.redis.opstreelabs.in/v1beta1
   kind: RedisCluster
   metadata:
     name: redis-cluster
     namespace: python-mastery-hub-prod
   spec:
     clusterSize: 6
     kubernetesConfig:
       image: redis:6.2
       imagePullPolicy: IfNotPresent
       resources:
         requests:
           memory: "256Mi"
           cpu: "250m"
         limits:
           memory: "512Mi"
           cpu: "500m"
     storage:
       volumeClaimTemplate:
         spec:
           accessModes: ["ReadWriteOnce"]
           resources:
             requests:
               storage: 10Gi
     securityContext:
       runAsUser: 1000
       fsGroup: 1000

Load Balancing and CDN
~~~~~~~~~~~~~~~~~~~~~

**Application Load Balancer:**

.. code-block:: yaml

   # k8s/production/alb-ingress.yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: python-mastery-hub-alb
     namespace: python-mastery-hub-prod
     annotations:
       kubernetes.io/ingress.class: alb
       alb.ingress.kubernetes.io/scheme: internet-facing
       alb.ingress.kubernetes.io/target-type: ip
       alb.ingress.kubernetes.io/ssl-policy: ELBSecurityPolicy-TLS-1-2-2017-01
       alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:region:account:certificate/cert-id
       alb.ingress.kubernetes.io/ssl-redirect: "443"
       alb.ingress.kubernetes.io/healthcheck-path: /health
       alb.ingress.kubernetes.io/healthcheck-interval-seconds: "30"
       alb.ingress.kubernetes.io/healthy-threshold-count: "2"
       alb.ingress.kubernetes.io/unhealthy-threshold-count: "3"
   spec:
     rules:
     - host: api.pythonmasteryhub.com
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: python-mastery-hub-service
               port:
                 number: 80

**CloudFront CDN Configuration:**

.. code-block:: yaml

   # terraform/cloudfront.tf
   resource "aws_cloudfront_distribution" "main" {
     origin {
       domain_name = "api.pythonmasteryhub.com"
       origin_id   = "ALB-pythonmasteryhub"
       
       custom_origin_config {
         http_port              = 80
         https_port             = 443
         origin_protocol_policy = "https-only"
         origin_ssl_protocols   = ["TLSv1.2"]
       }
     }

     enabled             = true
     is_ipv6_enabled     = true
     default_root_object = "index.html"

     default_cache_behavior {
       allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
       cached_methods         = ["GET", "HEAD"]
       target_origin_id       = "ALB-pythonmasteryhub"
       compress               = true
       viewer_protocol_policy = "redirect-to-https"

       forwarded_values {
         query_string = true
         headers      = ["Authorization", "CloudFront-Forwarded-Proto"]
         cookies {
           forward = "all"
         }
       }

       min_ttl     = 0
       default_ttl = 3600
       max_ttl     = 86400
     }

     # Cache behavior for API endpoints
     ordered_cache_behavior {
       path_pattern     = "/api/*"
       allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
       cached_methods   = ["GET", "HEAD"]
       target_origin_id = "ALB-pythonmasteryhub"

       forwarded_values {
         query_string = true
         headers      = ["*"]
         cookies {
           forward = "all"
         }
       }

       min_ttl                = 0
       default_ttl            = 0
       max_ttl                = 0
       compress               = true
       viewer_protocol_policy = "redirect-to-https"
     }

     # Cache behavior for static assets
     ordered_cache_behavior {
       path_pattern     = "/static/*"
       allowed_methods  = ["GET", "HEAD"]
       cached_methods   = ["GET", "HEAD"]
       target_origin_id = "ALB-pythonmasteryhub"

       forwarded_values {
         query_string = false
         cookies {
           forward = "none"
         }
       }

       min_ttl                = 86400
       default_ttl            = 31536000
       max_ttl                = 31536000
       compress               = true
       viewer_protocol_policy = "redirect-to-https"
     }

     price_class = "PriceClass_100"

     restrictions {
       geo_restriction {
         restriction_type = "none"
       }
     }

     viewer_certificate {
       acm_certificate_arn      = aws_acm_certificate.main.arn
       ssl_support_method       = "sni-only"
       minimum_protocol_version = "TLSv1.2_2021"
     }

     tags = {
       Environment = "production"
       Application = "python-mastery-hub"
     }
   }

Monitoring and Observability
----------------------------

Prometheus and Grafana Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Prometheus Configuration:**

.. code-block:: yaml

   # k8s/monitoring/prometheus.yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: prometheus-config
     namespace: monitoring
   data:
     prometheus.yml: |
       global:
         scrape_interval: 15s
         evaluation_interval: 15s

       rule_files:
         - "/etc/prometheus/rules/*.yml"

       scrape_configs:
         - job_name: 'kubernetes-pods'
           kubernetes_sd_configs:
           - role: pod
           relabel_configs:
           - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
             action: keep
             regex: true
           - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
             action: replace
             target_label: __metrics_path__
             regex: (.+)

         - job_name: 'python-mastery-hub'
           static_configs:
           - targets: ['python-mastery-hub-service:80']
           metrics_path: /metrics
           scrape_interval: 30s

**Application Metrics:**

.. code-block:: python

   # src/python_mastery_hub/monitoring/metrics.py
   from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
   from prometheus_client import multiprocess, generate_latest
   from typing import Dict, Any
   import time

   # Create metrics registry
   REGISTRY = CollectorRegistry()

   # Request metrics
   REQUEST_COUNT = Counter(
       'http_requests_total',
       'Total HTTP requests',
       ['method', 'endpoint', 'status_code'],
       registry=REGISTRY
   )

   REQUEST_DURATION = Histogram(
       'http_request_duration_seconds',
       'HTTP request duration in seconds',
       ['method', 'endpoint'],
       registry=REGISTRY
   )

   # Business metrics
   EXERCISE_SUBMISSIONS = Counter(
       'exercise_submissions_total',
       'Total exercise submissions',
       ['exercise_id', 'success'],
       registry=REGISTRY
   )

   ACTIVE_USERS = Gauge(
       'active_users_current',
       'Current number of active users',
       registry=REGISTRY
   )

   USER_PROGRESS = Histogram(
       'user_progress_score',
       'User exercise scores',
       ['difficulty_level'],
       registry=REGISTRY
   )

   # System metrics
   DATABASE_CONNECTIONS = Gauge(
       'database_connections_active',
       'Active database connections',
       registry=REGISTRY
   )

   CACHE_HIT_RATE = Gauge(
       'cache_hit_rate',
       'Cache hit rate percentage',
       registry=REGISTRY
   )

   class MetricsMiddleware:
       """Middleware to collect HTTP metrics."""
       
       async def __call__(self, request, call_next):
           start_time = time.time()
           
           response = await call_next(request)
           
           duration = time.time() - start_time
           
           REQUEST_COUNT.labels(
               method=request.method,
               endpoint=request.url.path,
               status_code=response.status_code
           ).inc()
           
           REQUEST_DURATION.labels(
               method=request.method,
               endpoint=request.url.path
           ).observe(duration)
           
           return response

**Grafana Dashboard Configuration:**

.. code-block:: json

   {
     "dashboard": {
       "title": "Python Mastery Hub - Application Metrics",
       "panels": [
         {
           "title": "Request Rate",
           "type": "graph",
           "targets": [
             {
               "expr": "rate(http_requests_total[5m])",
               "legendFormat": "{{method}} {{endpoint}}"
             }
           ],
           "yAxes": [
             {
               "label": "Requests/sec"
             }
           ]
         },
         {
           "title": "Response Time",
           "type": "graph", 
           "targets": [
             {
               "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
               "legendFormat": "95th percentile"
             },
             {
               "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
               "legendFormat": "50th percentile"
             }
           ]
         },
         {
           "title": "Active Users",
           "type": "singlestat",
           "targets": [
             {
               "expr": "active_users_current"
             }
           ]
         },
         {
           "title": "Exercise Submission Success Rate",
           "type": "graph",
           "targets": [
             {
               "expr": "rate(exercise_submissions_total{success=\"true\"}[5m]) / rate(exercise_submissions_total[5m]) * 100",
               "legendFormat": "Success Rate %"
             }
           ]
         }
       ]
     }
   }

Logging and Tracing
~~~~~~~~~~~~~~~~~~

**Centralized Logging with ELK Stack:**

.. code-block:: yaml

   # k8s/logging/elasticsearch.yaml
   apiVersion: elasticsearch.k8s.elastic.co/v1
   kind: Elasticsearch
   metadata:
     name: elasticsearch
     namespace: logging
   spec:
     version: 7.15.0
     nodeSets:
     - name: default
       count: 3
       config:
         node.store.allow_mmap: false
         xpack.security.enabled: true
         xpack.security.transport.ssl.enabled: true
         xpack.security.http.ssl.enabled: true
       podTemplate:
         spec:
           containers:
           - name: elasticsearch
             resources:
               requests:
                 memory: 2Gi
                 cpu: 1
               limits:
                 memory: 4Gi
                 cpu: 2
             env:
             - name: ES_JAVA_OPTS
               value: "-Xms2g -Xmx2g"
       volumeClaimTemplates:
       - metadata:
           name: elasticsearch-data
         spec:
           accessModes:
           - ReadWriteOnce
           resources:
             requests:
               storage: 100Gi

**Structured Logging Configuration:**

.. code-block:: python

   # src/python_mastery_hub/utils/logging_config.py
   import logging
   import sys
   from typing import Dict, Any
   import json
   from datetime import datetime

   class JSONFormatter(logging.Formatter):
       """JSON formatter for structured logging."""
       
       def format(self, record: logging.LogRecord) -> str:
           log_data = {
               'timestamp': datetime.utcnow().isoformat(),
               'level': record.levelname,
               'logger': record.name,
               'message': record.getMessage(),
               'module': record.module,
               'function': record.funcName,
               'line': record.lineno
           }
           
           # Add extra fields if present
           if hasattr(record, 'user_id'):
               log_data['user_id'] = record.user_id
           if hasattr(record, 'request_id'):
               log_data['request_id'] = record.request_id
           if hasattr(record, 'exercise_id'):
               log_data['exercise_id'] = record.exercise_id
               
           # Add exception info if present
           if record.exc_info:
               log_data['exception'] = self.formatException(record.exc_info)
               
           return json.dumps(log_data)

   def setup_logging(app_name: str = "python_mastery_hub") -> None:
       """Setup application logging configuration."""
       
       # Create root logger
       root_logger = logging.getLogger()
       root_logger.setLevel(logging.INFO)
       
       # Remove existing handlers
       root_logger.handlers.clear()
       
       # Console handler with JSON formatting
       console_handler = logging.StreamHandler(sys.stdout)
       console_handler.setFormatter(JSONFormatter())
       root_logger.addHandler(console_handler)
       
       # Set specific logger levels
       logging.getLogger("uvicorn").setLevel(logging.INFO)
       logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
       logging.getLogger("httpx").setLevel(logging.WARNING)

CI/CD Pipeline
-------------

GitHub Actions Workflow
~~~~~~~~~~~~~~~~~~~~~~

**Complete CI/CD Pipeline:**

.. code-block:: yaml

   # .github/workflows/deploy.yml
   name: CI/CD Pipeline

   on:
     push:
       branches: [main, develop]
     pull_request:
       branches: [main]
     release:
       types: [published]

   env:
     REGISTRY: ghcr.io
     IMAGE_NAME: ${{ github.repository }}

   jobs:
     test:
       runs-on: ubuntu-latest
       strategy:
         matrix:
           python-version: [3.9, "3.10", "3.11"]

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
       - name: Checkout code
         uses: actions/checkout@v3

       - name: Set up Python ${{ matrix.python-version }}
         uses: actions/setup-python@v3
         with:
           python-version: ${{ matrix.python-version }}

       - name: Cache dependencies
         uses: actions/cache@v3
         with:
           path: ~/.cache/pip
           key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
           restore-keys: |
             ${{ runner.os }}-pip-

       - name: Install dependencies
         run: |
           python -m pip install --upgrade pip
           pip install -e ".[dev]"

       - name: Run linting
         run: |
           black --check src/ tests/
           isort --check-only src/ tests/
           flake8 src/ tests/
           mypy src/

       - name: Run security checks
         run: |
           bandit -r src/
           safety check

       - name: Run tests
         run: |
           pytest tests/ -v --cov=src/python_mastery_hub --cov-report=xml
         env:
           DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
           REDIS_URL: redis://localhost:6379

       - name: Upload coverage to Codecov
         uses: codecov/codecov-action@v3
         with:
           file: ./coverage.xml

     security-scan:
       runs-on: ubuntu-latest
       steps:
       - name: Checkout code
         uses: actions/checkout@v3

       - name: Run Trivy vulnerability scanner
         uses: aquasecurity/trivy-action@master
         with:
           scan-type: 'fs'
           scan-ref: '.'
           format: 'sarif'
           output: 'trivy-results.sarif'

       - name: Upload Trivy scan results
         uses: github/codeql-action/upload-sarif@v2
         with:
           sarif_file: 'trivy-results.sarif'

     build:
       needs: [test, security-scan]
       runs-on: ubuntu-latest
       outputs:
         image-tag: ${{ steps.meta.outputs.tags }}
         image-digest: ${{ steps.build.outputs.digest }}
       steps:
       - name: Checkout code
         uses: actions/checkout@v3

       - name: Set up Docker Buildx
         uses: docker/setup-buildx-action@v2

       - name: Log in to Container Registry
         uses: docker/login-action@v2
         with:
           registry: ${{ env.REGISTRY }}
           username: ${{ github.actor }}
           password: ${{ secrets.GITHUB_TOKEN }}

       - name: Extract metadata
         id: meta
         uses: docker/metadata-action@v4
         with:
           images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
           tags: |
             type=ref,event=branch
             type=ref,event=pr
             type=semver,pattern={{version}}
             type=semver,pattern={{major}}.{{minor}}
             type=sha,prefix={{branch}}-

       - name: Build and push Docker image
         id: build
         uses: docker/build-push-action@v4
         with:
           context: .
           target: production
           push: true
           tags: ${{ steps.meta.outputs.tags }}
           labels: ${{ steps.meta.outputs.labels }}
           cache-from: type=gha
           cache-to: type=gha,mode=max

     deploy-staging:
       if: github.ref == 'refs/heads/develop'
       needs: build
       runs-on: ubuntu-latest
       environment: staging
       steps:
       - name: Checkout code
         uses: actions/checkout@v3

       - name: Configure kubectl
         uses: azure/k8s-set-context@v2
         with:
           method: kubeconfig
           kubeconfig: ${{ secrets.STAGING_KUBECONFIG }}

       - name: Deploy to staging
         run: |
           cd k8s/staging
           kustomize edit set image app=${{ needs.build.outputs.image-tag }}
           kubectl apply -k .
           kubectl rollout status deployment/python-mastery-hub-app -n python-mastery-hub-staging

       - name: Run smoke tests
         run: |
           kubectl wait --for=condition=ready pod -l app=python-mastery-hub -n python-mastery-hub-staging --timeout=300s
           curl -f https://staging.pythonmasteryhub.com/health

     deploy-production:
       if: github.event_name == 'release'
       needs: build
       runs-on: ubuntu-latest
       environment: production
       steps:
       - name: Checkout code
         uses: actions/checkout@v3

       - name: Configure kubectl
         uses: azure/k8s-set-context@v2
         with:
           method: kubeconfig
           kubeconfig: ${{ secrets.PRODUCTION_KUBECONFIG }}

       - name: Deploy to production
         run: |
           cd k8s/production
           kustomize edit set image app=${{ needs.build.outputs.image-tag }}
           kubectl apply -k .
           kubectl rollout status deployment/python-mastery-hub-app -n python-mastery-hub-prod

       - name: Verify deployment
         run: |
           kubectl wait --for=condition=ready pod -l app=python-mastery-hub -n python-mastery-hub-prod --timeout=600s
           curl -f https://api.pythonmasteryhub.com/health

       - name: Post-deployment tests
         run: |
           pytest tests/e2e/production/ -v

Backup and Disaster Recovery
----------------------------

Database Backup Strategy
~~~~~~~~~~~~~~~~~~~~~~~~

**Automated Backup CronJob:**

.. code-block:: yaml

   # k8s/backup/postgres-backup.yaml
   apiVersion: batch/v1
   kind: CronJob
   metadata:
     name: postgres-backup
     namespace: python-mastery-hub-prod
   spec:
     schedule: "0 2 * * *"  # Daily at 2 AM
     jobTemplate:
       spec:
         template:
           spec:
             containers:
             - name: postgres-backup
               image: postgres:13-alpine
               env:
               - name: PGPASSWORD
                 valueFrom:
                   secretKeyRef:
                     name: postgres-credentials
                     key: password
               command:
               - /bin/bash
               - -c
               - |
                 BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
                 pg_dump -h postgres-service -U postgres python_mastery_hub > /tmp/$BACKUP_FILE
                 
                 # Upload to S3
                 aws s3 cp /tmp/$BACKUP_FILE s3://pythonmasteryhub-backups/postgres/$BACKUP_FILE
                 
                 # Clean up local file
                 rm /tmp/$BACKUP_FILE
                 
                 # Remove old backups (keep 30 days)
                 aws s3 ls s3://pythonmasteryhub-backups/postgres/ | \
                   awk '$1 < "'$(date -d '30 days ago' '+%Y-%m-%d')'" {print $4}' | \
                   xargs -I {} aws s3 rm s3://pythonmasteryhub-backups/postgres/{}
               volumeMounts:
               - name: aws-credentials
                 mountPath: /root/.aws
                 readOnly: true
             volumes:
             - name: aws-credentials
               secret:
                 secretName: aws-credentials
             restartPolicy: OnFailure

**Point-in-Time Recovery Setup:**

.. code-block:: yaml

   # k8s/backup/postgres-pitr.yaml
   apiVersion: postgresql.cnpg.io/v1
   kind: Cluster
   metadata:
     name: postgres-cluster
     namespace: python-mastery-hub-prod
   spec:
     instances: 3
     
     backup:
       retentionPolicy: "30d"
       barmanObjectStore:
         destinationPath: "s3://pythonmasteryhub-backups/postgres-wal"
         s3Credentials:
           accessKeyId:
             name: backup-credentials
             key: ACCESS_KEY_ID
           secretAccessKey:
             name: backup-credentials
             key: SECRET_ACCESS_KEY
         wal:
           retention: "7d"
           maxParallel: 8
         data:
           retention: "30d"
           jobs: 2
         
     # Enable point-in-time recovery
     recovery:
       source: "postgres-cluster"
       
     monitoring:
       enabled: true
       prometheusRule:
         enabled: true

**Disaster Recovery Procedure:**

.. code-block:: bash

   #!/bin/bash
   # scripts/disaster-recovery.sh
   
   set -e
   
   # Disaster Recovery Script for Python Mastery Hub
   
   NAMESPACE="python-mastery-hub-prod"
   BACKUP_BUCKET="pythonmasteryhub-backups"
   
   # Function to restore from latest backup
   restore_from_backup() {
       echo "Starting disaster recovery process..."
       
       # Get latest backup
       LATEST_BACKUP=$(aws s3 ls s3://$BACKUP_BUCKET/postgres/ | \
                      sort | tail -n 1 | awk '{print $4}')
       
       echo "Latest backup: $LATEST_BACKUP"
       
       # Download backup
       aws s3 cp s3://$BACKUP_BUCKET/postgres/$LATEST_BACKUP /tmp/
       
       # Scale down application
       kubectl scale deployment python-mastery-hub-app --replicas=0 -n $NAMESPACE
       
       # Drop and recreate database
       kubectl exec -it postgres-0 -n $NAMESPACE -- \
           psql -U postgres -c "DROP DATABASE IF EXISTS python_mastery_hub;"
       kubectl exec -it postgres-0 -n $NAMESPACE -- \
           psql -U postgres -c "CREATE DATABASE python_mastery_hub;"
       
       # Restore backup
       kubectl cp /tmp/$LATEST_BACKUP postgres-0:/tmp/ -n $NAMESPACE
       kubectl exec -it postgres-0 -n $NAMESPACE -- \
           psql -U postgres python_mastery_hub < /tmp/$LATEST_BACKUP
       
       # Scale up application
       kubectl scale deployment python-mastery-hub-app --replicas=3 -n $NAMESPACE
       
       # Verify health
       kubectl wait --for=condition=ready pod -l app=python-mastery-hub -n $NAMESPACE --timeout=300s
       
       echo "Disaster recovery completed successfully!"
   }
   
   # Function to restore to specific point in time
   restore_to_point_in_time() {
       local target_time=$1
       
       echo "Restoring to point in time: $target_time"
       
       # Create recovery cluster
       cat <<EOF | kubectl apply -f -
   apiVersion: postgresql.cnpg.io/v1
   kind: Cluster
   metadata:
     name: postgres-recovery
     namespace: $NAMESPACE
   spec:
     instances: 1
     
     bootstrap:
       recovery:
         source: postgres-cluster
         recoveryTarget:
           targetTime: "$target_time"
         
     externalClusters:
     - name: postgres-cluster
       barmanObjectStore:
         destinationPath: "s3://$BACKUP_BUCKET/postgres-wal"
         s3Credentials:
           accessKeyId:
             name: backup-credentials
             key: ACCESS_KEY_ID
           secretAccessKey:
             name: backup-credentials
             key: SECRET_ACCESS_KEY
   EOF
       
       echo "Recovery cluster created. Manual verification required."
   }
   
   # Main execution
   case "$1" in
       "latest")
           restore_from_backup
           ;;
       "pitr")
           if [ -z "$2" ]; then
               echo "Usage: $0 pitr 'YYYY-MM-DD HH:MM:SS'"
               exit 1
           fi
           restore_to_point_in_time "$2"
           ;;
       *)
           echo "Usage: $0 {latest|pitr}"
           echo "  latest - Restore from latest backup"
           echo "  pitr - Point-in-time recovery"
           exit 1
           ;;
   esac

Multi-Region Deployment
~~~~~~~~~~~~~~~~~~~~~~

**Primary Region Configuration:**

.. code-block:: yaml

   # k8s/multi-region/primary-region.yaml
   apiVersion: argoproj.io/v1alpha1
   kind: Application
   metadata:
     name: python-mastery-hub-primary
     namespace: argocd
   spec:
     project: default
     source:
       repoURL: https://github.com/your-org/python-mastery-hub
       targetRevision: main
       path: k8s/production
       kustomize:
         namePrefix: primary-
         commonLabels:
           region: us-east-1
           role: primary
     destination:
       server: https://kubernetes.default.svc
       namespace: python-mastery-hub-prod
     syncPolicy:
       automated:
         prune: true
         selfHeal: true

**Secondary Region Configuration:**

.. code-block:: yaml

   # k8s/multi-region/secondary-region.yaml
   apiVersion: argoproj.io/v1alpha1
   kind: Application
   metadata:
     name: python-mastery-hub-secondary
     namespace: argocd
   spec:
     project: default
     source:
       repoURL: https://github.com/your-org/python-mastery-hub
       targetRevision: main
       path: k8s/production
       kustomize:
         namePrefix: secondary-
         commonLabels:
           region: us-west-2
           role: secondary
         patchesStrategicMerge:
         - secondary-patches.yaml
     destination:
       server: https://us-west-2-kubernetes-cluster
       namespace: python-mastery-hub-prod
     syncPolicy:
       automated:
         prune: true
         selfHeal: true

**Database Replication:**

.. code-block:: yaml

   # k8s/multi-region/postgres-replica.yaml
   apiVersion: postgresql.cnpg.io/v1
   kind: Cluster
   metadata:
     name: postgres-replica
     namespace: python-mastery-hub-prod
   spec:
     instances: 2
     
     bootstrap:
       pg_basebackup:
         source: postgres-primary
         
     externalClusters:
     - name: postgres-primary
       connectionParameters:
         host: postgres-primary.us-east-1.example.com
         user: streaming_replica
         dbname: postgres
         sslmode: require
       password:
         name: replica-credentials
         key: password

Security Hardening
------------------

Network Policies
~~~~~~~~~~~~~~~

**Application Network Policy:**

.. code-block:: yaml

   # k8s/security/network-policy.yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: python-mastery-hub-netpol
     namespace: python-mastery-hub-prod
   spec:
     podSelector:
       matchLabels:
         app: python-mastery-hub
     policyTypes:
     - Ingress
     - Egress
     ingress:
     - from:
       - namespaceSelector:
           matchLabels:
             name: ingress-nginx
       - podSelector:
           matchLabels:
             app: load-balancer
       ports:
       - protocol: TCP
         port: 8000
     egress:
     - to:
       - podSelector:
           matchLabels:
             app: postgres
       ports:
       - protocol: TCP
         port: 5432
     - to:
       - podSelector:
           matchLabels:
             app: redis
       ports:
       - protocol: TCP
         port: 6379
     - to: []  # Allow all external traffic for API calls
       ports:
       - protocol: TCP
         port: 443
       - protocol: TCP
         port: 80

**Database Network Policy:**

.. code-block:: yaml

   # k8s/security/postgres-netpol.yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: postgres-netpol
     namespace: python-mastery-hub-prod
   spec:
     podSelector:
       matchLabels:
         app: postgres
     policyTypes:
     - Ingress
     ingress:
     - from:
       - podSelector:
           matchLabels:
             app: python-mastery-hub
       - podSelector:
           matchLabels:
             app: backup-job
       ports:
       - protocol: TCP
         port: 5432

Pod Security Standards
~~~~~~~~~~~~~~~~~~~~

**Pod Security Policy:**

.. code-block:: yaml

   # k8s/security/pod-security-standards.yaml
   apiVersion: v1
   kind: Namespace
   metadata:
     name: python-mastery-hub-prod
     labels:
       pod-security.kubernetes.io/enforce: restricted
       pod-security.kubernetes.io/audit: restricted
       pod-security.kubernetes.io/warn: restricted

**Security Context Configuration:**

.. code-block:: yaml

   # k8s/security/security-context.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: python-mastery-hub-app
   spec:
     template:
       spec:
         securityContext:
           runAsNonRoot: true
           runAsUser: 1000
           runAsGroup: 1000
           fsGroup: 1000
           seccompProfile:
             type: RuntimeDefault
         containers:
         - name: app
           securityContext:
             allowPrivilegeEscalation: false
             readOnlyRootFilesystem: true
             runAsNonRoot: true
             runAsUser: 1000
             capabilities:
               drop:
               - ALL
           volumeMounts:
           - name: tmp
             mountPath: /tmp
           - name: cache
             mountPath: /app/cache
         volumes:
         - name: tmp
           emptyDir: {}
         - name: cache
           emptyDir: {}

Secrets Management
~~~~~~~~~~~~~~~~

**External Secrets Operator:**

.. code-block:: yaml

   # k8s/security/external-secret.yaml
   apiVersion: external-secrets.io/v1beta1
   kind: ExternalSecret
   metadata:
     name: app-secrets
     namespace: python-mastery-hub-prod
   spec:
     refreshInterval: 300s
     secretStoreRef:
       name: vault-secret-store
       kind: SecretStore
     target:
       name: app-secrets
       creationPolicy: Owner
     data:
     - secretKey: DATABASE_PASSWORD
       remoteRef:
         key: pythonmasteryhub/database
         property: password
     - secretKey: JWT_SECRET_KEY
       remoteRef:
         key: pythonmasteryhub/jwt
         property: secret_key
     - secretKey: REDIS_PASSWORD
       remoteRef:
         key: pythonmasteryhub/redis
         property: password

**Vault Secret Store:**

.. code-block:: yaml

   # k8s/security/vault-secret-store.yaml
   apiVersion: external-secrets.io/v1beta1
   kind: SecretStore
   metadata:
     name: vault-secret-store
     namespace: python-mastery-hub-prod
   spec:
     provider:
       vault:
         server: "https://vault.example.com"
         path: "secret"
         version: "v2"
         auth:
           kubernetes:
             mountPath: "kubernetes"
             role: "python-mastery-hub"
             secretRef:
               name: vault-auth
               key: token

Performance Optimization
------------------------

Database Performance Tuning
~~~~~~~~~~~~~~~~~~~~~~~~~~

**PostgreSQL Optimization:**

.. code-block:: sql

   -- scripts/postgres-tuning.sql
   
   -- Connection and memory settings
   ALTER SYSTEM SET max_connections = 200;
   ALTER SYSTEM SET shared_buffers = '256MB';
   ALTER SYSTEM SET effective_cache_size = '1GB';
   ALTER SYSTEM SET work_mem = '4MB';
   ALTER SYSTEM SET maintenance_work_mem = '64MB';
   
   -- Checkpoint and WAL settings
   ALTER SYSTEM SET checkpoint_completion_target = 0.9;
   ALTER SYSTEM SET wal_buffers = '16MB';
   ALTER SYSTEM SET default_statistics_target = 100;
   
   -- Query optimization
   ALTER SYSTEM SET random_page_cost = 1.1;
   ALTER SYSTEM SET seq_page_cost = 1.0;
   ALTER SYSTEM SET cpu_tuple_cost = 0.01;
   ALTER SYSTEM SET cpu_index_tuple_cost = 0.005;
   ALTER SYSTEM SET cpu_operator_cost = 0.0025;
   
   -- Reload configuration
   SELECT pg_reload_conf();
   
   -- Create performance monitoring views
   CREATE OR REPLACE VIEW performance_stats AS
   SELECT 
       schemaname,
       tablename,
       seq_scan,
       seq_tup_read,
       idx_scan,
       idx_tup_fetch,
       n_tup_ins,
       n_tup_upd,
       n_tup_del
   FROM pg_stat_user_tables
   ORDER BY seq_scan DESC;
   
   -- Index usage monitoring
   CREATE OR REPLACE VIEW index_usage AS
   SELECT 
       schemaname,
       tablename,
       indexname,
       idx_scan,
       idx_tup_read,
       idx_tup_fetch
   FROM pg_stat_user_indexes
   ORDER BY idx_scan DESC;

**Database Index Strategy:**

.. code-block:: sql

   -- scripts/create-indexes.sql
   
   -- User-related indexes
   CREATE INDEX CONCURRENTLY idx_users_email_active 
   ON users(email) WHERE is_active = true;
   
   CREATE INDEX CONCURRENTLY idx_users_created_at 
   ON users(created_at DESC);
   
   -- Progress tracking indexes
   CREATE INDEX CONCURRENTLY idx_user_progress_user_exercise 
   ON user_progress(user_id, exercise_id);
   
   CREATE INDEX CONCURRENTLY idx_user_progress_completed 
   ON user_progress(completed_at DESC) WHERE completed_at IS NOT NULL;
   
   CREATE INDEX CONCURRENTLY idx_user_progress_score 
   ON user_progress(score DESC) WHERE score IS NOT NULL;
   
   -- Exercise indexes
   CREATE INDEX CONCURRENTLY idx_exercises_category_difficulty 
   ON exercises(category, difficulty_level);
   
   CREATE INDEX CONCURRENTLY idx_exercises_updated 
   ON exercises(updated_at DESC);
   
   -- Submission indexes
   CREATE INDEX CONCURRENTLY idx_submissions_user_exercise 
   ON submissions(user_id, exercise_id, submitted_at DESC);
   
   CREATE INDEX CONCURRENTLY idx_submissions_recent 
   ON submissions(submitted_at DESC);
   
   -- Composite indexes for common queries
   CREATE INDEX CONCURRENTLY idx_user_progress_stats 
   ON user_progress(user_id, score, completed_at) 
   WHERE completed_at IS NOT NULL;

Application Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Connection Pooling Configuration:**

.. code-block:: python

   # src/python_mastery_hub/config/database.py
   from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
   from sqlalchemy.orm import sessionmaker
   from sqlalchemy.pool import QueuePool
   import asyncio
   
   class DatabaseManager:
       def __init__(self, database_url: str):
           self.engine = create_async_engine(
               database_url,
               # Connection pool settings
               poolclass=QueuePool,
               pool_size=20,              # Number of connections to maintain
               max_overflow=30,           # Additional connections allowed
               pool_pre_ping=True,        # Validate connections before use
               pool_recycle=3600,         # Recycle connections every hour
               
               # Query optimization
               echo=False,                # Set to True for query debugging
               future=True,
               
               # Connection timeouts
               connect_args={
                   "command_timeout": 60,
                   "server_settings": {
                       "application_name": "python_mastery_hub",
                       "jit": "off",  # Disable JIT for better performance on small queries
                   }
               }
           )
           
           self.async_session = sessionmaker(
               self.engine,
               class_=AsyncSession,
               expire_on_commit=False
           )
   
       async def get_session(self) -> AsyncSession:
           async with self.async_session() as session:
               yield session
   
       async def close(self):
           await self.engine.dispose()

**Caching Layer Optimization:**

.. code-block:: python

   # src/python_mastery_hub/infrastructure/cache.py
   import redis.asyncio as redis
   import json
   import pickle
   from typing import Any, Optional, Dict
   from datetime import timedelta
   
   class OptimizedCacheManager:
       def __init__(self, redis_url: str):
           self.redis_pool = redis.ConnectionPool.from_url(
               redis_url,
               max_connections=50,
               retry_on_timeout=True,
               socket_keepalive=True,
               socket_keepalive_options={
                   1: 1,    # TCP_KEEPIDLE
                   2: 3,    # TCP_KEEPINTVL  
                   3: 5,    # TCP_KEEPCNT
               }
           )
           self.redis = redis.Redis(connection_pool=self.redis_pool)
           
       async def get(self, key: str, deserialize: bool = True) -> Optional[Any]:
           """Get value from cache with optional deserialization."""
           try:
               value = await self.redis.get(key)
               if value is None:
                   return None
                   
               if deserialize:
                   try:
                       return json.loads(value)
                   except (json.JSONDecodeError, TypeError):
                       return pickle.loads(value)
               return value
               
           except Exception as e:
               # Log error but don't fail the request
               logger.error(f"Cache get error for key {key}: {e}")
               return None
   
       async def set(
           self, 
           key: str, 
           value: Any, 
           ttl: Optional[timedelta] = None,
           serialize: bool = True
       ) -> bool:
           """Set value in cache with optional serialization."""
           try:
               if serialize:
                   try:
                       serialized_value = json.dumps(value)
                   except (TypeError, ValueError):
                       serialized_value = pickle.dumps(value)
               else:
                   serialized_value = value
                   
               await self.redis.set(key, serialized_value, ex=ttl)
               return True
               
           except Exception as e:
               logger.error(f"Cache set error for key {key}: {e}")
               return False
   
       async def delete_pattern(self, pattern: str) -> int:
           """Delete all keys matching pattern."""
           try:
               keys = await self.redis.keys(pattern)
               if keys:
                   return await self.redis.delete(*keys)
               return 0
           except Exception as e:
               logger.error(f"Cache delete pattern error for {pattern}: {e}")
               return 0
   
       async def pipeline_set(self, items: Dict[str, Any], ttl: Optional[timedelta] = None):
           """Set multiple items efficiently using pipeline."""
           try:
               pipe = self.redis.pipeline()
               for key, value in items.items():
                   try:
                       serialized_value = json.dumps(value)
                   except (TypeError, ValueError):
                       serialized_value = pickle.dumps(value)
                   pipe.set(key, serialized_value, ex=ttl)
               await pipe.execute()
           except Exception as e:
               logger.error(f"Pipeline set error: {e}")

Maintenance and Operations
-------------------------

Regular Maintenance Tasks
~~~~~~~~~~~~~~~~~~~~~~~~

**Automated Maintenance CronJobs:**

.. code-block:: yaml

   # k8s/maintenance/cleanup-jobs.yaml
   apiVersion: batch/v1
   kind: CronJob
   metadata:
     name: database-cleanup
     namespace: python-mastery-hub-prod
   spec:
     schedule: "0 3 * * 0"  # Weekly on Sunday at 3 AM
     jobTemplate:
       spec:
         template:
           spec:
             containers:
             - name: db-cleanup
               image: python-mastery-hub:latest
               command:
               - python
               - -m
               - python_mastery_hub.maintenance.database_cleanup
               env:
               - name: DATABASE_URL
                 valueFrom:
                   secretKeyRef:
                     name: app-secrets
                     key: DATABASE_URL
             restartPolicy: OnFailure

**Database Maintenance Script:**

.. code-block:: python

   # src/python_mastery_hub/maintenance/database_cleanup.py
   import asyncio
   import logging
   from datetime import datetime, timedelta
   from sqlalchemy.ext.asyncio import create_async_engine
   from sqlalchemy import text
   
   logger = logging.getLogger(__name__)
   
   class DatabaseMaintenance:
       def __init__(self, database_url: str):
           self.engine = create_async_engine(database_url)
   
       async def cleanup_old_sessions(self, days_old: int = 30):
           """Remove old user sessions."""
           cutoff_date = datetime.utcnow() - timedelta(days=days_old)
           
           async with self.engine.begin() as conn:
               result = await conn.execute(
                   text("DELETE FROM user_sessions WHERE created_at < :cutoff"),
                   {"cutoff": cutoff_date}
               )
               logger.info(f"Cleaned up {result.rowcount} old sessions")
   
       async def cleanup_old_submissions(self, days_old: int = 90):
           """Archive old exercise submissions."""
           cutoff_date = datetime.utcnow() - timedelta(days=days_old)
           
           async with self.engine.begin() as conn:
               # Move to archive table
               await conn.execute(text("""
                   INSERT INTO submissions_archive 
                   SELECT * FROM submissions 
                   WHERE submitted_at < :cutoff
               """), {"cutoff": cutoff_date})
               
               # Delete from main table
               result = await conn.execute(
                   text("DELETE FROM submissions WHERE submitted_at < :cutoff"),
                   {"cutoff": cutoff_date}
               )
               logger.info(f"Archived {result.rowcount} old submissions")
   
       async def update_statistics(self):
           """Update table statistics for query optimization."""
           async with self.engine.begin() as conn:
               await conn.execute(text("ANALYZE;"))
               logger.info("Updated database statistics")
   
       async def vacuum_tables(self):
           """Vacuum tables to reclaim space."""
           tables = ["users", "submissions", "user_progress", "exercises"]
           
           async with self.engine.begin() as conn:
               for table in tables:
                   await conn.execute(text(f"VACUUM ANALYZE {table};"))
                   logger.info(f"Vacuumed table: {table}")
   
       async def run_maintenance(self):
           """Run all maintenance tasks."""
           logger.info("Starting database maintenance")
           
           try:
               await self.cleanup_old_sessions()
               await self.cleanup_old_submissions()
               await self.update_statistics()
               await self.vacuum_tables()
               logger.info("Database maintenance completed successfully")
           except Exception as e:
               logger.error(f"Database maintenance failed: {e}")
               raise
           finally:
               await self.engine.dispose()
   
   async def main():
       import os
       database_url = os.getenv("DATABASE_URL")
       maintenance = DatabaseMaintenance(database_url)
       await maintenance.run_maintenance()
   
   if __name__ == "__main__":
       asyncio.run(main())

Health Checks and Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Comprehensive Health Check Endpoint:**

.. code-block:: python

   # src/python_mastery_hub/web/api/health.py
   from fastapi import APIRouter, Depends, HTTPException
   from sqlalchemy.ext.asyncio import AsyncSession
   from sqlalchemy import text
   import asyncio
   import time
   from typing import Dict, Any
   
   router = APIRouter()
   
   class HealthChecker:
       def __init__(self, db: AsyncSession, cache_manager, queue_manager):
           self.db = db
           self.cache = cache_manager
           self.queue = queue_manager
   
       async def check_database(self) -> Dict[str, Any]:
           """Check database connectivity and performance."""
           try:
               start_time = time.time()
               result = await self.db.execute(text("SELECT 1"))
               response_time = time.time() - start_time
               
               return {
                   "status": "healthy",
                   "response_time_ms": round(response_time * 1000, 2),
                   "message": "Database connection successful"
               }
           except Exception as e:
               return {
                   "status": "unhealthy", 
                   "error": str(e),
                   "message": "Database connection failed"
               }
   
       async def check_cache(self) -> Dict[str, Any]:
           """Check cache connectivity and performance."""
           try:
               start_time = time.time()
               test_key = "health_check_test"
               await self.cache.set(test_key, "test_value", ttl=timedelta(seconds=10))
               value = await self.cache.get(test_key)
               await self.cache.delete(test_key)
               response_time = time.time() - start_time
               
               if value == "test_value":
                   return {
                       "status": "healthy",
                       "response_time_ms": round(response_time * 1000, 2),
                       "message": "Cache operations successful"
                   }
               else:
                   return {
                       "status": "unhealthy",
                       "message": "Cache value mismatch"
                   }
           except Exception as e:
               return {
                   "status": "unhealthy",
                   "error": str(e),
                   "message": "Cache connection failed"
               }
   
       async def check_queue(self) -> Dict[str, Any]:
           """Check message queue connectivity."""
           try:
               # Simple queue health check
               queue_info = await self.queue.get_queue_info()
               return {
                   "status": "healthy",
                   "active_jobs": queue_info.get("active", 0),
                   "pending_jobs": queue_info.get("pending", 0),
                   "message": "Queue system operational"
               }
           except Exception as e:
               return {
                   "status": "unhealthy",
                   "error": str(e),
                   "message": "Queue connection failed"
               }
   
   @router.get("/health")
   async def health_check(
       db: AsyncSession = Depends(get_db),
       cache_manager = Depends(get_cache_manager),
       queue_manager = Depends(get_queue_manager)
   ):
       """Comprehensive health check endpoint."""
       checker = HealthChecker(db, cache_manager, queue_manager)
       
       # Run all checks concurrently
       db_health, cache_health, queue_health = await asyncio.gather(
           checker.check_database(),
           checker.check_cache(), 
           checker.check_queue(),
           return_exceptions=True
       )
       
       # Determine overall health
       all_healthy = all(
           check.get("status") == "healthy" 
           for check in [db_health, cache_health, queue_health]
           if isinstance(check, dict)
       )
       
       status_code = 200 if all_healthy else 503
       
       return {
           "status": "healthy" if all_healthy else "unhealthy",
           "timestamp": datetime.utcnow().isoformat(),
           "checks": {
               "database": db_health,
               "cache": cache_health,
               "queue": queue_health
           }
       }
   
   @router.get("/ready")
   async def readiness_check():
       """Simple readiness check for Kubernetes."""
       return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}

This comprehensive deployment guide provides everything needed to deploy Python Mastery Hub from development to production, including security, monitoring, backup, and maintenance strategies. The configuration ensures high availability, scalability, and operational excellence.