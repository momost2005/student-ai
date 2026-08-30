from app.ai.registry import AIProviderRegistry
from app.ai.settings import AISettings


class AIGateway:

    def __init__(
        self,
        registry: AIProviderRegistry,
        settings: AISettings
    ):
        self.registry = registry
        self.settings = settings

    def generate(self, prompt: str) -> str:
        provider = self.registry.get(
            self.settings.active_provider
        )

        return provider.generate(prompt)