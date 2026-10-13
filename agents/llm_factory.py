"""Deterministic demo responder. Remote LLM providers are not implemented."""
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Ottawa Ankle Knee Rules"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return (
            f"[{self.system_name} demonstration]: This mock interface does not "
            "interpret clinical evidence or validate the query. "
            "Use the dedicated Ottawa clinical criteria evaluator for imaging decisions."
        )


class LLMFactory:
    @staticmethod
    def create(provider: str = "mock", system_name: str = "Ottawa Ankle Knee Rules"):
        prov = str(provider).lower()
        if prov in {"mock", "deterministic", "test"}:
            return MockLLM(system_name)
        raise ValueError(f"Model provider {provider!r} is not implemented. Use 'mock'.")
