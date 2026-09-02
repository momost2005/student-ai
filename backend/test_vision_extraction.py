from pathlib import Path

from app.documents.openai_extraction_provider import (
    OpenAIExtractionProvider
)


project_root = Path(__file__).resolve().parent.parent

image_path = (
    project_root
    / "curriculum"
    / "processed"
    / "page_5.png"
)


extractor = OpenAIExtractionProvider()

result = extractor.extract_page(
    image_path=str(image_path),
    model="gpt-5.6-luna"
)

print(result)