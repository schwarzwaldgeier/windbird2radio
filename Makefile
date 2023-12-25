default: help

.PHONY: help
## help: this help message
all: help
help: Makefile
	@echo "Usage: \n"
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' |  sed -e 's/^/ /'

.PHONY: install
## install: install required packages
install:
	pip install -r requirements.txt

.PHONY: run
## run: run listener
run:
	python main.py

.PHONY: lint
## lint: run linter
lint:
	pylint **/*.py

.PHONY: test
## test: run pytest
test:
	pytest

.PHONY: test-cov
## test-cov: run pytest with coverage
test-cov:
	pytest --cov
