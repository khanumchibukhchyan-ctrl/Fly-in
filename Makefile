PYTHON = python3
PIP = $(PYTHON) -m pip
MAP ?= test_map.txt
TARGETS = main.py src

.PHONY: install run debug lint lint-strict clean

install:
	$(PIP) install matplotlib flake8 mypy

run:
	$(PYTHON) main.py $(MAP)

debug:
	$(PYTHON) -m pdb main.py $(MAP)

lint:
	flake8 $(TARGETS)
	mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs $(TARGETS)

lint-strict:
	flake8 $(TARGETS)
	mypy --strict --ignore-missing-imports $(TARGETS)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .mypy_cache .pytest_cache
