PYTHON = uv run python3
PIP = uv pip

.PHONY: all install run debug clean lint lint-strict

all: run

install:
	uv venv --allow-existing
	$(PIP) install flake8 mypy rich

run:
	PYTHONPATH=. $(PYTHON) main.py maps/challenger/01_the_impossible_dream.txt

debug:
	PYTHONPATH=. $(PYTHON) -m pdb main.py maps/hard/03_ultimate_challenge.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	uv run flake8 *.py --max-line-length=120
	uv run mypy *.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 *.py --max-line-length=120
	uv run mypy *.py --strict
