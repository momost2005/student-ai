from app.ai.base import AIProvider


class MockAIProvider(AIProvider):

    def generate(self, prompt: str) -> str:
        return f"Mock AI response for: {prompt}"