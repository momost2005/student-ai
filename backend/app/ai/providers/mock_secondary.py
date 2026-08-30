from app.ai.base import AIProvider


class SecondaryMockAIProvider(AIProvider):

    def generate(self, prompt: str) -> str:
        return f"Secondary Mock AI response for: {prompt}"