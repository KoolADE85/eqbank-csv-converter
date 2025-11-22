import csv
import random
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import get_csv_test_files
from eqdownload.convert import convert_csv_to_ofx


def extract_account_number(csv_filename: str) -> str:
    """Extract account number from CSV filename (format: '123456789 Details.csv')."""
    return Path(csv_filename).name.split()[0]


def parse_csv_transactions(csv_file: Path) -> list[dict[str, str]]:
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


@pytest.mark.parametrize("csv_file", get_csv_test_files(), ids=lambda f: f.name)
def test_convert_csv_to_ofx(csv_file: Path, work_dir: Path, eq_script: Path):
    dest_csv = work_dir / csv_file.name
    shutil.copy(csv_file, dest_csv)

    account_num = extract_account_number(csv_file.name)
    transactions = parse_csv_transactions(csv_file)
    assert len(transactions) > 0, f"No transactions found in {csv_file.name}"

    num_to_check = min(2, len(transactions))
    sample_transactions = random.sample(transactions, num_to_check)

    output_ofx = dest_csv.with_suffix(".ofx")

    try:
        convert_csv_to_ofx(str(dest_csv), str(output_ofx), str(eq_script))
        conversion_successful = True
    except SystemExit as e:
        conversion_successful = e.code == 0
        if not conversion_successful:
            pytest.fail(
                f"csv2ofx conversion failed for {csv_file.name} with exit code: {e.code}"
            )

    assert conversion_successful, f"csv2ofx conversion failed for {csv_file.name}"
    assert output_ofx.exists(), f"OFX file was not created: {output_ofx}"
    assert output_ofx.stat().st_size > 0, f"OFX file is empty: {output_ofx}"

    with open(output_ofx, "r", encoding="utf-8") as f:
        ofx_content = f.read()

    assert account_num in ofx_content, (
        f"Account number '{account_num}' not found in OFX file"
    )

    for transaction in sample_transactions:
        description = transaction.get("Description", "")
        if description:
            assert description in ofx_content, (
                f"Transaction description '{description}' not found in OFX file"
            )

        amount = transaction.get("Amount", "")
        if amount:
            amount_clean = amount.replace("$", "").replace(",", "")
            amount_numeric = amount_clean.lstrip("-")
            assert amount_numeric in ofx_content, (
                f"Transaction amount '{amount_numeric}' not found in OFX file"
            )


def test_convert_script_with_keep_flag(work_dir: Path, project_root: Path):
    csv_files = get_csv_test_files()
    if not csv_files:
        pytest.skip("No CSV files found in tests/data")

    copied_files: list[Path] = []
    for csv_file in csv_files:
        dest_csv = work_dir / csv_file.name
        shutil.copy(csv_file, dest_csv)
        copied_files.append(dest_csv)

    cmd = ["uv", "run", "eqconvert", str(work_dir), "--keep"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)

    assert result.returncode == 0, (
        f"convert.py failed\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    )

    for csv_file in copied_files:
        assert csv_file.exists(), (
            f"CSV file was deleted despite --keep flag: {csv_file}"
        )

    for csv_file in copied_files:
        ofx_file = csv_file.with_suffix(".ofx")
        assert ofx_file.exists(), f"OFX file was not created: {ofx_file}"
        assert ofx_file.stat().st_size > 0, f"OFX file is empty: {ofx_file}"
