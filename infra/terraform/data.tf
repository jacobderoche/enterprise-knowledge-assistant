# --- Secrets Manager: DB password + provider API keys ---------------------
resource "random_password" "db" {
  length  = 24
  special = false
}

resource "aws_secretsmanager_secret" "db" {
  name = "${local.name}/db-password"
  tags = local.tags
}

resource "aws_secretsmanager_secret_version" "db" {
  secret_id     = aws_secretsmanager_secret.db.id
  secret_string = random_password.db.result
}

resource "aws_secretsmanager_secret" "model_api_keys" {
  name = "${local.name}/model-api-keys"
  tags = local.tags
}

# --- RDS PostgreSQL (pgvector-capable engine version) ---------------------
resource "aws_db_subnet_group" "this" {
  count      = length(var.vpc_subnet_ids) > 0 ? 1 : 0
  name       = "${local.name}-db"
  subnet_ids = var.vpc_subnet_ids
  tags       = local.tags
}

resource "aws_db_instance" "postgres" {
  identifier             = "${local.name}-pg"
  engine                 = "postgres"
  engine_version         = "16.4"
  instance_class         = var.db_instance_class
  allocated_storage      = 20
  storage_encrypted      = true
  db_name                = "knowledge"
  username               = var.db_username
  password               = random_password.db.result
  db_subnet_group_name   = length(var.vpc_subnet_ids) > 0 ? aws_db_subnet_group.this[0].name : null
  vpc_security_group_ids = var.vpc_security_group_ids
  skip_final_snapshot    = true
  deletion_protection    = false
  tags                   = local.tags
}

# The pgvector extension is enabled by the application on first connect:
#   CREATE EXTENSION IF NOT EXISTS vector;

# --- S3: raw document storage ---------------------------------------------
resource "aws_s3_bucket" "documents" {
  bucket = "${local.name}-documents"
  tags   = local.tags
}

resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "documents" {
  bucket                  = aws_s3_bucket.documents.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
