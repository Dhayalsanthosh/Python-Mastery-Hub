# File: deployment/terraform/variables.tf
# Terraform variables definition

# Project Configuration
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "myapp"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]*[a-z0-9]$", var.project_name))
    error_message = "Project name must start with a letter, contain only lowercase letters, numbers, and hyphens, and end with a letter or number."
  }
}

variable "environment" {
  description = "Environment name (e.g., development, staging, production)"
  type        = string

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "owner" {
  description = "Owner of the resources"
  type        = string
  default     = "DevOps Team"
}

variable "cost_center" {
  description = "Cost center for billing"
  type        = string
  default     = "Engineering"
}

# AWS Configuration
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"

  validation {
    condition = can(regex("^[a-z0-9-]+$", var.aws_region))
    error_message = "AWS region must be a valid region identifier."
  }
}

variable "terraform_state_bucket" {
  description = "S3 bucket for Terraform state"
  type        = string
}

variable "terraform_lock_table" {
  description = "DynamoDB table for Terraform state locking"
  type        = string
}

# Network Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block."
  }
}

variable "availability_zones_count" {
  description = "Number of availability zones to use"
  type        = number
  default     = 3

  validation {
    condition     = var.availability_zones_count >= 2 && var.availability_zones_count <= 4
    error_message = "Availability zones count must be between 2 and 4."
  }
}

# Database Configuration
variable "db_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.4"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"

  validation {
    condition = can(regex("^db\\.[a-z0-9]+\\.[a-z0-9]+$", var.db_instance_class))
    error_message = "DB instance class must be a valid RDS instance type."
  }
}

variable "db_allocated_storage" {
  description = "Initial allocated storage for RDS instance (GB)"
  type        = number
  default     = 20

  validation {
    condition     = var.db_allocated_storage >= 20 && var.db_allocated_storage <= 65536
    error_message = "DB allocated storage must be between 20 and 65536 GB."
  }
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for RDS instance (GB)"
  type        = number
  default     = 100

  validation {
    condition     = var.db_max_allocated_storage >= 20 && var.db_max_allocated_storage <= 65536
    error_message = "DB max allocated storage must be between 20 and 65536 GB."
  }
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "myapp"

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9_]*$", var.db_name))
    error_message = "Database name must start with a letter and contain only letters, numbers, and underscores."
  }
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "postgres"

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9_]*$", var.db_username))
    error_message = "Database username must start with a letter and contain only letters, numbers, and underscores."
  }
}

variable "db_backup_retention_period" {
  description = "Backup retention period in days"
  type        = number
  default     = 7

  validation {
    condition     = var.db_backup_retention_period >= 0 && var.db_backup_retention_period <= 35
    error_message = "Backup retention period must be between 0 and 35 days."
  }
}

variable "db_backup_window" {
  description = "Preferred backup window"
  type        = string
  default     = "03:00-04:00"

  validation {
    condition     = can(regex("^[0-9]{2}:[0-9]{2}-[0-9]{2}:[0-9]{2}$", var.db_backup_window))
    error_message = "Backup window must be in format HH:MM-HH:MM."
  }
}

variable "db_maintenance_window" {
  description = "Preferred maintenance window"
  type        = string
  default     = "sun:04:00-sun:05:00"

  validation {
    condition = can(regex("^(mon|tue|wed|thu|fri|sat|sun):[0-9]{2}:[0-9]{2}-(mon|tue|wed|thu|fri|sat|sun):[0-9]{2}:[0-9]{2}$", var.db_maintenance_window))
    error_message = "Maintenance window must be in format ddd:HH:MM-ddd:HH:MM."
  }
}

# EKS Configuration
variable "eks_cluster_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.28"

  validation {
    condition     = can(regex("^1\\.[2-9][0-9]$", var.eks_cluster_version))
    error_message = "EKS cluster version must be a valid Kubernetes version (e.g., 1.28)."
  }
}

variable "eks_node_groups" {
  description = "EKS node groups configuration"
  type = map(object({
    instance_types = list(string)
    scaling_config = object({
      desired_size = number
      max_size     = number
      min_size     = number
    })
    disk_size    = number
    capacity_type = string
  }))
  default = {
    general = {
      instance_types = ["t3.medium"]
      scaling_config = {
        desired_size = 2
        max_size     = 10
        min_size     = 1
      }
      disk_size     = 20
      capacity_type = "ON_DEMAND"
    }
  }
}

# Redis Configuration
variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.micro"

  validation {
    condition     = can(regex("^cache\\.[a-z0-9]+\\.[a-z0-9]+$", var.redis_node_type))
    error_message = "Redis node type must be a valid ElastiCache node type."
  }
}

variable "redis_num_cache_nodes" {
  description = "Number of cache nodes for Redis"
  type        = number
  default     = 1

  validation {
    condition     = var.redis_num_cache_nodes >= 1 && var.redis_num_cache_nodes <= 20
    error_message = "Number of cache nodes must be between 1 and 20."
  }
}

variable "redis_parameter_group_name" {
  description = "Parameter group name for Redis"
  type        = string
  default     = "default.redis7"
}

# Domain and SSL Configuration
variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "example.com"

  validation {
    condition     = can(regex("^[a-z0-9.-]+\\.[a-z]{2,}$", var.domain_name))
    error_message = "Domain name must be a valid domain format."
  }
}

variable "create_route53_zone" {
  description = "Whether to create Route53 hosted zone"
  type        = bool
  default     = false
}

variable "enable_cloudfront" {
  description = "Whether to enable CloudFront distribution"
  type        = bool
  default     = false
}

