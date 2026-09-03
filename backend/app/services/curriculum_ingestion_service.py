import json

from sqlalchemy.orm import Session

from app.documents.openai_extraction_provider import (
    OpenAIExtractionProvider
)

from app.documents.page_renderer import (
    PDFPageRenderer
)

from app.repositories.curriculum_repository import (
    CurriculumRepository
)


class CurriculumIngestionService:

    def __init__(self):

        self.renderer = PDFPageRenderer()

        self.extractor = OpenAIExtractionProvider()

        self.repository = CurriculumRepository()


    def process_page(
        self,
        db: Session,
        document_id: int,
        pdf_path: str,
        page_number: int,
        image_output_path: str,
        extraction_model: str
    ):

        document = self.repository.get_document(
            db,
            document_id
        )

        if not document:
            raise ValueError(
                f"Curriculum document "
                f"{document_id} was not found"
            )

        # 1. Render PDF page to image
        image_path = self.renderer.render_page(
            pdf_path=pdf_path,
            page_number=page_number,
            output_path=image_output_path,
            zoom=2.0
        )

        # 2. Extract structured content using Vision AI
        extracted_page = self.extractor.extract_page(
            image_path=image_path,
            page_number=page_number,
            model=extraction_model
        )

        # 3. Keep original structured JSON for audit/debugging
        raw_json = json.dumps(
            extracted_page.model_dump(),
            ensure_ascii=False,
            indent=2
        )

        # 4. Save/update page
        page = self.repository.save_page(
            db=db,
            document_id=document_id,
            page_number=page_number,
            page_type=extracted_page.page_type,
            raw_extracted_content=raw_json
        )

        # 5. Save normalized sections
        self.repository.replace_sections(
            db=db,
            page=page,
            sections=extracted_page.sections
        )

        return page