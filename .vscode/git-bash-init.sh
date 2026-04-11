# VS Code Git Bash init file.
# Activate the local Windows virtual environment when present.
# Do not fail if the virtual environment has not been created yet.
if [ -f ".venv/Scripts/activate" ]; then
  . ".venv/Scripts/activate"
fi
