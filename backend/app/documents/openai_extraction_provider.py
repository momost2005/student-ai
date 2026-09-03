import base64
import json
import mimetypes
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.documents.extraction_base import (
    DocumentExtractionProvider
)

from app.documents.extraction_models import (
    ExtractedPage
)


load_dotenv()


class OpenAIExtractionProvider(
    DocumentExtractionProvider
):

    def make_schema_strict(
    self,
    schema: dict
    ) -> dict:

        if schema.get("type") == "object":

            schema["additionalProperties"] = False

            properties = schema.get(
                "properties",
                {}
            )

            if properties:
                schema["required"] = list(
                    properties.keys()
                )

        for value in schema.values():

            if isinstance(value, dict):
                self.make_schema_strict(value)

            elif isinstance(value, list):

                for item in value:

                    if isinstance(item, dict):
                        self.make_schema_strict(item)

        return schema

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

        with open(
            image_path,
            "rb"
        ) as file:

            encoded = base64.b64encode(
                file.read()
            ).decode("utf-8")

        return (
            f"data:{mime_type};"
            f"base64,{encoded}"
        )


    def extract_page(
        self,
        image_path: str,
        page_number: int,
        model: str | None = None
    ) -> ExtractedPage:

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

        schema = self.make_schema_strict(
            ExtractedPage.model_json_schema()
        )

        prompt = f"""
You are extracting structured educational content
from a mathematics textbook page.

This is PDF page number {page_number}.

Rules:
- Preserve reading order.
- Preserve headings.
- Preserve mathematical expressions exactly.
- Use LaTeX in math_expression when useful.
- Do not solve exercises.
- Do not add information that is not visible.
- Ignore decorative elements.
- Use one of the allowed page types.
- Return every field defined by the schema.
- If a nullable value is not present, return null.
- Never omit any field.

Question extraction rules:
- For practice, review, assessment, and exercise sections, extract every distinct exercise or problem into the questions array.
- Do not combine multiple exercises into one question.
- The content field should contain only section instructions or explanatory text, not the individual exercises.
- Preserve the visible question number in number. If no number is visible, return null.
- Put the full question wording in text.
- Put the mathematical expression in math_expression when applicable.
- If a section contains no exercises, return an empty questions array.
"""

        response = client.responses.create(
            model=model,

            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type":
                                "input_text",
                            "text":
                                prompt
                        },
                        {
                            "type":
                                "input_image",
                            "image_url":
                                image_data_url
                        }
                    ]
                }
            ],

            text={
                "format": {
                    "type":
                        "json_schema",

                    "name":
                        "curriculum_page",

                    "schema":
                        schema,

                    "strict":
                        True
                }
            }
        )

        parsed_json = json.loads(
            response.output_text
        )

        return ExtractedPage.model_validate(
            parsed_json
        )

    