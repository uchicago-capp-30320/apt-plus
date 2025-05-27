# ref: https://github.com/fpgmaas/cookiecutter-uv-example/blob/main/Makefile

.PHONY: install
install: ## Install the virtual environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using uv"
	@uv sync
	@uv run pre-commit install


.PHONY: cs
cs: ## Collect static files
	@uv run manage.py collectstatic --noinput

.PHONY: run
run: cs ## Launch the server
	@uv run manage.py runserver

.PHONY: format
format: ## Format the code with ruff
	@uvx ruff format

.PHONY: act
act: ## Run Github Actions workflow locally
	@act --secret-file .env

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv lock --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@uv run pytest --cov --cov-config=pyproject.toml # --cov-report=xml


.PHONY: help
help:
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.DEFAULT_GOAL := help
