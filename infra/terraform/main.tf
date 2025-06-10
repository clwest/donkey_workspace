terraform {
  required_version = ">= 1.5"
}

provider "aws" {
  region = var.aws_region
}

module "network" {
  source = "terraform-aws-modules/vpc/aws"
  name   = "mythos-staging"
  cidr   = var.vpc_cidr
}

# ECS Cluster and services would be defined here

