# Donkey AI Assistant

## Overview

This repository contains the backend and frontend for the Donkey AI Assistant system.

### Backend (`backend/`)
- Django project with Celery workers and Redis integration.
- Management commands, seeds and utilities are under this directory.

### Frontend (`frontend/`)
- React application bootstrapped with Vite.
- Contains routes, components and supporting documentation.

## Quick Start

### Backend (Django)
1. Create and activate a Python virtual environment.
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Apply database migrations:
   ```bash
   cd backend
   python manage.py migrate
   ```
4. Start the development stack (Redis, Django and Celery):
   ```bash
   make run
   ```

### Frontend (React)
1. Install node modules:
   ```bash
   cd frontend
   npm install
   ```
2. Start the development server:
   ```bash
   npm run dev
   ```

## Documentation
- [Project notes in `AGENTS.md`](AGENTS.md)
- Additional backend docs are available under [`backend/docs`](backend/docs/)
- Frontend specific docs live in [`frontend/docs`](frontend/docs/)

## Contributing
1. Fork and clone the repository.
2. Create a new branch for your feature or fix.
3. Commit changes with clear messages and open a pull request.
4. Run backend tests with `pytest` before submitting.

