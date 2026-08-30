from app.ai.base import AIProvider
from app.ai.providers.mock import MockAIProvider
from app.ai.providers.mock_secondary import SecondaryMockAIProvider
from app.ai.providers.openai_provider import OpenAIProvider


class AIProviderRegistry:

    def __init__(self):
        self._providers: dict[str, AIProvider] = {}
        self.register("mock",MockAIProvider())
        self.register("mock-secondary",SecondaryMockAIProvider())
        self.register("openai",OpenAIProvider())

    def register(self, name: str, provider: AIProvider):
        self._providers[name] = provider

    def get(self, name: str) -> AIProvider:
        if name not in self._providers:
            raise ValueError(f"AI provider '{name}' is not registered")

        return self._providers[name]

    def names(self) -> list[str]:
        return list(self._providers.keys())