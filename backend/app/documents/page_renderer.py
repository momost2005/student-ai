from pathlib import Path

import pymupdf


class PDFPageRenderer:

    def render_page(
        self,
        pdf_path: str,
        page_number: int,
        output_path: str,
        zoom: float = 2.0
    ) -> str:

        document = pymupdf.open(pdf_path)

        page_index = page_number - 1

        if page_index < 0 or page_index >= len(document):
            raise ValueError(
                f"Page {page_number} is outside PDF range"
            )

        page = document[page_index]

        matrix = pymupdf.Matrix(zoom, zoom)

        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False
        )

        output_file = Path(output_path)
        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        pixmap.save(str(output_file))

        document.close()

        return str(output_file)