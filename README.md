# Donkey Workspace

This repository holds the backend (Django) and frontend (React/Vite) for the Donkey assistant system.

## Continuous Integration

| Workflow | Status |
| --- | --- |
| Backend | ![Backend](https://github.com/OWNER/REPO/actions/workflows/backend.yml/badge.svg) |
| Frontend | ![Frontend](https://github.com/OWNER/REPO/actions/workflows/frontend.yml/badge.svg) |
| Docker | ![Docker](https://github.com/OWNER/REPO/actions/workflows/docker.yml/badge.svg) |

The **backend** workflow installs Python dependencies, runs `flake8`, `black --check` and executes the test suite with `pytest`.

The **frontend** workflow installs Node packages and runs `npm run lint` to check the React code.

The optional **Docker** workflow builds the repository's `Dockerfile` and pushes the image to GitHub Container Registry on pushes to `main`.

Update the `OWNER/REPO` portion of the badge URLs to match your GitHub repository name.
