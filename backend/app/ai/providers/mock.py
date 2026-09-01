from app.ai.base import AIProvider


class MockAIProvider(AIProvider):

    def generate(
        self,
        prompt: str,
        model: str | None = None
    ) -> str:

        return f"Mock AI response for: {prompt}"