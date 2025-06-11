# Demo Script

Follow these steps to run the demo locally.

1. **Clone & install**
   ```bash
   git clone <repo_url>
   cd donkey_workspace
   cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
   cd ../frontend && npm install
   ```
2. **Seed data**
   ```bash
   ./scripts/seed_all.sh
   ```
3. **Start backend & frontend**
   ```bash
   cd backend && source .venv/bin/activate && python manage.py runserver
   # In a new terminal
   cd frontend && npm run dev
   ```
4. **Walk through the flows**
   1. Visit `/assistants/onboarding` and create an assistant
   2. Complete the tour when prompted
   3. Chat with the assistant and click **Reflect now**
   4. Open the demo recap and overlay panels from the dashboard
5. **View performance dashboard**
   ```bash
   ./scripts/benchmark_endpoints.sh
   cat backend/benchmark_results.json
   ```
   Pause here to discuss response times and coverage.
