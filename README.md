# EQ Bank CSV to OFX Converter

A Python tool to convert EQ Bank .csv transaction exports to .ofx format for import into financial software.


## Installation

1. Install dependencies using uv:
```bash
uv sync --dev
source .venv/bin/activate
```

All commands can be run with `uv run <command>`.


## Usage

The converter looks for CSV files matching the pattern `[account_number] Details.csv` (e.g., `123456789 Details.csv`) in the specified directory.

Convert files in your Downloads folder:
```bash
eqconvert ~/Downloads
```

Convert files and keep the originals:
```bash
eqconvert ~/Downloads --keep
```


## Testing

Run all tests:
```bash
pytest
```

### Test Structure

- `tests/data/` - Contains sample CSV files for testing
- `tests/runs/` - Output directory for test results (cleaned before each test run, preserved after for debugging)
