# File: deployment/terraform/main.tf
# Main Terraform configuration for infrastructure provisioning

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.10"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }

  backend "s3" {
    bucket         = var.terraform_state_bucket
    key            = "terraform/state"
    region         = var.aws_region
    encrypt        = true
    dynamodb_table = var.terraform_lock_table
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project      = var.project_name
      Environment  = var.environment
      ManagedBy    = "Terraform"
      Owner        = var.owner
      CostCenter   = var.cost_center
      CreatedDate  = formatdate("YYYY-MM-DD", timestamp())
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

# Local values
locals {
  cluster_name = "${var.project_name}-${var.environment}"
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = var.owner
    CostCenter  = var.cost_center
  }

  vpc_cidr = var.vpc_cidr
  azs      = slice(data.aws_availability_zones.available.names, 0, 3)

  private_subnets = [
    cidrsubnet(local.vpc_cidr, 8, 1),
    cidrsubnet(local.vpc_cidr, 8, 2),
    cidrsubnet(local.vpc_cidr, 8, 3),
  ]

  public_subnets = [
    cidrsubnet(local.vpc_cidr, 8, 101),
    cidrsubnet(local.vpc_cidr, 8, 102),
    cidrsubnet(local.vpc_cidr, 8, 103),
  ]

  database_subnets = [
    cidrsubnet(local.vpc_cidr, 8, 201),
    cidrsubnet(local.vpc_cidr, 8, 202),
    cidrsubnet(local.vpc_cidr, 8, 203),
  ]
}

# VPC Module
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = local.cluster_name
  cidr = local.vpc_cidr

  azs                = local.azs
  private_subnets    = local.private_subnets
  public_subnets     = local.public_subnets
  database_subnets   = local.database_subnets

  enable_nat_gateway     = true
  single_nat_gateway     = var.environment == "development"
  enable_vpn_gateway     = false
  enable_dns_hostnames   = true
  enable_dns_support     = true

  # Database subnet group
  create_database_subnet_group = true
  database_subnet_group_name   = "${local.cluster_name}-db"

  # VPC Flow Logs
  enable_flow_log                      = true
  create_flow_log_cloudwatch_iam_role  = true
  create_flow_log_cloudwatch_log_group = true
  flow_log_cloudwatch_log_group_retention_in_days = 7

  tags = merge(local.common_tags, {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
  })

  public_subnet_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                      = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"             = "1"
  }
}

# Security Groups
resource "aws_security_group" "database" {
  name        = "${local.cluster_name}-database"
  description = "Security group for RDS database"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.cluster_name}-database"
  })
}

resource "aws_security_group" "redis" {
  name        = "${local.cluster_name}-redis"
  description = "Security group for ElastiCache Redis"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.cluster_name}-redis"
  })
}

resource "aws_security_group" "eks_cluster" {
  name        = "${local.cluster_name}-cluster"
  description = "Security group for EKS cluster"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [local.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.cluster_name}-cluster"
  })
}

# Database Module
module "database" {
  source = "./modules/database"

  cluster_name    = local.cluster_name
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.database_subnets
  security_groups = [aws_security_group.database.id]

  # Database configuration
  engine_version    = var.db_engine_version
  instance_class    = var.db_instance_class
  allocated_storage = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  
  database_name = var.db_name
  username      = var.db_username
  
  # Backup configuration
  backup_retention_period = var.db_backup_retention_period
  backup_window          = var.db_backup_window
  maintenance_window     = var.db_maintenance_window
  
  deletion_protection = var.environment == "production"
  skip_final_snapshot = var.environment != "production"

  tags = local.common_tags
}

# Web Application Module
module "web_app" {
  source = "./modules/web_app"

  cluster_name = local.cluster_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.private_subnets

  # EKS configuration
  cluster_version = var.eks_cluster_version
  node_groups     = var.eks_node_groups

  # Security groups
  cluster_security_group_id = aws_security_group.eks_cluster.id

  # Database connection
  database_endpoint = module.database.endpoint
  database_port     = module.database.port

  # Redis connection
  redis_endpoint = module.monitoring.redis_endpoint

  tags = local.common_tags
}

# Monitoring Module
module "monitoring" {
  source = "./modules/monitoring"

  cluster_name = local.cluster_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.private_subnets

  # Redis for monitoring data
  redis_node_type = var.redis_node_type
  redis_num_cache_nodes = var.redis_num_cache_nodes
  redis_security_groups = [aws_security_group.redis.id]

  # CloudWatch configuration
  log_retention_days = var.log_retention_days

  tags = local.common_tags
}

