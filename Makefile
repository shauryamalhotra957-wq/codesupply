.PHONY: help setup backend worker frontend dev test lint clean docker

help:
	@echo "CodeSupply - Software Supply-Chain Intelligence Platform"
	@echo ""
	@echo "Commands:"
	@echo "  make setup      - Install all dependencies"
	@echo "  make backend    - Start backend API server"
	@echo "  make worker     - Start scan worker"
	@echo "  make frontend   - Start frontend dev server"
	@echo "  make dev        - Start all services"
	@echo "  make test       - Run all tests"
	@echo "  make lint       - Run linters"
	@echo "  make clean      - Clean temporary files"
	@echo "  make docker     - Start with Docker Compose"

setup:
	cd backend && pip install -e ".[dev]"
	cd frontend && npm install

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

worker:
	cd backend && python -m app.workers.runner

frontend:
	cd frontend && npm run dev

test:
	cd backend && pytest -v
	cd frontend && npm test

lint:
	cd backend && ruff check . && ruff format --check .
	cd frontend && npm run lint && npm run typecheck

clean:
	rm -rf backend/tmp/
	rm -rf backend/*.db
	rm -rf frontend/.next/

docker:
	docker-compose up --build
