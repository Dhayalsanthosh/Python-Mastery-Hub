# File: deployment/terraform/outputs.tf
# Terraform outputs definition

# Network Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnets" {
  description = "List of IDs of private subnets"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of IDs of public subnets"
  value       = module.vpc.public_subnets
}

output "database_subnets" {
  description = "List of IDs of database subnets"
  value       = module.vpc.database_subnets
}

output "database_subnet_group" {
  description = "ID of the database subnet group"
  value       = module.vpc.database_subnet_group
}

output "nat_gateway_ids" {
  description = "List of IDs of the NAT Gateways"
  value       = module.vpc.natgw_ids
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = module.vpc.igw_id
}

# EKS Cluster Outputs
output "cluster_id" {
  description = "EKS cluster ID"
  value       = module.web_app.cluster_id
}

output "cluster_arn" {
  description = "EKS cluster ARN"
  value       = module.web_app.cluster_arn
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.web_app.cluster_endpoint
}

output "cluster_version" {
  description = "The Kubernetes version for the EKS cluster"
  value       = module.web_app.cluster_version
}

output "cluster_platform_version" {
  description = "Platform version for the EKS cluster"
  value       = module.web_app.cluster_platform_version
}

output "cluster_status" {
  description = "Status of the EKS cluster"
  value       = module.web_app.cluster_status
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = module.web_app.cluster_security_group_id
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = module.web_app.cluster_certificate_authority_data
  sensitive   = true
}

output "cluster_oidc_issuer_url" {
  description = "The URL on the EKS cluster for the OpenID Connect identity provider"
  value       = module.web_app.cluster_oidc_issuer_url
}

output "oidc_provider_arn" {
  description = "The ARN of the OIDC Provider for EKS"
  value       = module.web_app.oidc_provider_arn
}

# Node Groups Outputs
output "node_groups" {
  description = "EKS node groups"
  value       = module.web_app.node_groups
}

output "node_security_group_id" {
  description = "ID of the EKS node shared security group"
  value       = module.web_app.node_security_group_id
}

# Database Outputs
output "db_instance_id" {
  description = "RDS instance ID"
  value       = module.database.db_instance_id
}

output "db_instance_arn" {
  description = "RDS instance ARN"
  value       = module.database.db_instance_arn
}

output "db_instance_endpoint" {
  description = "RDS instance endpoint"
  value       = module.database.endpoint
  sensitive   = true
}

output "db_instance_port" {
  description = "RDS instance port"
  value       = module.database.port
}

output "db_instance_name" {
  description = "RDS instance name"
  value       = module.database.db_name
}

output "db_instance_username" {
  description = "RDS instance root username"
  value       = module.database.username
  sensitive   = true
}

output "db_instance_address" {
  description = "RDS instance hostname"
  value       = module.database.address
  sensitive   = true
}

output "db_instance_hosted_zone_id" {
  description = "RDS instance hosted zone ID"
  value       = module.database.hosted_zone_id
}

output "db_subnet_group_id" {
  description = "RDS subnet group ID"
  value       = module.database.db_subnet_group_id
}

output "db_parameter_group_id" {
  description = "RDS parameter group ID"
  value       = module.database.db_parameter_group_id
}

# Redis Outputs
output "redis_cluster_id" {
  description = "ElastiCache Redis cluster ID"
  value       = module.monitoring.redis_cluster_id
}

output "redis_cluster_address" {
  description = "ElastiCache Redis cluster address"
  value       = module.monitoring.redis_endpoint
  sensitive   = true
}

output "redis_cluster_port" {
  description = "ElastiCache Redis cluster port"
  value       = module.monitoring.redis_port
}

output "redis_parameter_group_id" {
  description = "ElastiCache Redis parameter group ID"
  value       = module.monitoring.redis_parameter_group_id
}

output "redis_subnet_group_id" {
  description = "ElastiCache Redis subnet group ID"
  value       = module.monitoring.redis_subnet_group_id
}

# Load Balancer Outputs
output "alb_id" {
  description = "Application Load Balancer ID"
  value       = aws_lb.main.id
}

output "alb_arn" {
  description = "Application Load Balancer ARN"
  value       = aws_lb.main.arn
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Application Load Balancer hosted zone ID"
  value       = aws_lb.main.zone_id
}

# CloudFront Outputs
output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.main[0].id : null
}

output "cloudfront_distribution_arn" {
  description = "CloudFront distribution ARN"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.main[0].arn : null
}

output "cloudfront_distribution_domain_name" {
  description = "CloudFront distribution domain name"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.main[0].domain_name : null
}

output "cloudfront_distribution_hosted_zone_id" {
  description = "CloudFront distribution hosted zone ID"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.main[0].hosted_zone_id : null
}

# WAF Outputs
output "waf_web_acl_id" {
  description = "WAF Web ACL ID"
  value       = var.enable_waf ? aws_wafv2_web_acl.main[0].id : null
}

output "waf_web_acl_arn" {
  description = "WAF Web ACL ARN"
  value       = var.enable_waf ? aws_wafv2_web_acl.main[0].arn : null
}

# Route53 Outputs
output "route53_zone_id" {
  description = "Route53 hosted zone ID"
  value       = var.create_route53_zone ? aws_route53_zone.main[0].zone_id : null
}

