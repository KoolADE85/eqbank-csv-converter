# EQ Bank CSV to OFX Converter

A Python tool to convert EQ Bank CSV transaction exports to OFX (Open Financial Exchange) format for import into financial software like Homebank or other accounting applications.

## Usage
```
uv run convert
```

## Installation

1. Install dependencies using uv:
```bash
uv sync --dev
```

## Usage

The converter looks for CSV files matching the pattern `[account_number] Details.csv` (e.g., `123493788 Details.csv`).

Convert files in your Downloads folder:
```bash
uv run convert
```

Convert files and keep the originals:
```bash
uv run convert --keep
```

Convert files from a specific directory:
```bash
uv run convert --dir ~/Documents/bank-statements
```

## CSV File Format

The converter expects EQ Bank CSV files with the following columns:

- **Transfer date** - Date in YYYY-MM-DD format (e.g., "05 APR 2025")
- **Description** - Transaction description
- **Amount** - Transaction amount with $ symbol and sign (e.g., "$127.89" or "-$135.00")
- **Balance** - Account balance after transaction

Example CSV:
```csv
Transfer date,Description,Amount,Balance
05 APR 2025,Transfer from  124065372  to  123493788,$127.89,$3698.23
05 APR 2025,Transfer from  123493788  to  124065712,-$135,$3570.34
```

## Testing

Run all tests:
```bash
uv run pytest
```

### Test Structure

- `tests/data/` - Contains sample CSV files for testing
- `tests/runs/` - Output directory for test results (cleaned before each test run, preserved after for debugging)

### What the Tests Verify

1. CSV files exist in the test data directory
2. OFX files are created successfully
3. Account numbers appear in the generated OFX
4. Random sample transactions from CSV appear in OFX output
5. The `--keep` flag properly preserves original CSV files

## Development

### Code Quality

This project uses several tools to maintain code quality:

**Type Checking** (basedpyright):
```bash
uv run basedpyright
```

**Linting** (ruff):
```bash
uv run ruff check
```
