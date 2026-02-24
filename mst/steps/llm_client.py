from abc import ABC, abstractmethod
import os
from openai import OpenAI
from ollama import chat as ollama_chat


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


def get_llm_client() -> LLMClient:
    """Factory function to get the appropriate LLM client based on config."""
    provider = os.getenv("LLM_PROVIDER", "openai")
    if provider == "ollama":
        return OllamaClient()

    base_url = os.getenv("OPENAI_BASE_URL", "http://glm-flash.cluster:9999/v1")
    api_key = os.getenv("OPENAI_API_KEY", "not-needed")
    return OpenAIClient(base_url, api_key)
