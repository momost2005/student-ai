from dataclasses import dataclass

from pypdf import PdfReader


@dataclass
class PDFPage:
    page_number: int
    text: str


@dataclass
class PDFDocument:
    file_name: str
    page_count: int
    pages: list[PDFPage]


class PDFDocumentProcessor:

    def extract(self, file_path: str) -> PDFDocument:

        reader = PdfReader(file_path)

        pages: list[PDFPage] = []

        for index, page in enumerate(reader.pages):

            text = page.extract_text() or ""

            pages.append(
                PDFPage(
                    page_number=index + 1,
                    text=text
                )
            )

        return PDFDocument(
            file_name=file_path,
            page_count=len(reader.pages),
            pages=pages
        )