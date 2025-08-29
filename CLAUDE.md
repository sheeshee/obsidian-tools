# CLAUDE.md

## Available Scripts

### **auto_compose.py**

Extracts lines beginning with a given string into their own note.

#### Usage

```bash
python auto_compose.py -i <trigger_string> <file_path> [<output_dir>]
```

## Development Commands

### Dependencies
```bash
# Add dependencies
uv add package-name
```

### Code Quality
```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check

# Fix linting issues
uv run ruff check --fix
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test
uv run pytest tests/test_main.py::test_get_matches

# Run with verbose output
uv run pytest -v
```

## Code Style

- Line length: 88 characters
- Indentation: 4 spaces
- Quote style: double quotes
- Follows ruff configuration with pycodestyle, pyflakes, isort, and naming conventions
- Google-style docstrings
- Pre-commit hooks enforce trailing whitespace, end-of-file fixes, and YAML validation
