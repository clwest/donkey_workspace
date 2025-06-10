variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "db_name" {
  type = string
}

variable "db_user" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "sentry_dsn" {
  type = string
}
