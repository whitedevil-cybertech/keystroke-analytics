set dotenv-load
set export
set shell := ["bash", "-uc"]
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# Show available commands
default:
    @just --list --unsorted

# ── Setup ────────────────────────────────────────────────────────────

# Create venv and install all dependencies
[group('setup')]
setup:
    @echo "Setting up environment..."
    uv venv
    uv sync --all-extras
    @echo ""
    @echo "Setup complete! Activate with:"
    @echo "  source .venv/bin/activate  (Linux/macOS)"
    @echo "  .venv\\Scripts\\activate    (Windows)"

# Install main dependencies only
[group('setup')]
install:
    uv sync

# ── Testing & Quality ────────────────────────────────────────────────

# Run test suite
[group('test')]
test:
    uv run pytest tests/ -v

# Lint with ruff
[group('test')]
lint:
    uv run ruff check keystroke_analytics/ tests/

# Type check with mypy
[group('test')]
typecheck:
    uv run mypy keystroke_analytics/

# Run all quality checks
[group('test')]
check: lint typecheck test
    @echo "All checks passed!"

# Format code
[group('test')]
format:
    uv run ruff format keystroke_analytics/ tests/

# ── Run ──────────────────────────────────────────────────────────────

# Start a capture session
[group('run')]
[confirm("This will start keystroke capture. Continue?")]
run:
    uv run python -m keystroke_analytics run

# Start with encryption enabled
[group('run')]
[confirm("This will start encrypted capture. Continue?")]
run-encrypted:
    uv run python -m keystroke_analytics run --encrypt

# Decrypt a log file (set FILE=path/to/file.enc)
[group('run')]
decrypt FILE:
    uv run python -m keystroke_analytics decrypt {{FILE}}

# ── Utilities ────────────────────────────────────────────────────────

# Remove venv and caches
[group('utility')]
clean:
    rm -rf .venv __pycache__ .pytest_cache .mypy_cache .ruff_cache
    rm -rf keystroke_analytics/__pycache__
    rm -rf tests/__pycache__
    rm -rf build dist *.egg-info
    @echo "Cleaned"

# Lock dependencies
[group('utility')]
lock:
    uv lock

# Update all dependencies
[group('utility')]
update:
    uv lock --upgrade
    uv sync --all-extras
