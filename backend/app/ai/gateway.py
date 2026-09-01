from sqlalchemy.orm import Session

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


    def generate(
        self,
        db: Session,
        prompt: str
    ) -> tuple[str, str | None, str]:

        provider_name = (
            self.settings.get_active_provider(db)
        )

        model_name = (
            self.settings.get_active_model(db)
        )

        provider = self.registry.get(
            provider_name
        )

        response = provider.generate(
            prompt=prompt,
            model=model_name
        )

        return (
            provider_name,
            model_name,
            response
        )