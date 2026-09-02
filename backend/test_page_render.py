from pathlib import Path

from app.documents.page_renderer import PDFPageRenderer


project_root = Path(__file__).resolve().parent.parent

pdf_path = (
    project_root
    / "curriculum"
    / "samples"
    / "grade6_math_term1.pdf"
)

output_path = (
    project_root
    / "curriculum"
    / "processed"
    / "page_5.png"
)


renderer = PDFPageRenderer()

result = renderer.render_page(
    pdf_path=str(pdf_path),
    page_number=5,
    output_path=str(output_path),
    zoom=2.0
)

print(f"Image created: {result}")