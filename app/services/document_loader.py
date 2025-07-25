from fastapi import UploadFile
from docx import Document
from fitz import open as fitz_open  # alias to avoid shadowing built-in `open`
import tempfile
import os

async def load_document(file: UploadFile) -> str:
    contents = await file.read()
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(contents)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(contents)
    else:
        return contents.decode()

def extract_text_from_pdf(data: bytes) -> str:
    doc = fitz_open(stream=data, filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

def extract_text_from_docx(data: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    doc = Document(tmp_path)
    text = "\n".join([para.text for para in doc.paragraphs])

    os.remove(tmp_path)  # optional: clean up temp file
    return text
