# eqdownload Project Context

## Purpose
Convert EQ Bank CSV transaction files to OFX format using csv2ofx.

## Structure
- `src/eqdownload/convert.py` - CLI entry point
- `src/eqdownload/eq.py` - EQ Bank-specific csv2ofx mapping
- `tests/` - Pytest tests with sample data

## Development
```bash
uv sync          # Install dependencies
uv run pytest    # Run tests
```

**Important:** Never run `uv run eqconvert` without the `--dir` parameter as it defaults to the user's Downloads folder. Always use `uv run eqconvert --dir <path>` when testing.

## Quality Checks
- Type checking: `uv run basedpyright` (must show 0 errors, 0 warnings)
- Linting: `uv run ruff check`
- Formatting: `uv run ruff format`
