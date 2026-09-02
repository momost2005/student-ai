from dataclasses import dataclass

import fitz


@dataclass
class PDFPage:
    page_number: int
    text: str


@dataclass
class PDFDocument:
    file_name: str
    page_count: int
    pages: list[PDFPage]


class PyMuPDFDocumentProcessor:

    def extract(self, file_path: str) -> PDFDocument:

        pdf = fitz.open(file_path)

        pages: list[PDFPage] = []

        for index, page in enumerate(pdf):

            text = page.get_text(
                "text",
                sort=True
            )

            pages.append(
                PDFPage(
                    page_number=index + 1,
                    text=text
                )
            )

        return PDFDocument(
            file_name=file_path,
            page_count=len(pdf),
            pages=pages
        )