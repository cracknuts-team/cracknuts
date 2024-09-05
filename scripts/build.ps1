$PROJECT_HOME=Split-Path -Path $PSScriptRoot -Parent

python -m build -w $PROJECT_HOME
#echo $HOME_DIR