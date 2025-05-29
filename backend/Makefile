# ==== 🐴 Donkey Assistant Makefile ====
.PHONY: install format setup run kill flush-redis reset-db flush-db migrate prompt dev celery redis-start django bootstrap_memory init-db reset_logs codex codex-dry help seed-all run-all-scripts reset-seed

# ==== 📦 Setup & Environment ====
install:
	@echo "📦 Installing from requirements.txt..."
	@source .venv/bin/activate && pip install -r requirements.txt

format:
	@echo "🧽 Formatting code with black..."
	@black .

setup:
	@echo "📂 Ensuring folders exist..."
	@mkdir -p data context prompts
	@touch data/prompt_logs.db
	@touch context/daily_notes.json

init-db:
	@echo "🗃️  Initializing prompt_logs.db..."
	@python scripts/init_db.py

bootstrap_memory:
	@echo "🧠 Bootstrapping assistant memory..."
	@python memory/bootstrap.py

reset_logs:
	@echo "🧼 Resetting logs and memory..."
	@rm -f prompt_logs.db
	@make bootstrap_memory

# ==== 🧠 Prompt Assistant ====
prompt:
	@echo "🧠 Starting prompt menu interface..."
	@source .venv/bin/activate && python command_menu.py

donkey_dev:
	@echo "🐴 Booting up Donkey Dev Assistant..."
	@source .venv/bin/activate && python command_menu.py

donkey_nolog:
	@echo "🚫 Running Assistant (no logs)..."
	@USE_LOGGING=False source .venv/bin/activate && python ollama_dev_assistant.py

ingest:
	@echo "📥 Ingesting prompt_sets/..."
	@python manage.py ingest_prompts

# ==== 🚀 Django + Redis + Celery ====
run:
	@make redis-start
	@sleep 1
	@make django &
	@sleep 2
	@make celery &
	@echo "⏳ Waiting for Django to start..."

redis-start:
	@echo "🟥 Starting Redis..."
	@pgrep redis-server || redis-server

flush-redis:
	@echo "💣 Flushing Redis..."
	@redis-cli FLUSHALL

kill:
	@echo "💀 Killing dev processes..."
	-@pkill -f 'manage.py runserver' || true
	-@pkill -f 'celery' || true
	-@pkill -f 'redis-server' || true
	-@pkill -f 'vite' || true
	-@pkill -f 'flutter' || true

restart:
	@make kill
	@sleep 1
	@make run

django:
	@echo "🌄 Running Django..."
	@python manage.py runserver

celery:
	@echo "🌪️ Starting Celery..."
	@celery -A server worker --loglevel=info --pool=solo

# ==== 🧪 Dev Utilities ====

# makemigrations:
# <TAB>@python manage.py makemigrations

# migrate: makemigrations
#        @python manage.py migrate

reset-db:
	@echo "💣 Dropping and recreating DB..."
	dropdb donkey_ai_assistant || true
	createdb donkey_ai_assistant
	find . -path "./.venv" -prune -o -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find . -path "./.venv" -prune -o -path "*/migrations/*.pyc" -delete
	python manage.py makemigrations
	python manage.py migrate

flush-db:
	@echo "🧹 Flushing database..."
	@python manage.py flush --no-input
	@python manage.py migrate

reset-seed:
	@echo "🔄 Resetting DB and reseeding..."
	@make flush-db && make seed-all

# ==== 🤖 Codex ====
codex:
	@echo "⚡ Running Codex Helpers"
    @PYTHONPATH=$(PWD) python backend/tools/run_codex_tasks.py

codex-dry:
	@echo "🧃 [DRY RUN] Codex Helpers"
    @CODEX_DRY_RUN=1 PYTHONPATH=$(PWD) python backend/tools/run_codex_tasks.py

# ==== 🌱 Seeder Shortcut ====
seed-all:
	@echo "🌱 Running all seed scripts..."

	@python manage.py seed_assistants && echo "✅ Seeded Assistants"
	@python manage.py seed_symbolic_anchors && echo "✅ Seeded Glossary Terms"
	@python manage.py seed_dev_docs && echo "✅ Seeded Dev Docs"
	@python manage.py seed_memory_entries && echo "✅ Seeded Memory Entries"
	@python manage.py seed_convergence_logs && echo "✅ Seeded Convergence Logs"


post-seed-dashboard:
	@python manage.py check_post_seed_status

run-all-scripts:
	@echo "🚀 Running all management commands and dev scripts..."
	@bash seed_all.sh
	@bash run_all_seeders.sh
	@bash run_all_devdoc_scripts.sh

safe-restart:
	@echo "🧼 Graceful restart (kill + run + flush)..."
	@echo "💀 Killing dev processes..."
	pkill -f runserver || true
	pkill -f celery || true
	pkill -f redis-server || true
	sleep 1
	@make run &
	sleep 5


	
# ==== 🧙 Help ====
help:
	@echo "\n🧙‍♂️ Donkey Assistant Commands:"
	@echo "  make install           📦 Install dependencies"
	@echo "  make prompt            🧠 Run prompt menu"
	@echo "  make ingest            📥 Ingest prompt_sets markdown"
	@echo "  make run               🔄 Start Redis + Django + Celery"
	@echo "  make restart           🔄 Kill + restart everything"
	@echo "  make format            🧽 Run black formatter"
	@echo "  make reset-db          💣 Drop + re-init DB"
	@echo "  make flush-db          ♻️  Flush + migrate DB"
	@echo "  make flush-redis       🧨 Clear Redis tasks"
	@echo "  make codex             ⚡ Run Codex script"
	@echo "  make bootstrap_memory  🧠 Load core memory"
	@echo "  make seed-all          🌱 Run all seeders"
	@echo "  make reset-seed        🔄 Flush DB + reseed"
	@echo "  make run-all-scripts   🚀 Run all command and dev_script files"
	@echo ""