output "route53_zone_name_servers" {
  description = "Route53 hosted zone name servers"
  value       = var.create_route53_zone ? aws_route53_zone.main[0].name_servers : null
}

# SSL Certificate Outputs
output "acm_certificate_arn" {
  description = "ACM certificate ARN"
  value       = aws_acm_certificate.main.arn
}

output "acm_certificate_domain_name" {
  description = "ACM certificate domain name"
  value       = aws_acm_certificate.main.domain_name
}

output "acm_certificate_status" {
  description = "ACM certificate status"
  value       = aws_acm_certificate.main.status
}

# S3 Outputs
output "s3_bucket_app_storage_id" {
  description = "S3 bucket ID for app storage"
  value       = aws_s3_bucket.app_storage.id
}

output "s3_bucket_app_storage_arn" {
  description = "S3 bucket ARN for app storage"
  value       = aws_s3_bucket.app_storage.arn
}

output "s3_bucket_app_storage_domain_name" {
  description = "S3 bucket domain name for app storage"
  value       = aws_s3_bucket.app_storage.bucket_domain_name
}

output "s3_bucket_backups_id" {
  description = "S3 bucket ID for backups"
  value       = aws_s3_bucket.backups.id
}

output "s3_bucket_backups_arn" {
  description = "S3 bucket ARN for backups"
  value       = aws_s3_bucket.backups.arn
}

output "s3_bucket_backups_domain_name" {
  description = "S3 bucket domain name for backups"
  value       = aws_s3_bucket.backups.bucket_domain_name
}

# IAM Outputs
output "app_role_arn" {
  description = "Application IAM role ARN"
  value       = aws_iam_role.app_role.arn
}

output "app_role_name" {
  description = "Application IAM role name"
  value       = aws_iam_role.app_role.name
}

# KMS Outputs
output "kms_key_id" {
  description = "KMS key ID"
  value       = aws_kms_key.main.key_id
}

output "kms_key_arn" {
  description = "KMS key ARN"
  value       = aws_kms_key.main.arn
}

output "kms_alias_arn" {
  description = "KMS key alias ARN"
  value       = aws_kms_alias.main.arn
}

# Secrets Manager Outputs
output "secrets_manager_secret_id" {
  description = "Secrets Manager secret ID"
  value       = aws_secretsmanager_secret.app_secrets.id
}

output "secrets_manager_secret_arn" {
  description = "Secrets Manager secret ARN"
  value       = aws_secretsmanager_secret.app_secrets.arn
}

# CloudWatch Outputs
output "cloudwatch_log_group_name" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.app_logs.name
}

output "cloudwatch_log_group_arn" {
  description = "CloudWatch log group ARN"
  value       = aws_cloudwatch_log_group.app_logs.arn
}

# SNS Outputs
output "sns_topic_alerts_arn" {
  description = "SNS topic ARN for alerts"
  value       = aws_sns_topic.alerts.arn
}

# Security Group Outputs
output "database_security_group_id" {
  description = "Database security group ID"
  value       = aws_security_group.database.id
}

output "redis_security_group_id" {
  description = "Redis security group ID"
  value       = aws_security_group.redis.id
}

output "alb_security_group_id" {
  description = "ALB security group ID"
  value       = aws_security_group.alb.id
}

# Environment Information
output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "project_name" {
  description = "Project name"
  value       = var.project_name
}

output "aws_region" {
  description = "AWS region"
  value       = var.aws_region
}

output "availability_zones" {
  description = "List of availability zones used"
  value       = local.azs
}

# Connection Information
output "kubectl_config" {
  description = "kubectl config command"
  value       = "aws eks --region ${var.aws_region} update-kubeconfig --name ${module.web_app.cluster_name}"
}

output "database_connection_string" {
  description = "Database connection string template"
  value       = "postgresql://${var.db_username}:<password>@${module.database.endpoint}:${module.database.port}/${var.db_name}"
  sensitive   = true
}

output "redis_connection_string" {
  description = "Redis connection string template"
  value       = "redis://${module.monitoring.redis_endpoint}:${module.monitoring.redis_port}/0"
  sensitive   = true
}

# Summary Information
output "infrastructure_summary" {
  description = "Infrastructure deployment summary"
  value = {
    cluster_name         = module.web_app.cluster_name
    cluster_endpoint     = module.web_app.cluster_endpoint
    database_endpoint    = module.database.endpoint
    redis_endpoint       = module.monitoring.redis_endpoint
    load_balancer_dns    = aws_lb.main.dns_name
    cloudfront_domain    = var.enable_cloudfront ? aws_cloudfront_distribution.main[0].domain_name : "Not enabled"
    s3_buckets = {
      app_storage = aws_s3_bucket.app_storage.bucket
      backups     = aws_s3_bucket.backups.bucket
    }
    monitoring = {
      log_group = aws_cloudwatch_log_group.app_logs.name
      sns_topic = aws_sns_topic.alerts.name
    }
  }
  sensitive = true
}

# Terraform State Information
output "terraform_workspace" {
  description = "Terraform workspace"
  value       = terraform.workspace
}

output "terraform_version" {
  description = "Terraform version used"
  value       = "~> ${substr(terraform.version, 0, 4)}"
}