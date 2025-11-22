#!/usr/bin/env python3
import argparse
import glob
import os
import re
import sys

from csv2ofx.main import run as csv2ofx_run  # type: ignore[import-untyped]


def find_csv_files(search_dir: str) -> list[str]:
    """Find CSV files that match the pattern in the specified directory."""
    search_path = os.path.expanduser(search_dir)

    # Pattern: numbers followed by "Details" optionally followed by number in parentheses, with .csv extension
    pattern = re.compile(r"^\d+\s*Details(\(\d+\))?.csv$")

    matching_files: list[str] = []
    csv_files = glob.glob(os.path.join(search_path, "*.csv"))

    for file_path in csv_files:
        filename = os.path.basename(file_path)
        if pattern.match(filename) and os.path.getsize(file_path) > 0:
            matching_files.append(file_path)

    return matching_files


def convert_csv_to_ofx(csv_file: str, output_file: str, eq_script: str):
    """
    Convert a single CSV file to OFX format using csv2ofx library directly.

    Args:
        csv_file: Path to the input CSV file
        output_file: Path to the output OFX file
        eq_script: Path to the EQ Bank mapping script

    Raises:
        SystemExit: If conversion fails
    """
    original_argv = sys.argv.copy()

    try:
        # eq.py reads from sys.argv to extract the account number
        sys.argv = ["csv2ofx", "-x", eq_script, csv_file, output_file]
        args = ["-x", eq_script, csv_file, output_file]
        csv2ofx_run(args)
    finally:
        sys.argv = original_argv


def convert_csv_files(files: list[str], keep_csv: bool = False):
    """Convert each CSV file to OFX format using csv2ofx."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    eq_script = os.path.join(script_dir, "eq.py")

    successful_conversions: list[str] = []
    failed_conversions: list[str] = []

    for csv_file in files:
        base_name = os.path.splitext(csv_file)[0]
        output_file = f"{base_name}.ofx"

        print(
            f"Converting {os.path.basename(csv_file)} to {os.path.basename(output_file)}..."
        )

        try:
            convert_csv_to_ofx(csv_file, output_file, eq_script)
            print("  Success!")
            successful_conversions.append(csv_file)
        except SystemExit as e:
            if e.code != 0:
                print(f"  Error converting {csv_file}: {e.code}")
                failed_conversions.append(csv_file)
            else:
                print("  Success!")
                successful_conversions.append(csv_file)
        except Exception as e:
            print(f"  Unexpected error: {e}")
            failed_conversions.append(csv_file)

    if failed_conversions:
        print(
            f"\n{len(failed_conversions)} files failed to convert. Not deleting any CSV files."
        )
    else:
        print(f"\nAll {len(successful_conversions)} files converted successfully.")
        if not keep_csv:
            print("Deleting original CSV files...")
            for csv_file in successful_conversions:
                try:
                    os.remove(csv_file)
                    print(f"  Deleted {os.path.basename(csv_file)}")
                except Exception as e:
                    print(f"  Error deleting {csv_file}: {e}")


def main():
    """Main entry point for the eqdownload converter."""
    parser = argparse.ArgumentParser(
        description="Convert EQ Bank CSV files to OFX format"
    )
    parser.add_argument(
        "directory",
        type=str,
        help="Directory to search for CSV files",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Keep CSV files after conversion (by default, CSV files are deleted)",
    )
    args = parser.parse_args()

    matching_files = find_csv_files(args.directory)

    if matching_files:
        print(
            f"Found {len(matching_files)} EQ Bank transaction files in {args.directory}:"
        )
        for file_path in matching_files:
            print(f"  {file_path}")

        print("\nStarting conversion...")
        convert_csv_files(matching_files, keep_csv=args.keep)
    else:
        print(f"No matching EQ Bank transaction files found in {args.directory}")


if __name__ == "__main__":
    main()
