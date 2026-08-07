PYTHON = python3
PIP = pip3

.PHONY: all install run debug clean lint lint-strict

all: run

install:
	$(PIP) install flake8 mypy

run:
	$(PYTHON) src/main.py maps/hard/03_ultimate_challenge.txt

debug:
	$(PYTHON) -m pdb src/main.py maps/hard/03_ultimate_challenge.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	flake8 src/
	mypy src/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 src/
	mypy src/ --strict
