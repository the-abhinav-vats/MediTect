# ocr_utils.py
import easyocr
import numpy as np
from PIL import Image
import streamlit as st

@st.cache_resource
def get_reader(langs):
    # langs: list like ['en'] or ['hi'] or ['en','hi']
    return easyocr.Reader(langs, gpu=False)

def extract_text(image: Image.Image, langs=['en']):
    """
    image: PIL.Image
    langs: list of language codes for EasyOCR, e.g. ['en'] or ['hi'] or ['en','hi']
    returns: list of text lines (strings)
    """
    if isinstance(langs, str):
        langs = [langs]
    reader = get_reader(langs)
    img_np = np.array(image.convert("RGB"))[:, :, ::-1]  # RGB -> BGR for easyocr internal
    try:
        results = reader.readtext(img_np, detail=0)  # detail=0 returns only text
        # results is list[str]
        return [r.strip() for r in results if r and r.strip()]
    except Exception as e:
        print("OCR error:", e)
        return []
