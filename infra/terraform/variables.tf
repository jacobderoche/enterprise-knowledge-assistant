variable "project" {
  description = "Project name prefix"
  type        = string
  default     = "knowledge-assistant"
}

variable "environment" {
  description = "Deployment environment (dev/staging/prod)"
  type        = string
  default     = "dev"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "db_username" {
  description = "Master username for RDS PostgreSQL"
  type        = string
  default     = "app"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "vpc_subnet_ids" {
  description = "Subnet IDs used by RDS and ECS"
  type        = list(string)
  default     = []
}

variable "vpc_security_group_ids" {
  description = "Security groups for RDS and ECS"
  type        = list(string)
  default     = []
}
