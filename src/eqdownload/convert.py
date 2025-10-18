#!/usr/bin/env python3
import argparse
import glob
import os
import re
import sys
from pathlib import Path

from csv2ofx.main import run as csv2ofx_run


def get_default_downloads_dir():
    """Get the default Downloads directory in an OS-agnostic way."""
    # Try to get the user's Downloads directory
    # Works on Windows, macOS, and Linux
    home = Path.home()
    downloads = home / "Downloads"

    # On Windows, also check for localized Downloads folder
    if sys.platform == "win32":
        import winreg

        try:
            # Try to get the Downloads folder from Windows registry
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
            )
            downloads_path = winreg.QueryValueEx(
                key, "{374DE290-123F-4565-9164-39C4925E467B}"
            )[0]
            winreg.CloseKey(key)
            return downloads_path
        except Exception:
            pass

    # Default to ~/Downloads if it exists, otherwise use home directory
    return str(downloads) if downloads.exists() else str(home)


def find_csv_files(search_dir=None):
    """Find CSV files that match the pattern in the specified directory or default Downloads."""
    if search_dir:
        search_path = os.path.expanduser(search_dir)
    else:
        search_path = get_default_downloads_dir()

    # Pattern: numbers followed by "Details" optionally followed by number in parentheses, with .csv extension
    pattern = re.compile(r"^\d+\s*Details(\(\d+\))?.csv$")

    matching_files = []

    # Get all CSV files
    csv_files = glob.glob(os.path.join(search_path, "*.csv"))

    # Filter files based on the pattern
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        if pattern.match(filename):
            # Check if file is not empty
            if os.path.getsize(file_path) > 0:
                matching_files.append(file_path)

    return matching_files


def convert_csv_to_ofx(csv_file, output_file, eq_script):
    """
    Convert a single CSV file to OFX format using csv2ofx library directly.

    Args:
        csv_file: Path to the input CSV file
        output_file: Path to the output OFX file
        eq_script: Path to the EQ Bank mapping script

    Raises:
        SystemExit: If conversion fails
    """
    # Save the original sys.argv
    original_argv = sys.argv.copy()

    try:
        # Set sys.argv to mimic command-line invocation
        # This is needed because eq.py reads from sys.argv to extract the account number
        sys.argv = ["csv2ofx", "-x", eq_script, csv_file, output_file]

        # Build arguments for csv2ofx (without the program name)
        args = ["-x", eq_script, csv_file, output_file]

        # Call csv2ofx_run directly - it will call sys.exit on error
        csv2ofx_run(args)
    finally:
        # Always restore original sys.argv
        sys.argv = original_argv


def convert_csv_files(files, keep_csv=False):
    """Convert each CSV file to OFX format using csv2ofx."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    eq_script = os.path.join(script_dir, "eq.py")

    successful_conversions = []
    failed_conversions = []

    for csv_file in files:
        # Create output filename by replacing .csv with .ofx
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
            # csv2ofx_run calls sys.exit() on errors
            if e.code != 0:
                print(f"  Error converting {csv_file}: {e.code}")
                failed_conversions.append(csv_file)
            else:
                # Exit code 0 means success
                print("  Success!")
                successful_conversions.append(csv_file)
        except Exception as e:
            print(f"  Unexpected error: {e}")
            failed_conversions.append(csv_file)

    # Delete original CSV files if all conversions were successful and keep_csv flag is not set
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
    default_dir = get_default_downloads_dir()

    parser = argparse.ArgumentParser(
        description="Convert EQ Bank CSV files to OFX format"
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Keep CSV files after conversion (by default, CSV files are deleted)",
    )
    parser.add_argument(
        "--dir",
        type=str,
        help=f"Directory to search for CSV files (default: {default_dir})",
    )
    args = parser.parse_args()

    matching_files = find_csv_files(args.dir)

    search_dir = args.dir if args.dir else default_dir
    if matching_files:
        print(f"Found {len(matching_files)} EQ Bank transaction files in {search_dir}:")
        for file_path in matching_files:
            print(f"  {file_path}")

        print("\nStarting conversion...")
        convert_csv_files(matching_files, keep_csv=args.keep)
    else:
        print(f"No matching EQ Bank transaction files found in {search_dir}")


if __name__ == "__main__":
    main()
