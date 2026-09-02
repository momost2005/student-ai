from abc import ABC, abstractmethod


class DocumentExtractionProvider(ABC):

    @abstractmethod
    def extract_page(
        self,
        image_path: str,
        model: str | None = None
    ) -> str:
        pass