from app.ai.base import AIProvider
from app.ai.providers.mock import MockAIProvider


class AIGateway:

    def __init__(self):
        self.provider: AIProvider = MockAIProvider()

    def generate(self, prompt: str) -> str:
        return self.provider.generate(prompt)