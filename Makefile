.PHONY: install lint format typecheck test run docker

install:
	pip install -e ".[dev]"

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy app

test:
	pytest

run:
	uvicorn app.main:app --reload

docker:
	docker compose up --build
