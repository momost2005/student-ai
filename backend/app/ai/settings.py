class AISettings:

    def __init__(self):
        self._active_provider = "mock"

    @property
    def active_provider(self) -> str:
        return self._active_provider

    def set_active_provider(self, provider_name: str):
        self._active_provider = provider_name