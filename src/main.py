import argparse
import sys
from pathlib import Path
import cv2 as cv

from scanner import scan_document

# Supported image file extensions
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp"}


def parsing_args():
    parser = argparse.ArgumentParser(description="ECG Document Scanner")
    parser.add_argument(
        "--input",
        required=True,
        help="Path to an image file OR directory containing images",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Destination path for scanned image file OR output directory",
    )
    return parser.parse_args()


def process_single_image(input_file: Path, output_file: Path) -> bool:
    """Scans a single image file and saves the result."""
    scanned_image = scan_document(str(input_file))
    if scanned_image is None:
        print(f"Error: Couldn't find document in '{input_file}'", file=sys.stderr)
        return False

    output_file.parent.mkdir(parents=True, exist_ok=True)

    success = cv.imwrite(str(output_file), scanned_image)
    if not success:
        print(f"Error: Couldn't write output to '{output_file}'", file=sys.stderr)
        return False

    print(f"Success! Saved: {output_file}")
    return True


def main():
    args = parsing_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Error: Input path '{input_path}' does not exist", file=sys.stderr)
        sys.exit(1)

    # CASE 1: Single file input
    if input_path.is_file():
        # If output path is an existing directory, save inside it with the same filename
        if output_path.is_dir():
            output_file = output_path / input_path.name
        else:
            output_file = output_path

        success = process_single_image(input_path, output_file)
        if not success:
            sys.exit(1)

    # CASE 2: Directory input (batch processing)
    elif input_path.is_dir():
        output_dir = output_path
        output_dir.mkdir(parents=True, exist_ok=True)

        # Collect all supported image files in the directory
        image_files = [
            f for f in input_path.iterdir()
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
        ]

        if not image_files:
            print(f"Warning: No valid images found in '{input_path}'", file=sys.stderr)
            sys.exit(0)

        print(f"Found {len(image_files)} image(s) in '{input_path}'. Processing...\n")

        success_count = 0
        fail_count = 0

        for img_file in image_files:
            out_file = output_dir / img_file.name
            if process_single_image(img_file, out_file):
                success_count += 1
            else:
                fail_count += 1

        print(f"\nFinished! {success_count} succeeded, {fail_count} failed.")
        if success_count == 0 and fail_count > 0:
            sys.exit(1)


if __name__ == "__main__":
    main()
