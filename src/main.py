import argparse
import sys
from pathlib import Path
import cv2 as cv

from scanner import scan_document


def parsing_args():
    # Fix 1: Correct module and class name
    parser = argparse.ArgumentParser(description="ECG Document Scanner")
    parser.add_argument("--input", required=True, help="Path to your document")
    parser.add_argument("--output", required=True, help="Path where you want your scanned document")
    return parser.parse_args()


def main():
    args = parsing_args()

    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Error: image path '{input_path}' is not valid", file=sys.stderr)
        sys.exit(1)

    scanned_image = scan_document(str(input_path))
    if scanned_image is None:
        print("Error: Couldn't find document in the image", file=sys.stderr)
        sys.exit(1)

    # Fix 3: Wrap args.output in Path()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Fix 2 & 4: cv is imported, check for boolean False
    success = cv.imwrite(str(output_path), scanned_image)
    if not success:
        print(f"Error: couldn't write file to destination: '{output_path}'", file=sys.stderr)
        sys.exit(1)

    print(f"Success! scanned image is at {output_path}")


if __name__ == "__main__":
    main()
