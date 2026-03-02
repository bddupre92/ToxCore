.PHONY: dev-up dev-down frontend-dev backend-dev test lint db-migrate db-seed

# --- Docker ---
dev-up:
	docker compose up -d
	@echo "Waiting for services to be healthy..."
	@docker compose exec postgres pg_isready -U postgres > /dev/null 2>&1 || sleep 2
	@echo "PostgreSQL and Redis are ready."

dev-down:
	docker compose down

dev-clean:
	docker compose down -v

# --- Frontend ---
frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

frontend-lint:
	cd frontend && npm run lint

frontend-test:
	cd frontend && npm run test

# --- Backend ---
backend-dev:
	cd backend && uvicorn app.main:app --reload --port 8000

backend-lint:
	cd backend && ruff check .

backend-typecheck:
	cd backend && mypy app/

backend-test:
	cd backend && python -m pytest tests/ -v

backend-test-cov:
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=term-missing

# --- Combined ---
test: backend-test frontend-test

lint: backend-lint frontend-lint

# --- Database ---
db-migrate:
	@echo "Run migrations against local Postgres..."
	@for f in supabase/migrations/*.sql; do \
		echo "Applying $$f..."; \
		docker compose exec -T postgres psql -U postgres -d toxscore -f /docker-entrypoint-initdb.d/$$(basename $$f); \
	done

db-seed:
	@echo "Seeding database..."
	@for f in supabase/seed/*.sql; do \
		echo "Running $$f..."; \
		docker compose exec -T postgres psql -U postgres -d toxscore < $$f; \
	done
