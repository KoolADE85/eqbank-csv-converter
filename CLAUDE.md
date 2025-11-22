# eqdownload Project Context

## Purpose
Convert CSV transaction downloads (from EQ Bank) to OFX format using csv2ofx.

## Structure
- `src/eqdownload/convert.py` - CLI entry point
- `src/eqdownload/eq.py` - EQ Bank-specific csv2ofx mapping
- `tests/` - Pytest tests with sample data

## Development
```bash
uv sync          # Install dependencies
uv run pytest    # Run tests
```

## Quality Checks
- Type checking: `uv run basedpyright` (must show 0 errors, 0 warnings)
- Linting: `uv run ruff check`
- Formatting: `uv run ruff format`
