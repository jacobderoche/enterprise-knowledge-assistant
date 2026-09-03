# --- ECR repositories for service images -----------------------------------
resource "aws_ecr_repository" "backend" {
  name                 = "${local.name}/backend"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = local.tags
}

resource "aws_ecr_repository" "ai_service" {
  name                 = "${local.name}/ai-service"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = local.tags
}

resource "aws_ecr_repository" "frontend" {
  name                 = "${local.name}/frontend"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = local.tags
}

# --- ECS cluster (Fargate) -------------------------------------------------
# Task definitions / services are intentionally omitted from this skeleton and
# should be added per service (backend, ai-service, frontend) referencing the
# ECR repos above and injecting secrets from Secrets Manager. Alternatively,
# deploy to EKS using the same images.
resource "aws_ecs_cluster" "this" {
  name = local.name
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  tags = local.tags
}
