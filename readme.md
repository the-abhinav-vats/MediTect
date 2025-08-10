# AtomQuest25 — AI Medicine Detector

## Overview
AtomQuest25 is a modular Streamlit app to detect medicines from packaging using camera or uploaded images.
Features: English/Hindi OCR, barcode scan, expiry detection, fuzzy matching against a local medicines DB, side-effects info.

## Run (recommended local)
1. Create venv and activate
2. `pip install -r requirements.txt`
3. `streamlit run app.py`

> Live camera mode uses your system webcam — run locally (not in remote cloud like Colab).

## Structure
- app.py
- ocr_utils.py
- bar_utils.py
- date_utils.py
- match_utils.py
- database/medicines.csv

## Notes
- To improve OCR accuracy, later add label-crop with YOLOv8/YOLOv9.
- Add Hindi fonts/support by installing required Tesseract or enabling EasyOCR Hindi models.
