
import cv2
import pytesseract
import outputs
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def preprocess(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Invert: white text on dark bg → dark text on white bg
    inverted = cv2.bitwise_not(gray)
    
    # Resize to improve OCR accuracy
    scale = 2
    resized = cv2.resize(inverted, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(resized, h=30)
    
    # Threshold
    thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    return thresh

def process_ocr(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Cannot open {image_path}")

    processed = preprocess(image)
    text = pytesseract.image_to_string(processed, config="--psm 6 --oem 3")
    
    os.makedirs("outputs", exist_ok=True)
    cv2.imwrite("outputs/ocr_processed.png", processed)

    with open("outputs/extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(text)

    print("\n===== EXTRACTED TEXT =====\n")
    print(text if text.strip() else "No text detected")
    print("\nSaved processed image + extracted text inside outputs/")
