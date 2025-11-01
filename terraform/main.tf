# ================================================================
# TERRAFORM CONFIGURATION FOR PROMISE AI TEST DATABASES
# Creates PostgreSQL and MySQL RDS instances in AWS (Free Tier)
# ================================================================

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ================================================================
# VARIABLES
# ================================================================

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "db_username" {
  description = "Master username for databases"
  type        = string
  default     = "testuser"
}

variable "db_password" {
  description = "Master password for databases (change this!)"
  type        = string
  sensitive   = true
  default     = "ChangeMe123!" # CHANGE THIS!
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to connect to databases"
  type        = list(string)
  default     = ["0.0.0.0/0"] # WARNING: Open to world - restrict in production!
}

variable "project_name" {
  description = "Project name for tagging"
  type        = string
  default     = "promise-ai-test"
}

# ================================================================
# PROVIDER
# ================================================================

provider "aws" {
  region = var.aws_region
}

# ================================================================
# DATA SOURCES
# ================================================================

data "aws_availability_zones" "available" {
  state = "available"
}

# ================================================================
# VPC AND NETWORKING
# ================================================================

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name    = "${var.project_name}-vpc"
    Project = var.project_name
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name    = "${var.project_name}-igw"
    Project = var.project_name
  }
}

resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name    = "${var.project_name}-public-subnet-1"
    Project = var.project_name
  }
}

resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true

  tags = {
    Name    = "${var.project_name}-public-subnet-2"
    Project = var.project_name
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name    = "${var.project_name}-public-rt"
    Project = var.project_name
  }
}

resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

# ================================================================
# SECURITY GROUPS
# ================================================================

resource "aws_security_group" "postgresql" {
  name        = "${var.project_name}-postgresql-sg"
  description = "Security group for PostgreSQL RDS instance"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "PostgreSQL from anywhere (restrict in production!)"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.project_name}-postgresql-sg"
    Project = var.project_name
  }
}

resource "aws_security_group" "mysql" {
  name        = "${var.project_name}-mysql-sg"
  description = "Security group for MySQL RDS instance"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "MySQL from anywhere (restrict in production!)"
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.project_name}-mysql-sg"
    Project = var.project_name
  }
}

# ================================================================
# DB SUBNET GROUP
# ================================================================

resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = [aws_subnet.public_1.id, aws_subnet.public_2.id]

  tags = {
    Name    = "${var.project_name}-db-subnet-group"
    Project = var.project_name
  }
}

# ================================================================
# RDS POSTGRESQL INSTANCE (FREE TIER)
# ================================================================

resource "aws_db_instance" "postgresql" {
  identifier     = "${var.project_name}-postgresql"
  engine         = "postgres"
  engine_version = "15.4" # Free tier eligible

  # Free Tier Configuration
  instance_class        = "db.t3.micro" # Free tier eligible
  allocated_storage     = 20            # Free tier: 20GB
  max_allocated_storage = 0             # Disable autoscaling for free tier

  # Database Configuration
  db_name  = "testdb"
  username = var.db_username
  password = var.db_password
  port     = 5432

  # Network Configuration
  publicly_accessible    = true # Make it accessible from internet
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.postgresql.id]

  # Backup Configuration (minimal for testing)
  backup_retention_period = 1
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"

  # Performance and Monitoring
  performance_insights_enabled = false # Keep costs low
  enabled_cloudwatch_logs_exports = [
    "postgresql",
    "upgrade"
  ]

  # Other Settings
  skip_final_snapshot       = true # For testing - set false in production
  deletion_protection       = false # For testing - set true in production
  auto_minor_version_upgrade = true
  storage_encrypted          = true

  tags = {
    Name    = "${var.project_name}-postgresql"
    Project = var.project_name
    Type    = "PostgreSQL"
  }
}

# ================================================================
# RDS MYSQL INSTANCE (FREE TIER)
# ================================================================

