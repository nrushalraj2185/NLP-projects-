import fitz  # PyMuPDF
import docx
import io
from PIL import Image
import pytesseract

def extract_text(file_bytes, filename):
    if filename.lower().endswith(".pdf"):
        return _extract_from_pdf(file_bytes)
    elif filename.lower().endswith(".docx"):
        return _extract_from_docx(file_bytes)
    elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return _extract_from_image(file_bytes)
    return ""

def _extract_from_pdf(file_bytes):
    text = ""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page in doc:
        text += page.get_text()
    return text

def _extract_from_docx(file_bytes):
    text = ""
    doc = docx.Document(io.BytesIO(file_bytes))
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def _extract_from_image(file_bytes):
    image = Image.open(io.BytesIO(file_bytes))
    return pytesseract.image_to_string(image)
