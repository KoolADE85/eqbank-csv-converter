# EQ Bank CSV to OFX Converter

A Python tool to convert EQ Bank CSV transaction exports to OFX (Open Financial Exchange) format for import into financial software like Homebank or other accounting applications.


## Installation

1. Install dependencies using uv:
```bash
uv sync --dev
source .venv/bin/activate
```

All commands can be run with `uv run <command>`.

## Usage

The converter looks for CSV files matching the pattern `[account_number] Details.csv` (e.g., `123456789 Details.csv`).

Convert files in your Downloads folder:
```bash
eqconvert
```

Convert files and keep the originals:
```bash
eqconvert --keep
```

Convert files from a specific directory:
```bash
eqconvert --dir ~/Documents/bank-statements
```


## Testing

Run all tests:
```bash
pytest
```

### Test Structure

- `tests/data/` - Contains sample CSV files for testing
- `tests/runs/` - Output directory for test results (cleaned before each test run, preserved after for debugging)
