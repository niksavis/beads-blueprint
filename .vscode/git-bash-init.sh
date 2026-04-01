# VS Code Git Bash init file.
# Activate the local Windows virtual environment when present, but do not fail if missing.
if [ -f ".venv/Scripts/activate" ]; then
  . ".venv/Scripts/activate"
fi
