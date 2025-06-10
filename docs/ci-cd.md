
# CI/CD

Two GitHub Actions workflows automate testing and deployment.

- **ci.yml** — runs linting, migrations and tests for both backend and frontend
  on every PR.
- **deploy.yml** — builds Docker images, pushes them to GHCR and triggers a
  staging deployment via SSH.

Badges can be found in the project README.