variable "cloudfront_price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_100"

  validation {
    condition = contains([
      "PriceClass_All",
      "PriceClass_200",
      "PriceClass_100"
    ], var.cloudfront_price_class)
    error_message = "CloudFront price class must be one of: PriceClass_All, PriceClass_200, PriceClass_100."
  }
}

variable "enable_waf" {
  description = "Whether to enable AWS WAF"
  type        = bool
  default     = false
}

# Monitoring and Logging Configuration
variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 14

  validation {
    condition = contains([
      1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653
    ], var.log_retention_days)
    error_message = "Log retention days must be a valid CloudWatch retention period."
  }
}

variable "enable_container_insights" {
  description = "Whether to enable CloudWatch Container Insights"
  type        = bool
  default     = true
}

variable "alert_email" {
  description = "Email address for alerts"
  type        = string
  default     = ""

  validation {
    condition     = var.alert_email == "" || can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.alert_email))
    error_message = "Alert email must be a valid email address or empty string."
  }
}

# Backup Configuration
variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 90

  validation {
    condition     = var.backup_retention_days >= 1 && var.backup_retention_days <= 2555
    error_message = "Backup retention days must be between 1 and 2555."
  }
}

variable "enable_backup_encryption" {
  description = "Whether to encrypt backups"
  type        = bool
  default     = true
}

# Security Configuration
variable "enable_encryption_at_rest" {
  description = "Whether to enable encryption at rest"
  type        = bool
  default     = true
}

variable "enable_encryption_in_transit" {
  description = "Whether to enable encryption in transit"
  type        = bool
  default     = true
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the application"
  type        = list(string)
  default     = ["0.0.0.0/0"]

  validation {
    condition = alltrue([
      for cidr in var.allowed_cidr_blocks : can(cidrhost(cidr, 0))
    ])
    error_message = "All CIDR blocks must be valid IPv4 CIDR notation."
  }
}

# Performance Configuration
variable "enable_auto_scaling" {
  description = "Whether to enable auto scaling"
  type        = bool
  default     = true
}

variable "cpu_utilization_threshold" {
  description = "CPU utilization threshold for auto scaling"
  type        = number
  default     = 70

  validation {
    condition     = var.cpu_utilization_threshold >= 10 && var.cpu_utilization_threshold <= 90
    error_message = "CPU utilization threshold must be between 10 and 90."
  }
}

variable "memory_utilization_threshold" {
  description = "Memory utilization threshold for auto scaling"
  type        = number
  default     = 80

  validation {
    condition     = var.memory_utilization_threshold >= 10 && var.memory_utilization_threshold <= 90
    error_message = "Memory utilization threshold must be between 10 and 90."
  }
}

# Application Configuration
variable "app_replicas_min" {
  description = "Minimum number of application replicas"
  type        = number
  default     = 2

  validation {
    condition     = var.app_replicas_min >= 1 && var.app_replicas_min <= 100
    error_message = "Minimum replicas must be between 1 and 100."
  }
}

variable "app_replicas_max" {
  description = "Maximum number of application replicas"
  type        = number
  default     = 10

  validation {
    condition     = var.app_replicas_max >= 1 && var.app_replicas_max <= 100
    error_message = "Maximum replicas must be between 1 and 100."
  }
}

variable "app_replicas_desired" {
  description = "Desired number of application replicas"
  type        = number
  default     = 3

  validation {
    condition     = var.app_replicas_desired >= 1 && var.app_replicas_desired <= 100
    error_message = "Desired replicas must be between 1 and 100."
  }
}

# Development Configuration
variable "enable_debug_mode" {
  description = "Whether to enable debug mode"
  type        = bool
  default     = false
}

variable "skip_final_snapshot" {
  description = "Whether to skip final snapshot when deleting DB"
  type        = bool
  default     = false
}

variable "force_destroy_s3_buckets" {
  description = "Whether to force destroy S3 buckets"
  type        = bool
  default     = false
}

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}

  validation {
    condition = alltrue([
      for key, value in var.additional_tags :
      can(regex("^[a-zA-Z0-9+\\-=._:/@]+$", key)) && can(regex("^[a-zA-Z0-9+\\-=._:/@\\s]+$", value))
    ])
    error_message = "Tag keys and values must contain only alphanumeric characters and the characters +, -, =, ., _, :, /, @, and spaces."
  }
}

# Feature Flags
variable "feature_flags" {
  description = "Feature flags for enabling/disabling functionality"
  type = object({
    enable_monitoring        = bool
    enable_logging          = bool
    enable_tracing          = bool
    enable_backup          = bool
    enable_disaster_recovery = bool
    enable_multi_az         = bool
    enable_read_replica     = bool
  })
  default = {
    enable_monitoring        = true
    enable_logging          = true
    enable_tracing          = false
    enable_backup          = true
    enable_disaster_recovery = false
    enable_multi_az         = false
    enable_read_replica     = false
  }
}

# Environment-specific overrides
variable "environment_config" {
  description = "Environment-specific configuration overrides"
  type = map(object({
    instance_type = string
    min_capacity  = number
    max_capacity  = number
    storage_size  = number
  }))
  default = {
    development = {
      instance_type = "db.t3.micro"
      min_capacity  = 1
      max_capacity  = 2
      storage_size  = 20
    }
    staging = {
      instance_type = "db.t3.small"
      min_capacity  = 1
      max_capacity  = 3
      storage_size  = 50
    }
    production = {
      instance_type = "db.r5.large"
      min_capacity  = 2
      max_capacity  = 10
      storage_size  = 100
    }
  }
}