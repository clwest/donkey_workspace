variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
}

variable "db_password" {
  description = "Database password"
  type        = string
}

variable "sentry_dsn" {
  description = "Sentry DSN"
  type        = string
}
