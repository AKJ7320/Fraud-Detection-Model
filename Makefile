.PHONY: lint format-check typecheck test coverage gate

lint:
	ruff check src tests scripts

format-check:
	black --check src tests scripts

typecheck:
	mypy src tests scripts

test:
	pytest

coverage:
	pytest --cov=src --cov-report=term-missing

gate: lint format-check typecheck test coverage

.PHONY: reports
reports:
	python scripts/generate_visual_reports.py
