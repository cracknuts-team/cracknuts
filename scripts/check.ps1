$PROJECT_HOME=Split-Path -Path $PSScriptRoot -Parent

ruff check $PROJECT_HOME
typos $PROJECT_HOME