# Infrastructure as Code

This folder contains a Terraform stub for the staging environment.

## Usage

```bash
cd infra/terraform
terraform init
terraform plan -var-file=staging.tfvars
```

Define variables like database credentials and Sentry DSN in `staging.tfvars`.
