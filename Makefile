ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
SHELL := /bin/bash

include .devcontainer/.env
export

APP_NAME := yagsvc
DOCKER_IMAGE_TAG := $(APP_NAME):dev

.PHONY: help
help: ## This help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: build
build: ## Build app package
	rm -rf dist
	poetry build -f wheel

.PHONY: bootstrap
bootstrap: ## Perform a bootstrap
	# deleting as there may be a conflict when running inside a devcontainer vs local host
	rm -rf .venv && rm -rf .tox
	curl -sSL https://install.python-poetry.org | python3 - --uninstall || true
	curl -sSL https://install.python-poetry.org | python3 -
	# help IDEs to recognize venv's python interpreter
	poetry config virtualenvs.in-project true
	poetry self add "poetry-dynamic-versioning[plugin]"
	# poetry will create .venv as well:
	poetry install --only dev
	# install pre-commit hooks
	source .venv/bin/activate \
		&& pre-commit install \
		&& pre-commit install --hook-type commit-msg
	# install app and all deps
	poetry install

.PHONY: lint
lint: ## Run linters
	tox -e lint

.PHONY: test
test: ## Run unit tests
	tox -e test

.PHONY: clean
clean: ## Remove all generated artifacts (except .venv and .env)
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf .tox
	rm -rf dist

.PHONY: docker-run
docker-run: ## Run dev docker image
	docker run --rm -it \
		--name yag-$(APP_NAME) \
		-p $(LISTEN_PORT):$(LISTEN_PORT)/tcp \
		--env-file $(ROOT_DIR)/.devcontainer/.env \
		--env-file $(ROOT_DIR)/.devcontainer/secret.env \
		$(DOCKER_IMAGE_TAG)

.PHONY: docker-build
docker-build: ## Build docker image
	docker build \
		-t $(DOCKER_IMAGE_TAG) \
		--progress plain \
		.

AWS_ECR_ACCOUNT_ID := 070143334704
AWS_ECR_PROFILE := ecr-rw
AWS_ECR_REGION := us-east-1
AWS_ECR_REPO := im.acme.yag

.PHONY: docker-pub
docker-pub: ## Create a release tag and publish docker image
ifdef TAG
	git fetch \
	&& git checkout main \
	&& git tag -am "Release v$(TAG)" v$(TAG) \
	&& git push origin v$(TAG) \
	&& $(MAKE) docker-build \
	&& docker tag $(DOCKER_IMAGE_TAG) $(AWS_ECR_ACCOUNT_ID).dkr.ecr.$(AWS_ECR_REGION).amazonaws.com/$(AWS_ECR_REPO).$(APP_NAME):$(TAG) \
	&& AWS_PROFILE=$(AWS_ECR_PROFILE) docker push $(AWS_ECR_ACCOUNT_ID).dkr.ecr.$(AWS_ECR_REGION).amazonaws.com/$(AWS_ECR_REPO).$(APP_NAME):$(TAG)
else
	@echo 1>&2 "usage: make docker-pub TAG=1.0.0"
endif
