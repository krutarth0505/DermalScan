import streamlit as st
import numpy as np
import cv2
import io
import csv
from backend import process_image
from datetime import datetime
import time
from PIL import Image

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import Image as RLImage
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    PDF_SUPPORT = True
except Exception:
    PDF_SUPPORT = False


RECOMMENDATIONS = {
    "Wrinkles": [
        "Apply a broad-spectrum sunscreen (SPF 30+) every day.",
        "Use a nightly retinol or peptide-based moisturizer.",
        "Stay hydrated and avoid smoking to reduce early skin aging.",
        "Consider consulting a dermatologist for targeted anti-aging treatment."
    ],
    "Dark Spots": [
        "Use sunscreen daily to prevent spots from getting darker.",
        "Try products with vitamin C, niacinamide, or azelaic acid.",
        "Avoid picking acne or irritated skin to reduce post-inflammatory marks.",
        "See a dermatologist for persistent pigmentation concerns."
    ],
    "Puffy Eyes": [
        "Use a cold compress for 5 to 10 minutes to reduce swelling.",
        "Improve sleep quality and limit high-salt foods, especially at night.",
        "Use a caffeine or hyaluronic acid based eye gel.",
        "If puffiness is frequent, discuss allergy or sinus causes with a doctor."
    ],
    "Clear Skin": [
        "Maintain a gentle cleanse-moisturize-sunscreen routine.",
        "Keep using non-comedogenic skincare products.",
        "Stay hydrated and maintain a balanced diet.",
        "Continue regular preventive care and monitor changes in skin health."
    ]
}

LABEL_THEME = {
    "Wrinkles": "#f59e0b",
    "Dark Spots": "#f97316",
    "Puffy Eyes": "#38bdf8",
    "Clear Skin": "#34d399"
}


def _image_bgr_to_png_bytes(image_bgr):
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    img_buffer = io.BytesIO()
    pil_image.save(img_buffer, format="PNG")
    return img_buffer.getvalue()


def _build_pdf_report(result, recommendations, timestamp, original_img, annotated_img):
    pdf_buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        leftMargin=32,
        rightMargin=32,
        topMargin=32,
        bottomMargin=32
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#1f2a55"),
        spaceAfter=10
    )
    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#0b1025"),
        spaceBefore=8,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14
    )

    story = []

    story.append(Paragraph("DermalScan Analysis Report", title_style))
    story.append(Paragraph(f"Generated: {timestamp}", body_style))
    story.append(Spacer(1, 10))

    summary_data = [
        ["Predicted Class", str(result["label"])],
        ["Confidence", f"{result['confidence']:.2f}%"],
    ]

    if "face_id" in result:
        summary_data.append(["Face", f"Face {result['face_id']}"])

    summary_table = Table(summary_data, colWidths=[140, 340])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eef2ff")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#111827")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)

    story.append(Spacer(1, 12))
    story.append(Paragraph("Basic Recommendations", section_style))
    for tip in recommendations:
        story.append(Paragraph(f"- {tip}", body_style))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Image Preview", section_style))

    original_img_bytes = _image_bgr_to_png_bytes(original_img)
    annotated_img_bytes = _image_bgr_to_png_bytes(annotated_img)

    original_pdf_img = RLImage(io.BytesIO(original_img_bytes), width=240, height=180)
    annotated_pdf_img = RLImage(io.BytesIO(annotated_img_bytes), width=240, height=180)

    image_table = Table(
        [[original_pdf_img, annotated_pdf_img],
         [Paragraph("Uploaded Image", body_style), Paragraph("Annotated Output", body_style)]],
        colWidths=[250, 250]
    )
    image_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
    ]))
    story.append(image_table)

    story.append(Spacer(1, 12))
    story.append(Paragraph("Note: This report provides AI-assisted guidance and is not a medical diagnosis.", body_style))

    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

#  PAGE CONFIG 
st.set_page_config(
    page_title="DermalScan",
    page_icon="🧴",
    layout="wide"
)

#  APPLE-STYLE CSS 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Manrope:wght@400;500;700&display=swap');

:root {
    --bg-top: #1c2752;
    --bg-bottom: #070b1a;
    --surface: rgba(255, 255, 255, 0.10);
    --surface-strong: rgba(255, 255, 255, 0.16);
    --border: rgba(255, 255, 255, 0.18);
    --text-primary: #f8fafc;
    --text-secondary: #d9e2ff;
    --chip-text: #0f172a;
    --accent-a: #40a9ff;
    --accent-b: #7c9cff;
}

/* Background */
html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(42rem 24rem at 8% 10%, rgba(56, 189, 248, 0.22), transparent 65%),
        radial-gradient(38rem 22rem at 92% 12%, rgba(147, 197, 253, 0.18), transparent 65%),
        linear-gradient(165deg, var(--bg-top), var(--bg-bottom));
    font-family: "Manrope", "Segoe UI", Arial, sans-serif;
}

