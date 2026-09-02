from pathlib import Path

from app.documents.pymupdf_processor import (
    PyMuPDFDocumentProcessor
)


project_root = Path(__file__).resolve().parent.parent

pdf_path = (
    project_root
    / "curriculum"
    / "samples"
    / "grade6_math_term1.pdf"
)


processor = PyMuPDFDocumentProcessor()

document = processor.extract(
    str(pdf_path)
)


page = document.pages[4]


print(f"Total pages: {document.page_count}")

print()
print("=" * 80)
print(f"PAGE {page.page_number}")
print("=" * 80)

print(page.text)