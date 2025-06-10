# CI/CD Pipeline

Two GitHub Actions workflows automate testing and deployment.

- `ci.yml` runs linting, migrations, and tests for backend and frontend.
- `deploy.yml` builds Docker images, pushes them to the registry, and deploys the
  staging stack.

Workflows live under `.github/workflows/`.
