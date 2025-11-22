#!/usr/bin/env python3
"""
Test script for convert.py

This test script:
1. Copies all CSV files from tests/data to tests/runs
2. Executes the convert script on the copied files
3. Asserts that OFX files are created successfully
4. Verifies that the account number is present in the OFX file
5. Checks that 1-2 random transaction lines from the CSV appear in the OFX file
"""

import csv
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# Add src to path so we can import convert module
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from eqdownload.convert import convert_csv_to_ofx  # noqa: E402

# Get the project root directory
TESTS_DATA_DIR = PROJECT_ROOT / "tests" / "data"
TESTS_RUNS_DIR = PROJECT_ROOT / "tests" / "runs"
EQ_SCRIPT = PROJECT_ROOT / "src" / "eqdownload" / "eq.py"


@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """
    Set up test environment before each test.

    Cleans up the runs directory BEFORE each test run to ensure a clean state.
    Does NOT clean up after tests, keeping data for debugging purposes.
    """
    # Clean up runs directory before test to ensure clean state
    if TESTS_RUNS_DIR.exists():
        shutil.rmtree(TESTS_RUNS_DIR)
    TESTS_RUNS_DIR.mkdir(parents=True, exist_ok=True)

    yield

    # Do not clean up after test - keep data for debugging purposes


def get_csv_files():
    """Get all CSV files from tests/data directory."""
    return list(TESTS_DATA_DIR.glob("*.csv"))


def extract_account_number(csv_filename: str) -> str:
    """Extract account number from CSV filename (format: '123456789 Details.csv')."""
    basename = os.path.basename(csv_filename)
    return basename.split()[0]


def parse_csv_transactions(csv_file: Path) -> list[dict[str, str]]:
    """Parse CSV file and return list of transaction dictionaries."""
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def test_csv_files_exist():
    """Test that there are CSV files in tests/data directory."""
    csv_files = get_csv_files()
    assert len(csv_files) > 0, f"No CSV files found in {TESTS_DATA_DIR}"


@pytest.mark.parametrize("csv_file", get_csv_files(), ids=lambda f: f.name)
def test_convert_csv_to_ofx(csv_file: Path):
    """
    Test conversion of a CSV file to OFX format.

    This test:
    1. Copies the CSV file to tests/runs
    2. Runs csv2ofx with the custom eq.py mapping
    3. Verifies OFX file is created
    4. Checks that account number appears in OFX
    5. Verifies that 1-2 random transactions appear in OFX
    """
    # Copy CSV file to runs directory
    dest_csv = TESTS_RUNS_DIR / csv_file.name
    shutil.copy(csv_file, dest_csv)

    # Extract account number from filename
    account_num = extract_account_number(csv_file.name)

    # Parse CSV transactions
    transactions = parse_csv_transactions(csv_file)
    assert len(transactions) > 0, f"No transactions found in {csv_file.name}"

    # Select 1-2 random transactions to verify
    num_to_check = min(2, len(transactions))
    sample_transactions = random.sample(transactions, num_to_check)

    # Define output OFX file path
    output_ofx = dest_csv.with_suffix(".ofx")

    # Run csv2ofx conversion directly (not via subprocess)
    try:
        convert_csv_to_ofx(str(dest_csv), str(output_ofx), str(EQ_SCRIPT))
        conversion_successful = True
    except SystemExit as e:
        conversion_successful = e.code == 0
        if not conversion_successful:
            pytest.fail(
                f"csv2ofx conversion failed for {csv_file.name} with exit code: {e.code}"
            )

    # Check that conversion was successful
    assert conversion_successful, f"csv2ofx conversion failed for {csv_file.name}"

    # Check that OFX file was created
    assert output_ofx.exists(), f"OFX file was not created: {output_ofx}"

    # Check that OFX file is not empty
    assert output_ofx.stat().st_size > 0, f"OFX file is empty: {output_ofx}"

    # Read OFX content
    with open(output_ofx, "r", encoding="utf-8") as f:
        ofx_content = f.read()

    # Verify account number appears in OFX file
    assert account_num in ofx_content, (
        f"Account number '{account_num}' not found in OFX file"
    )

    # Verify that sample transactions appear in OFX file
    for transaction in sample_transactions:
        # Check for description
        description = transaction.get("Description", "")
        if description:
            # The description should appear as-is in the OFX (preserving original spacing)
            # Look for it in the <NAME> tags
            assert description in ofx_content, (
                f"Transaction description '{description}' not found in OFX file"
            )

        # Check for amount (without currency symbol)
        amount = transaction.get("Amount", "")
        if amount:
            # Remove $ and commas for matching
            amount_clean = amount.replace("$", "").replace(",", "")
            # The amount might appear with or without the negative sign in different formats
            # Just check that the numeric part appears
            amount_numeric = amount_clean.lstrip("-")
            assert amount_numeric in ofx_content, (
                f"Transaction amount '{amount_numeric}' not found in OFX file"
            )


def test_convert_script_with_keep_flag():
    """
    Test that convert.py works with --keep flag.

    This test verifies that:
    1. CSV files are not deleted when --keep flag is used
    2. OFX files are created successfully
    """
    # Copy all CSV files to runs directory
    csv_files = get_csv_files()
    if not csv_files:
        pytest.skip("No CSV files found in tests/data")

    copied_files: list[Path] = []
    for csv_file in csv_files:
        dest_csv = TESTS_RUNS_DIR / csv_file.name
        shutil.copy(csv_file, dest_csv)
        copied_files.append(dest_csv)

    # Run convert command with --keep and --dir flags
    cmd = ["uv", "run", "eqconvert", "--keep", "--dir", str(TESTS_RUNS_DIR)]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)

    # Check that conversion script ran successfully
    assert result.returncode == 0, (
        f"convert.py failed\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    )

    # Verify that CSV files still exist (--keep flag)
    for csv_file in copied_files:
        assert csv_file.exists(), (
            f"CSV file was deleted despite --keep flag: {csv_file}"
        )

    # Verify that OFX files were created
    for csv_file in copied_files:
        ofx_file = csv_file.with_suffix(".ofx")
        assert ofx_file.exists(), f"OFX file was not created: {ofx_file}"
        assert ofx_file.stat().st_size > 0, f"OFX file is empty: {ofx_file}"


if __name__ == "__main__":
    # Run pytest with verbose output
    pytest.main([__file__, "-v"])