[data-testid="stAppViewContainer"] > .main {
    animation: fadeIn 420ms ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Header */
.main-title {
    text-align: center;
    font-family: "Space Grotesk", "Segoe UI", sans-serif;
    letter-spacing: 0.4px;
    font-size: clamp(34px, 5vw, 48px);
    font-weight: 700;
    color: var(--text-primary);
}
.subtitle {
    text-align: center;
    font-size: 17px;
    color: var(--text-secondary);
    margin-bottom: 30px;
}

/* Card */
.apple-card {
    background: linear-gradient(145deg, var(--surface), rgba(255, 255, 255, 0.05));
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 20px;
    border: 1px solid var(--border);
    box-shadow: 0 16px 34px rgba(2, 6, 23, 0.45);
    transition: transform 180ms ease, border-color 180ms ease;
}

.apple-card:hover {
    transform: translateY(-2px);
    border-color: rgba(148, 163, 184, 0.45);
}

/* Titles */
.apple-title {
    font-family: "Space Grotesk", "Segoe UI", sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 12px;
}

/* Text */
.apple-text {
    color: #e6ecff;
    font-size: 16px;
    line-height: 1.5;
}

/* Badge */
.apple-badge {
    display: inline-block;
    padding: 9px 14px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.88);
    color: var(--chip-text);
    font-weight: 700;
    font-size: 16px;
    border: 1px solid rgba(255, 255, 255, 0.5);
}

/* Confidence pill */
.apple-pill {
    margin-top: 10px;
    padding: 8px 14px;
    border-radius: 999px;
    background: linear-gradient(135deg, var(--accent-a), var(--accent-b));
    color: #f8fafc;
    font-weight: 700;
    display: inline-block;
    font-size: 14px;
}

.confidence-track {
    margin-top: 12px;
    height: 10px;
    border-radius: 999px;
    background: rgba(148, 163, 184, 0.32);
    overflow: hidden;
}

.confidence-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #22d3ee, #60a5fa 60%, #818cf8);
    transition: width 260ms ease;
}

/* Face chips */
[data-testid="stRadio"] [role="radiogroup"] {
    gap: 0.5rem;
}

[data-testid="stRadio"] [role="radio"] {
    border: 1px solid rgba(148, 163, 184, 0.45);
    border-radius: 999px;
    padding: 0.35rem 0.75rem;
    background: rgba(15, 23, 42, 0.45);
}

[data-testid="stRadio"] [role="radio"][aria-checked="true"] {
    background: linear-gradient(135deg, rgba(64, 169, 255, 0.92), rgba(124, 156, 255, 0.92));
    border-color: rgba(255, 255, 255, 0.55);
}

/* Buttons */
[data-testid="stDownloadButton"] button {
    border-radius: 12px;
    border: 1px solid rgba(148, 163, 184, 0.35);
    background: linear-gradient(140deg, rgba(15, 23, 42, 0.85), rgba(30, 41, 59, 0.75));
    color: #f8fafc;
    font-weight: 600;
    transition: transform 120ms ease, box-shadow 120ms ease;
}

[data-testid="stDownloadButton"] button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.35);
}

/* FORCE WIDGET TEXT WHITE */
[data-testid="stRadio"] *,
[data-testid="stFileUploader"] *,
[data-testid="stCameraInput"] *,
[data-testid="stToggle"] *,
label {
    color: var(--text-primary) !important;
}

@media (max-width: 900px) {
    .apple-card {
        padding: 18px;
        border-radius: 16px;
    }
    .apple-title {
        font-size: 19px;
    }
    .apple-text {
        font-size: 15px;
    }
}

