.PHONY: all install run debug clean lint lint-strict

all: run

install:
	uv sync

run:
	uv run python3 main.py maps/challenger/01_the_impossible_dream.txt

debug:
	uv run python3 -m pdb main.py maps/hard/03_ultimate_challenge.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	uv run flake8 *.py
	uv run mypy *.py

lint-strict:
	uv run flake8 *.py
	uv run mypy *.py --strict
