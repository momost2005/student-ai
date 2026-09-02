import base64
import mimetypes
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.documents.extraction_base import (
    DocumentExtractionProvider
)


load_dotenv()


class OpenAIExtractionProvider(
    DocumentExtractionProvider
):

    def __init__(self):
        self.api_key = os.getenv(
            "OPENAI_API_KEY"
        )

    def _image_to_data_url(
        self,
        image_path: str
    ) -> str:

        mime_type, _ = mimetypes.guess_type(
            image_path
        )

        if not mime_type:
            mime_type = "image/png"

        with open(image_path, "rb") as file:
            encoded = base64.b64encode(
                file.read()
            ).decode("utf-8")

        return (
            f"data:{mime_type};base64,{encoded}"
        )

    def extract_page(
        self,
        image_path: str,
        model: str | None = None
    ) -> str:

        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured"
            )

        if not model:
            raise ValueError(
                "Extraction model is not configured"
            )

        client = OpenAI(
            api_key=self.api_key
        )

        image_data_url = (
            self._image_to_data_url(
                image_path
            )
        )

        prompt = """
Extract this mathematics textbook page into clean Markdown.

Requirements:
- Preserve the natural reading order.
- Preserve all headings and section titles.
- Preserve question numbers.
- Preserve mathematical expressions exactly.
- Represent fractions and equations using LaTeX where useful.
- Keep examples, practice questions, and review sections separate.
- Do not solve any exercise.
- Do not add explanations or information that are not visible on the page.
- Ignore decorative elements when they do not contain educational content.
"""

        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        },
                        {
                            "type": "input_image",
                            "image_url":
                                image_data_url
                        }
                    ]
                }
            ]
        )

        return response.output_text