from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Type
from openai import OpenAI
from ollama import chat as ollama_chat
from pydantic import BaseModel

from ..config import LLMConfig

T = TypeVar("T", bound=BaseModel)


class LLMClient(ABC):
    @abstractmethod
    def chat(self, model: str, messages: list[dict], **kwargs) -> str:
        """Send a chat request and return the response content."""
        pass

    @abstractmethod
    def parse(self, model: str, messages: list[dict], response_model: Type[T], **kwargs) -> T:
        """Send a chat request and return a validated Pydantic model instance."""
        pass


class OllamaClient(LLMClient):
    def chat(self, model: str, messages: list[dict], **kwargs) -> str:
        response = ollama_chat(model=model, messages=messages, **kwargs)
        return response.message.content

    def parse(self, model: str, messages: list[dict], response_model: Type[T], **kwargs) -> T:
        response = ollama_chat(
            model=model,
            messages=messages,
            format=response_model.model_json_schema(),
            **kwargs,
        )
        return response_model.model_validate_json(response.message.content)


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

    def parse(self, model: str, messages: list[dict], response_model: Type[T], **kwargs) -> T:
        response = self._client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=response_model,
            **kwargs,
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise ValueError("LLM structured output returned None")
        return parsed


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
