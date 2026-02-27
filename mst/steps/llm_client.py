from abc import ABC, abstractmethod
from typing import Optional
from openai import OpenAI
from ollama import chat as ollama_chat

from ..config import LLMConfig


class LLMClient(ABC):
    @abstractmethod
    def chat(self, model: str, messages: list[dict], **kwargs) -> str:
        """Send a chat request and return the response content."""
        pass


class OllamaClient(LLMClient):
    def chat(self, model: str, messages: list[dict], **kwargs) -> str:
        response = ollama_chat(model=model, messages=messages, **kwargs)
        return response.message.content


class OpenAIClient(LLMClient):
    def __init__(self, base_url: str, api_key: str):
        self._client = OpenAI(base_url=base_url, api_key=api_key)

    def chat(self, model: str, messages: list[dict], **kwargs) -> str:
        response_format = kwargs.pop("response_format", None)
        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            **(kwargs if not response_format else {"response_format": response_format})
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("LLM returned None content")
        return content


def get_llm_client(config: Optional[LLMConfig] = None) -> LLMClient:
    """Factory function to get the appropriate LLM client based on config.

    Args:
        config: LLMConfig instance. If None, uses default LLMConfig values.
    """
    if config is None:
        config = LLMConfig()
    if config.provider == "ollama":
        return OllamaClient()
    return OpenAIClient(config.openai_base_url, config.openai_api_key)
