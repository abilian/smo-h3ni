.PHONY: test


test:
	@echo "⏳ Starting Postgres with Docker Compose..."
	COMPOSE_PROJECT_NAME=smo-tests docker compose -f docker-compose.test.yml up -d --wait
	@echo "✅ Running pytest on $(TEST_PATH)..."
	pytest tests
	@echo "🧹 Tearing down Docker Compose..."
	COMPOSE_PROJECT_NAME=smo-tests docker compose -f docker-compose.test.yml down
