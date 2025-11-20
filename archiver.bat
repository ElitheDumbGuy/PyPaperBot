@echo off
REM AcademicArchiver Windows Wrapper Script
REM This script runs AcademicArchiver from source using a virtual environment
REM Usage: archiver.bat --query="your query" --scholar-pages=1 --dwn-dir="./output" [other arguments]

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Check if venv exists, create if not
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate venv
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import requests; import pandas" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Run AcademicArchiver from source
REM We set PYTHONPATH to include src so we can import top-level packages like core, extractors, etc.
set PYTHONPATH=%SCRIPT_DIR%src
python -m core.cli %*

REM Deactivate venv
call venv\Scripts\deactivate.bat
