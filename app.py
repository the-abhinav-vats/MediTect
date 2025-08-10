# app.py
import streamlit as st
from PIL import Image
import cv2
import numpy as np
import time
import threading

from ocr_utils import extract_text
from bar_utils import read_barcode
from date_utils import find_expiry_date
from match_utils import match_medicine_name, load_database

st.set_page_config(page_title="💊 AtomQuest Medicine Detector",
                   layout="wide",
                   page_icon="💊")

st.title("💊 Instant Medicine ID & Safety")
st.markdown("Scan medicine packaging (camera) or upload image → get name, expiry, uses & side-effects.")

# Sidebar controls
st.sidebar.header("Settings")
lang_choice = st.sidebar.selectbox("OCR Language", ["English", "Hindi", "Both"])
use_live = st.sidebar.checkbox("Enable Live Camera Mode (local only)", value=True)
top_k = st.sidebar.slider("Top matches to show (fuzzy)", 1, 5, 3)

# Load DB (for immediate feedback)
db = load_database()

# Left column: input, Right column: results
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Input")
    input_mode = st.radio("", ["📷 Camera (snapshot)", "📂 Upload Image", "🎥 Live Camera"], index=0)

    image = None
    if input_mode == "📷 Camera (snapshot)":
        camera_file = st.camera_input("Capture medicine (works in browser/mobile)")
        if camera_file:
            image = Image.open(camera_file).convert("RGB")

    elif input_mode == "📂 Upload Image":
        uploaded = st.file_uploader("Upload image (jpg/png)", type=["jpg", "jpeg", "png"])
        if uploaded:
            image = Image.open(uploaded).convert("RGB")

    elif input_mode == "🎥 Live Camera":
        st.info("Live camera uses your system webcam and runs locally. Click Start/Stop below.")
        start = st.button("Start Live Camera")
        stop = st.button("Stop Live Camera")
        live_placeholder = st.empty()

        # live capture handled via simple loop
        if 'live_running' not in st.session_state:
            st.session_state.live_running = False

        if start:
            st.session_state.live_running = True
        if stop:
            st.session_state.live_running = False

        if st.session_state.live_running:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                st.error("Could not open webcam. Run locally and allow camera access.")
            else:
                live_img_slot = st.empty()
                with st.spinner("Live camera running — press Stop to end"):
                    while st.session_state.live_running:
                        ret, frame = cap.read()
                        if not ret:
                            st.error("Failed reading frame from camera.")
                            break
                        # show frame
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        live_img_slot.image(frame_rgb, channels="RGB")
                        # small sleep to reduce CPU
                        time.sleep(0.1)
                    cap.release()
                live_img_slot.empty()

with col2:
    st.subheader("Result")
    result_area = st.empty()

if image is not None:
    # Process image
    result_area.info("Processing image...")

    # Convert PIL -> np array
    img_np = np.array(image)[:, :, ::-1].copy()  # RGB -> BGR for OpenCV if needed

    # Select languages for EasyOCR
    if lang_choice == "English":
        langs = ["en"]
    elif lang_choice == "Hindi":
        langs = ["hi"]
    else:
        langs = ["en", "hi"]

    # Step 1: OCR
    ocr_texts = extract_text(image, langs=langs)  # returns list[str]
    joined_text = " ".join(ocr_texts) if ocr_texts else ""

    # Step 2: Barcode
    barcode = read_barcode(image)  # returns str or None

    # Step 3: Expiry date
    expiry = find_expiry_date(ocr_texts)

    # Step 4: Medicine match (prefer barcode)
    query_for_match = barcode if barcode else joined_text
    matches = match_medicine_name(query_for_match, db, top_k=top_k)

    # Display
    with result_area.container():
        st.markdown("**Extracted OCR lines:**")
        if ocr_texts:
            for line in ocr_texts:
                st.write("-", line)
        else:
            st.write("_No text detected_")

        st.markdown("**Barcode / QR:**")
        st.write(barcode or "_Not found_")

        st.markdown("**Detected Expiry Date:**")
        st.write(expiry or "_Not found_")

        st.markdown("---")
        st.markdown("### 🔎 Matching Results")
        if matches:
            for i, m in enumerate(matches, start=1):
                st.markdown(f"**{i}. {m['name']}**  —  Score: {m['score']}")
                st.write(f"Manufacturer: {m.get('manufacturer','-')}")
                st.write(f"Uses: {m.get('uses','-')}")
                st.write(f"Dosage: {m.get('dosage','-')}")
                st.write(f"Side effects: {m.get('side_effects','-')}")
                if m.get('more_info_url'):
                    st.write(f"[More info]({m.get('more_info_url')})")
                st.markdown("---")
        else:
            st.warning("No matches found in database. Try different angle or enable barcode.")

        st.success("Processing complete ✅")

else:
    st.info("No image selected yet. Use Camera or Upload to start.")
