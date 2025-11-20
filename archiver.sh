#!/bin/bash
# AcademicArchiver Linux/Mac Wrapper Script
# This script runs AcademicArchiver from source using a virtual environment
# Usage: ./archiver.sh --query="your query" --scholar-pages=1 --dwn-dir="./output" [other arguments]

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
else
    PYTHON_CMD=python
fi

# Check if venv exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate venv
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import requests; import pandas" &> /dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        deactivate
        exit 1
    fi
fi

# Run AcademicArchiver from source
export PYTHONPATH="$SCRIPT_DIR/src"
python -m core.cli "$@"

# Store exit code before deactivating
EXIT_CODE=$?

# Deactivate venv
deactivate

# Exit with the same code as AcademicArchiver
exit $EXIT_CODE
