.PHONY: build build_cython install develop build_dist test lint docs clean

MODULE := shirotsume_tools
PIP_MODULE := shirotsume_tools

all: clean build lint build_dist
refresh: clean develop test lint

build_cython:
	USE_CYTHON=true python setup.py build_ext --inplace

build:
	python setup.py build_ext --inplace

install:
	pip install .

run:
	uv run python -m ${MODULE}

develop:
	uv sync

build_dist:
	uv build

# ruff and pyright are global tools installed via `uv tool install ruff pyright`,
# not project dependencies.
lint:
	ruff check ${MODULE}/ tests/ --fix
	uv run pyright ${MODULE}/

test: build
	uv run pytest

coverage:
	coverage run --source ${MODULE} --parallel-mode -m pytest
	coverage combine
	coverage html -i

uninstall:
	pip uninstall ${PIP_MODULE} -y || true

clean:
	rm -rf build
	rm -rf dist
	rm -rf ${PIP_MODULE}.egg-info
