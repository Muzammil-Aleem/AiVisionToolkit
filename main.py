
import argparse
from ocr_module import process_ocr
from object_detection import detect_objects

def main():
    parser = argparse.ArgumentParser(description="AI Project 4 - OCR + Object Detection")
    parser.add_argument("--mode", choices=["ocr", "detect"], required=True)
    parser.add_argument("--image", required=True, help="Path to image")
    parser.add_argument("--confidence", type=float, default=0.8)
    args = parser.parse_args()

    if args.mode == "ocr":
        process_ocr(args.image)
    else:
        detect_objects(args.image, args.confidence)

if __name__ == "__main__":
    main()
