from pathlib import Path

from app.documents.pdf_processor import PDFDocumentProcessor


project_root = Path(__file__).resolve().parent.parent

pdf_path = (
    project_root
    / "curriculum"
    / "samples"
    / "grade6_math_term1.pdf"
)


processor = PDFDocumentProcessor()

document = processor.extract(
    str(pdf_path)
)


print(f"File: {document.file_name}")
print(f"Pages: {document.page_count}")


for page in document.pages[:5]:

    print()
    print("=" * 80)
    print(f"PAGE {page.page_number}")
    print("=" * 80)

    print(page.text[:1500])