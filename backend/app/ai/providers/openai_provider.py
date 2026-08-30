import os

from dotenv import load_dotenv
from openai import OpenAI

from app.ai.base import AIProvider


load_dotenv()


class OpenAIProvider(AIProvider):

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv(
            "OPENAI_MODEL",
            "gpt-5.4-mini"
        )

    def generate(self, prompt: str) -> str:

        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured"
            )

        client = OpenAI(
            api_key=self.api_key
        )

        response = client.responses.create(
            model=self.model,
            input=prompt
        )

        return response.output_text