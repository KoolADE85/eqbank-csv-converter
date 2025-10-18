# eqdownload Project Context

## Purpose
Convert EQ Bank CSV transaction files to OFX format.

## File Structure
- `src/eqdownload/convert.py` - Main CLI script with `main()` entry point
- `src/eqdownload/eq.py` - EQ Bank-specific mapping for csv2ofx
- `src/eqdownload/__init__.py` - Package init
- `tests/test_convert.py` - Pytest tests
- `tests/data/` - Test CSV files (committed)
- `tests/runs/` - Test output (gitignored, cleaned before each test, kept after for debugging)
- `pyproject.toml` - Project config, dependencies, pytest/basedpyright settings

## Key Implementation Details

### eq.py
- Parses account number from CSV filename via sys.argv
- Type-safe with full basedpyright compliance (no errors/warnings)
- Uses typed functions instead of lambdas for csv2ofx mapping
- CSV format: "Transfer date", "Description", "Amount" (with $ and sign), "Balance"
- Date format: "%Y-%m-%d"

### convert.py
- Searches for CSV files matching pattern: `^\d+\s*Details(\(\d+\))?.csv$`
- Uses csv2ofx command (no hardcoded venv paths) with `-x` flag pointing to eq.py
- `--keep` flag prevents CSV deletion after conversion
- `--dir` specifies search directory (default: OS-agnostic Downloads folder)
- OS-agnostic Downloads detection: uses Path.home()/Downloads on Unix/macOS, registry on Windows
- Installed as `convert` executable via pyproject.toml entry point
- Entry point: `eqdownload.convert:main`

### Tests
- Run: `uv run pytest` (no args needed)
- 3 tests: csv_files_exist, parametrized convert test, convert script with --keep
- Verifies: OFX creation, account number presence, random transaction presence
- Test data preserved in tests/runs/ after execution

## Commands
```bash
uv sync --dev                           # Install dependencies
uv run convert                          # Run conversion (production mode only - not for testing or development)
uv run pytest                           # Run conversion (testing or development mode)
uv run basedpyright                     # Type check
uv run ruff check                       # Lint
uv run ruff format                      # Format
```
