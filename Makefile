REBUILD_FLAG =

.PHONY: help all clean clean-pyc clean-build lint test coverage docs

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "test - run tests quickly with the default Python"
	@echo "coverage - check code coverage"

all: test

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

test: .venv.touch
	tox $(REBUILD_FLAG)

docs:
	tox -e docs

coverage: test

.venv.touch: setup.py requirements-dev.txt
	$(eval REBUILD_FLAG := --recreate)
	touch .venv.touch
