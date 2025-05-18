# Donkey Workspace

This repository contains the backend and frontend code for the Donkey AI assistant network.

## Running Tests

Two types of tests exist in this project:

1. **Django unit tests** located within each app under `backend/`. These can be executed with Django's test runner:

```bash
python backend/manage.py test
```

2. **Integration tests** in the top-level `tests/` folder. Run these (and any pytest style tests) with:

```bash
pytest
```

The `tests/assistants` directory links to existing assistant tests so they can be run as part of the integration suite.
