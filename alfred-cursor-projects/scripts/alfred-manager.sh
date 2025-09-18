#!/bin/bash

# Alfred Automation Script for Cursor Project Management
# This script provides a simple interface for Alfred to interact with projects

set -e

BASE_DIR="$(dirname "$0")/.."
PROJECTS_DIR="$BASE_DIR/projects"
CONFIG_FILE="$BASE_DIR/config/alfred-config.json"

# Function to list available templates
list_templates() {
  echo "Available project templates:"
  for template in "$BASE_DIR/templates"/*; do
    if [ -d "$template" ]; then
      echo "- $(basename "$template")"
    fi
  done
}

# Function to list existing projects
list_projects() {
  echo "Existing projects:"
  for project in "$PROJECTS_DIR"/*; do
    if [ -d "$project" ] && [ "$(basename "$project")" != "README.md" ]; then
      echo "- $(basename "$project")"
    fi
  done
}

# Function to create a new project
create_project() {
  local project_name="$1"
  local template_type="$2"
  
  if [ -z "$project_name" ]; then
    echo "Error: Project name is required"
    return 1
  fi
  
  if [ -z "$template_type" ]; then
    template_type="react-typescript"
  fi
  
  # Generate unique project name with timestamp
  local timestamp=$(date +"%Y0%m%d%H%M%S")
  local full_project_name="$template_type-$project_name-$timestamp"
  
  echo "Creating project: $full_project_name"
  
  # Call the create-project.sh script
  "$BASE_DIR/scripts/create-project.sh" "$full_project_name" "$template_type"
}

# Function to open a project in Cursor
open_in_cursor() {
  local project_name="$1"
  local project_path="$PROJECTS_DIR/$project_name"
  
  if [ ! -d "$project_path" ]; then
    echo "Error: Project '$project_name' not found"
    return 1
  fi
  
  if command -v cursor &> /dev/null; then
    echo "Opening $project_name in Cursor..."
    cursor "$project_path"
  else
    echo "Cursor not found in PATH. Please open $project_path manually"
  fi
}

# Main script logic
case "$1" in
  "list-templates")
    list_templates
    ;;
  "list-projects")
    list_projects
    ;;
  "create")
    create_project "$2" "$3"
    ;;
  "open")
    open_in_cursor "$2"
    ;;
  *)
    echo "Alfred Cursor Project Management"
    echo "Usage:"
    echo "  $0 list-templates                         # List available templates"
    echo "  $0 list-projects                           # List existing projects"
    echo "  $0 create <project-name> [template-type]   # Create a new project"
    echo "  $0 open <project-name>                    # Open project in Cursor"
    exit 1
    ;;
esac