resource "aws_db_instance" "mysql" {
  identifier     = "${var.project_name}-mysql"
  engine         = "mysql"
  engine_version = "8.0.35" # Free tier eligible

  # Free Tier Configuration
  instance_class        = "db.t3.micro" # Free tier eligible
  allocated_storage     = 20            # Free tier: 20GB
  max_allocated_storage = 0             # Disable autoscaling for free tier

  # Database Configuration
  db_name  = "testdb"
  username = var.db_username
  password = var.db_password
  port     = 3306

  # Network Configuration
  publicly_accessible    = true # Make it accessible from internet
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.mysql.id]

  # Backup Configuration (minimal for testing)
  backup_retention_period = 1
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"

  # Performance and Monitoring
  performance_insights_enabled = false # Keep costs low
  enabled_cloudwatch_logs_exports = [
    "error",
    "general",
    "slowquery"
  ]

  # MySQL Specific
  parameter_group_name = "default.mysql8.0"

  # Other Settings
  skip_final_snapshot       = true # For testing - set false in production
  deletion_protection       = false # For testing - set true in production
  auto_minor_version_upgrade = true
  storage_encrypted          = true

  tags = {
    Name    = "${var.project_name}-mysql"
    Project = var.project_name
    Type    = "MySQL"
  }
}

# ================================================================
# OUTPUTS
# ================================================================

output "postgresql_endpoint" {
  description = "PostgreSQL RDS endpoint"
  value       = aws_db_instance.postgresql.endpoint
}

output "postgresql_address" {
  description = "PostgreSQL RDS address (without port)"
  value       = aws_db_instance.postgresql.address
}

output "postgresql_port" {
  description = "PostgreSQL RDS port"
  value       = aws_db_instance.postgresql.port
}

output "postgresql_connection_string" {
  description = "PostgreSQL connection string for PROMISE AI"
  value       = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.postgresql.endpoint}/testdb"
  sensitive   = true
}

output "mysql_endpoint" {
  description = "MySQL RDS endpoint"
  value       = aws_db_instance.mysql.endpoint
}

output "mysql_address" {
  description = "MySQL RDS address (without port)"
  value       = aws_db_instance.mysql.address
}

output "mysql_port" {
  description = "MySQL RDS port"
  value       = aws_db_instance.mysql.port
}

output "mysql_connection_string" {
  description = "MySQL connection string for PROMISE AI"
  value       = "mysql://${var.db_username}:${var.db_password}@${aws_db_instance.mysql.endpoint}/testdb"
  sensitive   = true
}

output "connection_info" {
  description = "All connection information for PROMISE AI"
  value = {
    postgresql = {
      host     = aws_db_instance.postgresql.address
      port     = aws_db_instance.postgresql.port
      database = aws_db_instance.postgresql.db_name
      username = var.db_username
      password = var.db_password
    }
    mysql = {
      host     = aws_db_instance.mysql.address
      port     = aws_db_instance.mysql.port
      database = aws_db_instance.mysql.db_name
      username = var.db_username
      password = var.db_password
    }
  }
  sensitive = true
}

# ================================================================
# NOTES
# ================================================================

# Free Tier Limits (as of 2025):
# - 750 hours per month of db.t3.micro instance usage
# - 20 GB of General Purpose (SSD) database storage
# - 20 GB of backup storage
# - Both PostgreSQL and MySQL can run within free tier if total < 750 hours
# 
# Cost Estimate (if exceeding free tier):
# - db.t3.micro: ~$0.017/hour = ~$12.50/month
# - Storage: $0.115/GB-month
# - Total for both DBs: ~$25-30/month
#
# To Deploy:
# 1. terraform init
# 2. terraform plan
# 3. terraform apply
#
# To Connect:
# 1. terraform output postgresql_connection_string
# 2. terraform output mysql_connection_string
# 3. Use connection details in PROMISE AI
#
# To Destroy (IMPORTANT - Avoid charges):
# terraform destroy
