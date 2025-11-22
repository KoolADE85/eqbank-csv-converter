import shutil
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
TESTS_DATA_DIR = PROJECT_ROOT / "tests" / "data"
TESTS_RUNS_DIR = PROJECT_ROOT / "tests" / "runs"


@pytest.fixture(autouse=True)
def work_dir():
    """Provide working directory and clean it before each test. Preserved after for debugging."""
    if TESTS_RUNS_DIR.exists():
        shutil.rmtree(TESTS_RUNS_DIR)
    TESTS_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    return TESTS_RUNS_DIR


@pytest.fixture
def eq_script():
    return PROJECT_ROOT / "src" / "eqdownload" / "eq.py"


@pytest.fixture
def project_root():
    return PROJECT_ROOT


def get_csv_test_files():
    csv_files = list(TESTS_DATA_DIR.glob("*.csv"))
    assert len(csv_files) > 0, "No CSV test files found."
    return csv_files
