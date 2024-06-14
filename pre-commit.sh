#!/bin/bash

# Log the start of the script
echo "Running pre-commit script..."

# Determine the latest git tag
latest_tag=$(git describe --tags --abbrev=0)
if [ -z "$latest_tag" ]; then
    echo "No tags found."
    exit 0
fi

echo "Latest git tag is: $latest_tag"

# Log checking the pyproject.toml
echo "Checking for version mismatch in pyproject.toml..."

# Define the location of pyproject.toml
PYPROJECT_TOML="./pyproject.toml"

# Check if the pyproject.toml exists
if [ ! -f "$PYPROJECT_TOML" ]; then
    echo "[ez-pre-commit] Missing pyproject.toml file. Cannot check version."
    exit 1
fi

# Extract the version from pyproject.toml
pyproject_version=$(awk -F' = ' '/^version = / {gsub(/"/, "", $2); print $2}' $PYPROJECT_TOML)

# Log the version found
echo "Version in pyproject.toml is: $pyproject_version"

# Compare versions
if [ "$latest_tag" != "$pyproject_version" ]; then
    echo "[ez-pre-commit] Version mismatch! Tag: $latest_tag does not match pyproject.toml: $pyproject_version"
    exit 1
else
    echo "Versions match. All good!"
fi

exit 0
