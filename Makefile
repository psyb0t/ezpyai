.PHONY: dep build clean help

dep: ## Install dependencies
	python -m pip install build

build: ## Build the project
	python -m build

clean: ## Clean the build artifacts
	rm -rf ./dist

tag: ## Tag a new release
	@echo "Enter new version tag (e.g., v0.1.0): "; \
	read TAG; \
	git tag -a $$TAG -m "Release $$TAG"; \
	sed -i "s/version = \".*\"/version = \"$$TAG\"/" pyproject.toml; \
	git add pyproject.toml; \
	git commit -m "Update version to $$TAG"; \
	git push; \
	git push --tags

help: ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