</style>
""", unsafe_allow_html=True)

#  HEADER 
st.markdown("<div class='main-title'>🧴 DermalScan</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>AI-Powered Facial Skin Condition Analysis</div>",
    unsafe_allow_html=True
)

#  INPUT SOURCE 
st.markdown("<div class='apple-card'>", unsafe_allow_html=True)
st.markdown("<div class='apple-title'>📸 Choose Input Source</div>", unsafe_allow_html=True)

source = st.radio(
    "Select image source",
    ["Upload Image", "Use Live Camera"],
    horizontal=True
)

st.markdown("</div>", unsafe_allow_html=True)

img = None

#  UPLOAD IMAGE 
if source == "Upload Image":
    uploaded = st.file_uploader(
        "Upload a facial image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded:
        file_bytes = np.frombuffer(uploaded.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

#  LIVE CAMERA
else:
    enable_camera = st.toggle("Turn on camera", value=False)
    if enable_camera:
        camera_img = st.camera_input("Capture image using camera")
        if camera_img:
            file_bytes = np.frombuffer(camera_img.getvalue(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    else:
        st.info("Camera stays off until you enable it.")

# PROCESS IMAGE 
if img is not None:

    col1, col2 = st.columns(2)

    # ORIGINAL IMAGE
    with col1:
        st.markdown("<div class='apple-card'>", unsafe_allow_html=True)
        st.markdown("<div class='apple-title'>Input Image</div>", unsafe_allow_html=True)
        st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        st.markdown("</div>", unsafe_allow_html=True)

    # MODEL PROCESSING
    start_time = time.time()
    annotated_img, results = process_image(img)
    processing_time = time.time() - start_time

    # OUTPUT IMAGE
    with col2:
        st.markdown("<div class='apple-card'>", unsafe_allow_html=True)
        st.markdown("<div class='apple-title'>Analysis Output</div>", unsafe_allow_html=True)
        st.image(cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB))
        st.markdown("</div>", unsafe_allow_html=True)

    # RESULTS
    if results:
        selected_face_idx = 0

        if len(results) > 1:
            st.markdown("<div class='apple-card'>", unsafe_allow_html=True)
            st.markdown("<div class='apple-title'>Detected Faces</div>", unsafe_allow_html=True)

            face_options = list(range(len(results)))
            selected_face_idx = st.radio(
                "Select face",
                face_options,
                horizontal=True,
                format_func=lambda i: f"Face {results[i].get('face_id', i + 1)}"
            )

            st.markdown("</div>", unsafe_allow_html=True)

        r = results[selected_face_idx]

        if r.get("warning"):
            st.warning(r["warning"])

        # CONDITION
        st.markdown("<div class='apple-card'>", unsafe_allow_html=True)
        st.markdown("<div class='apple-title'>Detected Skin Condition</div>", unsafe_allow_html=True)
        if len(results) > 1:
            st.markdown(
                f"<div class='apple-text'>Selected: Face {r.get('face_id', selected_face_idx + 1)}</div>",
                unsafe_allow_html=True
            )
        label_color = LABEL_THEME.get(r["label"], "#34d399")
        st.markdown(
            f"<div class='apple-badge' style='border-left: 6px solid {label_color};'>🧴 {r['label']}</div>",
            unsafe_allow_html=True
        )
        st.markdown(f"<div class='apple-pill'>Confidence: {r['confidence']:.2f}%</div>", unsafe_allow_html=True)
        confidence_width = max(0.0, min(float(r["confidence"]), 100.0))
        st.markdown(
            f"<div class='confidence-track'><div class='confidence-fill' style='width:{confidence_width:.2f}%;'></div></div>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # PROBABILITIES
        st.markdown("<div class='apple-card'>", unsafe_allow_html=True)
        st.markdown("<div class='apple-title'>Probability Distribution</div>", unsafe_allow_html=True)

        for k, v in r["probabilities"].items():
            st.markdown(f"<div class='apple-text'><b>{k}</b>: {v:.1f}%</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # PROCESSING TIME
        st.markdown("<div class='apple-card'>", unsafe_allow_html=True)
        st.markdown("<div class='apple-title'>Processing Time</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='apple-text'>⏱ {processing_time:.2f} seconds</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # BASIC RECOMMENDATIONS
        st.markdown("<div class='apple-card'>", unsafe_allow_html=True)
        st.markdown("<div class='apple-title'>Basic Recommendations</div>", unsafe_allow_html=True)

        label = r["label"]
        tips = RECOMMENDATIONS.get(label, ["No recommendation available for this class."])

        for tip in tips:
            st.markdown(f"<div class='apple-text'>• {tip}</div>", unsafe_allow_html=True)

        st.markdown(
            "<div class='apple-text'><i>Note: These are general tips, not a medical diagnosis.</i></div>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # DOWNLOAD
        st.markdown("<div class='apple-card'>", unsafe_allow_html=True)
        st.markdown("<div class='apple-title'>Download Results</div>", unsafe_allow_html=True)

        report_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        csv_buffer = io.StringIO()
        csv_writer = csv.DictWriter(
            csv_buffer,
            fieldnames=["label", "confidence", "probabilities", "face_id", "bbox", "warning"]
        )
        csv_writer.writeheader()
        for row in results:
            out_row = dict(row)
            out_row["probabilities"] = str(out_row.get("probabilities", {}))
            out_row["bbox"] = str(out_row.get("bbox", None))
            csv_writer.writerow(out_row)

        st.download_button(
            "📄 Download CSV Report",
            csv_buffer.getvalue().encode("utf-8"),
            file_name=f"dermalscan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

        _, png_img = cv2.imencode(".png", annotated_img)
        st.download_button(
            "🖼 Download Annotated Image",
            png_img.tobytes(),
            file_name=f"dermalscan_result.png",
            mime="image/png"
        )

        if PDF_SUPPORT:
            pdf_bytes = _build_pdf_report(
                result=r,
                recommendations=tips,
                timestamp=report_timestamp,
                original_img=img,
                annotated_img=annotated_img
            )
            st.download_button(
                "📘 Download PDF Report",
                pdf_bytes,
                file_name=f"dermalscan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
        else:
            st.markdown(
                "<div class='apple-text'>PDF report requires the reportlab package.</div>",
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("⬆ Please upload or capture an image to start analysis")
