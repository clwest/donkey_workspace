# MythOS Maintenance Runbook

This guide explains how to monitor the daily health checks, manage dependency updates, and run synthetic tests.

## Viewing Health Checks
- Navigate to **Actions > Daily Health Check** on GitHub.
- Each run outputs response codes and timings for `/health/`, `/metrics/`, `/api/assistants/`, and `/api/token/`.
- Failures post a message to Slack via `SLACK_WEBHOOK_URL`.

## Responding to Alerts
1. Check Slack for the failure summary.
2. Review the failing workflow run for logs and response times.
3. Investigate the backend logs or deployment environment.
4. Re-run the workflow manually once the issue is resolved.

## Dependabot PRs
- Weekly dependency checks create pull requests from **dependabot[bot]**.
- CI must pass before the `Auto Merge Dependabot` workflow merges them.
- Review major updates manually; minor and patch updates merge automatically.

## Running Synthetic Tests
- Cypress tests live under `frontend/cypress/e2e/`.
- To run the smoke suite locally:
  ```bash
  cd frontend
  npm install
  npx cypress run --spec "cypress/e2e/smoke.cy.js"
  ```

## Additional Notes
- Scheduled smoke tests run daily at 02:30 UTC via GitHub Actions.
- Health checks run daily at 02:00 UTC.
- See `docs/ci-cd.md` for pipeline details.
