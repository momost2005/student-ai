from app.ai.base import AIProvider


class SecondaryMockAIProvider(AIProvider):

    def generate(
        self,
        prompt: str,
        model: str | None = None
    ) -> str:

        return f"Secondary Mock AI response for: {prompt}"