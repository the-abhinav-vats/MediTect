# bar_utils.py
from pyzbar import pyzbar
import numpy as np
from PIL import Image

def read_barcode(image: Image.Image):
    """
    Returns first decoded barcode/QR string or None
    """
    img = image.convert("RGB")
    np_img = np.array(img)
    decoded = pyzbar.decode(np_img)
    if not decoded:
        return None
    # Return first non-empty decode
    for d in decoded:
        try:
            s = d.data.decode('utf-8', errors='ignore').strip()
            if s:
                return s
        except:
            continue
    return None