# S3 Buckets for application data
resource "aws_s3_bucket" "app_storage" {
  bucket = "${local.cluster_name}-app-storage"

  tags = merge(local.common_tags, {
    Name = "${local.cluster_name}-app-storage"
    Type = "ApplicationStorage"
  })
}

resource "aws_s3_bucket_versioning" "app_storage" {
  bucket = aws_s3_bucket.app_storage.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "app_storage" {
  bucket = aws_s3_bucket.app_storage.id

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_s3_bucket_public_access_block" "app_storage" {
  bucket = aws_s3_bucket.app_storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 bucket for backups
resource "aws_s3_bucket" "backups" {
  bucket = "${local.cluster_name}-backups"

  tags = merge(local.common_tags, {
    Name = "${local.cluster_name}-backups"
    Type = "Backups"
  })
}

resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.backups.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    id     = "backup_lifecycle"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_INFREQUENT_ACCESS"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }

    expiration {
      days = var.backup_retention_days
    }
  }
}

# IAM Role for the application
resource "aws_iam_role" "app_role" {
  name = "${local.cluster_name}-app-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = module.web_app.oidc_provider_arn
        }
        Condition = {
          StringEquals = {
            "${replace(module.web_app.oidc_provider_url, "https://", "")}:sub" = "system:serviceaccount:myapp-${var.environment}:myapp-service-account"
            "${replace(module.web_app.oidc_provider_url, "https://", "")}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy" "app_policy" {
  name = "${local.cluster_name}-app-policy"
  role = aws_iam_role.app_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "${aws_s3_bucket.app_storage.arn}/*",
          "${aws_s3_bucket.backups.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.app_storage.arn,
          aws_s3_bucket.backups.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = "arn:aws:secretsmanager:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:secret:${local.cluster_name}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/myapp/*"
      }
    ]
  })
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = local.cluster_name
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets

  enable_deletion_protection = var.environment == "production"

  tags = merge(local.common_tags, {
    Name = "${local.cluster_name}-alb"
  })
}

resource "aws_security_group" "alb" {
  name        = "${local.cluster_name}-alb"
  description = "Security group for Application Load Balancer"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.cluster_name}-alb"
  })
}

# Route53 hosted zone
resource "aws_route53_zone" "main" {
  count = var.create_route53_zone ? 1 : 0
  name  = var.domain_name

  tags = merge(local.common_tags, {
    Name = var.domain_name
  })
}

# ACM Certificate
resource "aws_acm_certificate" "main" {
  domain_name       = var.domain_name
  validation_method = "DNS"

  subject_alternative_names = [
    "*.${var.domain_name}"
  ]

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(local.common_tags, {
    Name = var.domain_name
  })
}

resource "aws_route53_record" "cert_validation" {
  for_each = var.create_route53_zone ? {
    for dvo in aws_acm_certificate.main.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  } : {}

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.main[0].zone_id
}

resource "aws_acm_certificate_validation" "main" {
  certificate_arn         = aws_acm_certificate.main.arn
  validation_record_fqdns = var.create_route53_zone ? [for record in aws_route53_record.cert_validation : record.fqdn] : []

  timeouts {
    create = "5m"
  }
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "main" {
  count = var.enable_cloudfront ? 1 : 0

  origin {
    domain_name = aws_lb.main.dns_name
    origin_id   = "ALB-${local.cluster_name}"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "${local.cluster_name} CloudFront Distribution"
  default_root_object = "index.html"

  aliases = var.create_route53_zone ? [var.domain_name, "www.${var.domain_name}"] : []

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "ALB-${local.cluster_name}"

    forwarded_values {
      query_string = true
      headers      = ["Authorization", "CloudFront-Forwarded-Proto"]

      cookies {
        forward = "all"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    compress               = true
  }

  # Cache behavior for static assets
  ordered_cache_behavior {
    path_pattern     = "/static/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "ALB-${local.cluster_name}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
  }

  # Cache behavior for API endpoints
  ordered_cache_behavior {
    path_pattern     = "/api/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "ALB-${local.cluster_name}"

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

  price_class = var.cloudfront_price_class

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate_validation.main.certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  web_acl_id = var.enable_waf ? aws_wafv2_web_acl.main[0].arn : null

  tags = merge(local.common_tags, {
    Name = "${local.cluster_name}-cloudfront"
  })
}

# WAF Web ACL
resource "aws_wafv2_web_acl" "main" {
  count = var.enable_waf ? 1 : 0

  name  = "${local.cluster_name}-waf"
  scope = "CLOUDFRONT"

  default_action {
    allow {}
  }

  rule {
    name     = "RateLimitRule"
    priority = 1

    override_action {
      none {}
    }

    statement {
      rate_based_statement {
        limit          = 2000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.cluster_name}-RateLimit"
      sampled_requests_enabled   = true
    }

    action {
      block {}
    }
  }

  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.cluster_name}-CommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 3

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.cluster_name}-BadInputs"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${local.cluster_name}-WAF"
    sampled_requests_enabled   = true
  }

  tags = merge(local.common_tags, {
    Name = "${local.cluster_name}-waf"
  })
}

# KMS Key for encryption
resource "aws_kms_key" "main" {
  description             = "KMS key for ${local.cluster_name}"
  deletion_window_in_days = var.environment == "production" ? 30 : 7
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name = "${local.cluster_name}-kms"
  })
}

