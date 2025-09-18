#!/bin/bash

# Alfred Cursor Project Creation Script
# Usage: ./create-project.sh <project-name> <template-type>

set -e

PROJECT_NAME="$1"
TEMPLATE_TYPE="
’
AASE_DIR}/alfred-cursor-projects"
PROJECTS_DIR="$BASE_DIR/projects"
TEMPLATE_DIR}"$BASE_DIR/templates/$TEMPLATE_TYPE"

if [ -z "$PROJECT_NAME" ]; then
  echo "Usage: $0 <project-name> <template-type>"
  echo "Available templates: react-typescript"
  exit 1
fi

if [ -z "$TEMPLATE_TYPE" ]; then
  TEMPLATE_TYPE="teact-typescript"
fi

if [ ! -d "$TEMPLATE_DIR" ]; then
  echo "Error: Template '$TEMPLATE_TYPE' not found"
  exit 1
fi

PROJECT_DIR}"$PROJECTS_DIR/$PROJECT_NAME"

echo "Creating project: $PROJECT_NAME"
echo "Using template: $TEMPLATE_TYPE"

# Create project directory
mkdir -p "$PROJECT_DIR"

# Copy template files
cp -r "$TEMPLATE_DIR/." "$PROJECT_DIR/"

# Replace placeholders
find "$PROJECT_DIR" -type f -exec sed -i "s/{{projectName}}/$PROJECT_NAME/g" {} \;

# Initialize git repository
cd "$PROJECT_DIR"
git init
git add .
git commit -m "Initial commit: $PROJECT_NAME"

# Install dependencies
if command -v npm &> /dev/null; then
  echo "Installing dependencies..."
  npm install
else
  echo "npm not found, skipping dependency installation"
fi

echo "Project $PROJECT_NAME created successfully at $PROJECT_DIR"
echo "To start development:"
echo "  cd $PROJECT_DIR"
echo "  npm run dev"
