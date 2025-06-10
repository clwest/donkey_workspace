# Infrastructure as Code

This folder contains a minimal Terraform configuration for the staging stack.

```bash
cd infra
terraform init
terraform plan -var-file=terraform.tfvars
```

Resources created:
- VPC and ECS cluster
- Postgres RDS instance
- Redis ElastiCache cluster

Fill in values in `terraform.tfvars` before applying.
