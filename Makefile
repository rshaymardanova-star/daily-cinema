.PHONY: dev dev-full up down build test test-fast test-full lint format pre-commit clean logs status validate-styles

dev:
	@echo "Starting Daily Cinema in dev mode (ACU_MODE=light, hot reload)..."
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

dev-full:
	@echo "Starting Daily Cinema in full mode (ACU_MODE=full, hot reload)..."
	ACU_MODE=full docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

up:
	docker compose up -d --build

down:
	docker compose down

build:
	docker compose build

test: test-fast

test-fast:
	@echo "Running fast tests (ACU_MODE=light)..."
	ACU_MODE=light python3 -m pytest tests/test_unit_light.py -v

test-full:
	@echo "Running full E2E tests (ACU_MODE=full)..."
	ACU_MODE=full python3 -m pytest tests/ -v --ignore=tests/test_load.py

test-e2e:
	@echo "Running E2E visual style tests..."
	python3 -m pytest tests/test_visual_styles_e2e.py -v

lint:
	@echo "Running linters..."
	python3 -m black --check backend/ ml_module/ unity_worker/ tests/
	python3 -m isort --check-only backend/ ml_module/ unity_worker/ tests/
	python3 -m flake8 backend/ ml_module/ unity_worker/ tests/ --max-line-length=150 --ignore=E501,W503

format:
	@echo "Formatting code..."
	python3 -m black backend/ ml_module/ unity_worker/ tests/
	python3 -m isort backend/ ml_module/ unity_worker/ tests/

validate-styles:
	@echo "Validating all visual styles..."
	@for style in ethereal_default cosmic_cinematic luminous_dreamscape spectral_mythology neon_ritual; do \
		echo "Validating $$style..."; \
		curl -s -H "X-API-Key: dc-prod-api-key-change-me" -X POST http://localhost:8000/styles/validate \
			-H "Content-Type: application/json" -d "{\"visual_style\": \"$$style\"}" | python3 -m json.tool; \
	done

logs:
	docker compose logs -f

status:
	@echo "=== Service Health ==="
	@curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "Backend: DOWN"
	@curl -s http://localhost:8001/health | python3 -m json.tool 2>/dev/null || echo "ML: DOWN"
	@curl -s http://localhost:8002/health | python3 -m json.tool 2>/dev/null || echo "Unity: DOWN"
	@echo "=== ACU Mode ==="
	@curl -s http://localhost:8001/acu_mode | python3 -m json.tool 2>/dev/null || echo "ML ACU: unknown"
	@curl -s http://localhost:8002/acu_mode | python3 -m json.tool 2>/dev/null || echo "Unity ACU: unknown"

clean:
	docker compose down -v
	rm -rf .pytest_cache __pycache__
