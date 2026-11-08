PYTHON = python3
PIP = $(PYTHON) -m pip
MAP ?= test_map.txt

.PHONY: install run debug lint clean

install:
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) main.py $(MAP)

debug:
	$(PYTHON) -m pdb main.py $(MAP)

lint:
	flake8 .
	mypy .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