resource "aws_kms_alias" "main" {
  name          = "alias/${local.cluster_name}"
  target_key_id = aws_kms_key.main.key_id
}

# Parameter Store for application configuration
resource "aws_ssm_parameter" "database_url" {
  name  = "/${local.cluster_name}/database/url"
  type  = "SecureString"
  value = "postgresql://${var.db_username}:${random_password.db_password.result}@${module.database.endpoint}:${module.database.port}/${var.db_name}"

  key_id = aws_kms_key.main.key_id

  tags = merge(local.common_tags, {
    Name = "${local.cluster_name}-database-url"
  })
}

resource "aws_ssm_parameter" "redis_url" {
  name  = "/${local.cluster_name}/redis/url"
  type  = "SecureString"
  value = "redis://${module.monitoring.redis_endpoint}:6379/0"

  key_id = aws_kms_key.main.key_id

  tags = merge(local.common_tags, {
    Name = "${local.cluster_name}-redis-url"
  })
}

# Random passwords
resource "random_password" "db_password" {
  length  = 32
  special = true
}

resource "random_password" "app_secret_key" {
  length  = 64
  special = true
}

resource "random_password" "jwt_secret_key" {
  length  = 64
  special = true
}

# Store secrets in AWS Secrets Manager
resource "aws_secretsmanager_secret" "app_secrets" {
  name                    = "${local.cluster_name}-app-secrets"
  description             = "Application secrets for ${local.cluster_name}"
  recovery_window_in_days = var.environment == "production" ? 30 : 0
  kms_key_id             = aws_kms_key.main.key_id

  tags = merge(local.common_tags, {
    Name = "${local.cluster_name}-app-secrets"
  })
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    database_url    = "postgresql://${var.db_username}:${random_password.db_password.result}@${module.database.endpoint}:${module.database.port}/${var.db_name}"
    redis_url       = "redis://${module.monitoring.redis_endpoint}:6379/0"
    secret_key      = random_password.app_secret_key.result
    jwt_secret_key  = random_password.jwt_secret_key.result
  })
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/aws/myapp/${local.cluster_name}"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.main.arn

  tags = merge(local.common_tags, {
    Name = "${local.cluster_name}-app-logs"
  })
}

# SNS Topic for alerts
resource "aws_sns_topic" "alerts" {
  name              = "${local.cluster_name}-alerts"
  kms_master_key_id = aws_kms_key.main.key_id

  tags = merge(local.common_tags, {
    Name = "${local.cluster_name}-alerts"
  })
}

resource "aws_sns_topic_subscription" "email_alerts" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "${local.cluster_name}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EKS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors EKS cluster CPU utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ClusterName = module.web_app.cluster_name
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "high_memory" {
  alarm_name          = "${local.cluster_name}-high-memory"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "MemoryUtilization"
  namespace           = "ContainerInsights"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors container memory utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ClusterName = module.web_app.cluster_name
  }

  tags = local.common_tags
}

# Output values
output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.web_app.cluster_endpoint
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.web_app.cluster_name
}

output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = module.database.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = module.monitoring.redis_endpoint
  sensitive   = true
}

output "load_balancer_dns" {
  description = "Application Load Balancer DNS name"
  value       = aws_lb.main.dns_name
}

output "cloudfront_domain" {
  description = "CloudFront distribution domain name"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.main[0].domain_name : null
}

output "s3_bucket_names" {
  description = "S3 bucket names"
  value = {
    app_storage = aws_s3_bucket.app_storage.bucket
    backups     = aws_s3_bucket.backups.bucket
  }
}

output "secrets_manager_arn" {
  description = "AWS Secrets Manager ARN"
  value       = aws_secretsmanager_secret.app_secrets.arn
}

output "kms_key_id" {
  description = "KMS key ID"
  value       = aws_kms_key.main.key_id
}