.PHONY: install-dev lint typecheck test check clean

# Python usado para crear el entorno (3.14): `make PYTHON=python3.14`.
PYTHON ?= python3

# Se llama "venv" porque [tool.pyright] busca el entorno ahí.
VENV = venv
VENV_READY = $(VENV)/.installed

# Se crea en el primer comando y se reinstala cuando cambian las
# dependencias.
$(VENV_READY): pyproject.toml
	test -x $(VENV)/bin/python || $(PYTHON) -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install -e .
	$(VENV)/bin/python -m pip install --group dev
	touch $(VENV_READY)

install-dev: $(VENV_READY)

lint: $(VENV_READY)
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .

typecheck: $(VENV_READY)
	$(VENV)/bin/mypy
	$(VENV)/bin/pyright

test: $(VENV_READY)
	$(VENV)/bin/pytest

check: lint typecheck test

clean:
	rm -rf .ruff_cache .mypy_cache .pytest_cache build dist src/*.egg-info
	find . -type d -name __pycache__ -not -path './$(VENV)/*' -exec rm -rf {} +
