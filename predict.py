"""Command-line lung-cancer prediction.

Usage:
    python predict.py <image_path> [<image_path> ...]
"""

import sys

from classifier import classify_single_image


def main(argv):
    if len(argv) < 2:
        print("Usage: python predict.py <image_path> [<image_path> ...]")
        return 1

    exit_code = 0
    for image_path in argv[1:]:
        prediction = classify_single_image(image_path)
        if prediction is None:
            print(f"{image_path}: ERROR - could not read image")
            exit_code = 1
        else:
            print(f"{image_path}: {prediction}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
