PYTHON = python3
PIP = pip3

.PHONY: all install run debug clean lint lint-strict

all: run

install:
	$(PYTHON) -m pip install flake8 mypy

run:
	PYTHONPATH=. $(PYTHON) src/main.py maps/hard/03_ultimate_challenge.txt

debug:
	PYTHONPATH=. $(PYTHON) -m pdb src/main.py maps/hard/03_ultimate_challenge.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	flake8 . --max-line-length=120
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 . --max-line-length=120
	mypy . --strict
