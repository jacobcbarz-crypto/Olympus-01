#!/bin/bash

# Alfred Cursor Project Creation Script
# Usage: ./create-project.sh <project-name> <template-type>

set -e

PROJECT_NAME="$1"
TEMPLATE_TYPE="$2"
BASE_DIR="./alfred-cursor-projects"
PROJECTS_DIR="$BASE_DIR/projects"
TEMPLATE_DIR="$BASE_DIR/templates/$TEMPLATE_TYPE"

# Available templates
AVAILABLE_TEMPLATES=("react-typescript" "nextjs-typescript" "python-fastapi")

if [ -z "$PROJECT_NAME" ]; then
  echo "Usage: $0 <project-name> <template-type>"
  echo "Available templates:"
  for template in "${AVAILABLE_TEMPLATES[@]}"; do
    echo "  - $template"
  done
  exit 1
fi

if [ -z "$TEMPLATE_TYPE" ]; then
  TEMPLATE_TYPE="teact-typescript"
fi

# Validate template exists
if [ ! -d "$TEMPLATE_DIR" ]; then
  echo "Error: Template '$TEMPLATE_TYPE' not found"
  echo "Available templates:"
  for template in "${AVAILABLE_TEMPLATES[@]}"; do
    echo "  - $template"
  done
  exit 1
fi

PROJECT_DIR="$PROJECTS_DIR/$PROJECT_NAME"

echo "Creating project: $PROJECT_NAME"
echo "Using template: $TEMPLATE_TYPE"

# Create project directory
mkdir -p "$PROJECT_DIR"

# Copy template files
cp -r "$TEMPLATE_DIR/"* "$PROJECT_DIR/"

# Replace placeholders
find "$PROJECT_DIR" -type f -exec sed -i "s/{{projectName}}/$PROJECT_NAME/g" {} \;

# Initialize git repository
cd "$PROJECT_DIR"
git init
git add .
git commit -m "Initial commit: $PROJECT_NAME"

# Install dependencies based on template type
case $TEMPLATE_TYPE in
  "react-typescript"|"nextjs-typescript")
    if command -v npm &> /dev/null; then
      echo "Installing Node.js dependencies..."
      npm install
    else
      echo "npm not found, skipping dependency installation"
    fi
    ;;
  "python-fastapi")
    if command -v python3 &> /dev/null; then
      echo "Creating Python virtual environment..."
      python3 -m venv venv
      source venv/bin/activate
      echo "Installing Python dependencies..."
      pip install -r requirements.txt
    else
      echo "python3 not found, skipping dependency installation"
    fi
    ;;
esac

echo "Project $PROJECT_NAME created successfully at $PROJECT_DIR"
echo "To start development:"
echo "  cd $PROJECT_DIR"

case $TEMPLATE_TYPE in
  "react-typescript"|"nextjs-typescript")
    echo "  npm run dev"
    ;;
  "python-fastapi")
    echo "  source venv/bin/activate"
    echo "  uvicorn main:app --reload"
    ;;
esac
