from abc import ABC, abstractmethod

from app.documents.extraction_models import (
    ExtractedPage
)


class DocumentExtractionProvider(ABC):

    @abstractmethod
    def extract_page(
        self,
        image_path: str,
        page_number: int,
        model: str | None = None
    ) -> ExtractedPage:
        pass