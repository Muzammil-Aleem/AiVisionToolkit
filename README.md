
# AI Project 4 – Intelligent Training Kit

This project fully implements the requirements from your PDF:

✅ OCR (Optical Character Recognition) using **pytesseract**  
✅ Image preprocessing (**grayscale, blur, adaptive thresholding**)  
✅ Object Detection using **MobileNet-SSD + OpenCV DNN**  
✅ Confidence thresholding (**80% minimum**)  
✅ Visual outputs saved automatically  

## Project Structure

- `main.py` → main launcher
- `ocr_module.py` → OCR pipeline
- `object_detection.py` → object detection
- `download_models.py` → downloads MobileNet SSD model
- `outputs/` → generated results
- `models/` → downloaded AI models

## Installation

### 1. Install Python
Install Python 3.10+

### 2. Install Tesseract OCR

Windows:
Download from:
https://github.com/UB-Mannheim/tesseract/wiki

During installation, add Tesseract to PATH.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download AI model

```bash
python download_models.py
```

## Run OCR

```bash
python main.py --mode ocr --image sample.jpg
```

Output:
- Extracted text
- Processed image
- Saved text file

## Run Object Detection

```bash
python main.py --mode detect --image sample.jpg
```

Output:
- Bounding boxes
- Labels
- Confidence scores (80% threshold)

## Milestone Validation

✔ Library integration  
✔ Preprocessing integrity  
✔ 80% confidence threshold  
✔ Visual confirmation output
