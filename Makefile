.PHONY: dep build clean help

dep: ## Install dependencies
	python -m pip install build

build: ## Build the project
	python -m build

clean: ## Clean the build artifacts
	rm -rf ./dist

tag: ## Tag a new release
	@LAST_TAG=$$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0"); \
	echo "Enter new version tag (last tag: $$LAST_TAG): "; \
	read TAG; \
	sed -i "s/version = \".*\"/version = \"$$TAG\"/" pyproject.toml; \
	git add pyproject.toml; \
	git commit -m "Update version to $$TAG"; \
	git tag -a $$TAG -m "Release $$TAG"; \
	git push; \
	git push --tags

help: ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
