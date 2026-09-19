from pathlib import Path
import sys
import argparse
from scanner import scan_document
def parsing_args():
    parser = parseargs.argument_parser()
    parser.add_argument("--input", required = True, help = "path to your document")
    parser.add_argument("--output", required = True, help = "path where you want your scanned document")
    return parser.parse_args()

def main():
    args = parsing_args()
    input_path = Path(args.input)
    if not input_path.is_file():
        print("image path is not valid")
        sys.exit(1)
    
    scanned_image = scan_document(input_path)
    if scanned_image is None:
        print("Couldn't find document")
        sys.exit(1)
    output_path = args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    success = cv.imwrite(str(output_path), scanned_image)
    if success is None:
        print("couldn't write file to destination")
        sys.exit(1)
    print(f"Success! scanned image is at {output_path}")

if __name__ == "__main__":
    main()
    
