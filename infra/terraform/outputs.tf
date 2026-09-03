output "rds_endpoint" {
  description = "PostgreSQL connection endpoint"
  value       = aws_db_instance.postgres.address
}

output "documents_bucket" {
  description = "S3 bucket for raw documents"
  value       = aws_s3_bucket.documents.bucket
}

output "db_secret_arn" {
  description = "Secrets Manager ARN holding the DB password"
  value       = aws_secretsmanager_secret.db.arn
}

output "ecr_repositories" {
  description = "ECR repository URLs"
  value = {
    backend    = aws_ecr_repository.backend.repository_url
    ai_service = aws_ecr_repository.ai_service.repository_url
    frontend   = aws_ecr_repository.frontend.repository_url
  }
}

output "ecs_cluster" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.this.name
}
