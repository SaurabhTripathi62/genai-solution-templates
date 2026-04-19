"""
LLM Factory — single interface for all LLM providers.
Swap between GPT-4, Claude, and local models with one line.
"""

import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel


SUPPORTED_MODELS = {
    "gpt-4o": {"provider": "openai", "model_name": "gpt-4o"},
    "gpt-4-turbo": {"provider": "openai", "model_name": "gpt-4-turbo-preview"},
    "gpt-4o-mini": {"provider": "openai", "model_name": "gpt-4o-mini"},
    "gpt-3.5-turbo": {"provider": "openai", "model_name": "gpt-3.5-turbo"},
    "claude-3-opus": {"provider": "anthropic", "model_name": "claude-3-opus-20240229"},
    "claude-3-sonnet": {"provider": "anthropic", "model_name": "claude-3-sonnet-20240229"},
    "claude-3-haiku": {"provider": "anthropic", "model_name": "claude-3-haiku-20240307"},
}


class LLMFactory:
    """
    Create any supported LLM with a consistent interface.

    Usage:
        llm = LLMFactory.create("gpt-4o")
        llm = LLMFactory.create("claude-3-sonnet", temperature=0.3)
        response = llm.invoke("Your prompt here")
    """

    @staticmethod
    def create(
        model_key: str,
        temperature: float = 0.1,
        max_tokens: int = 1024,
        streaming: bool = False,
    ) -> BaseChatModel:

        if model_key not in SUPPORTED_MODELS:
            raise ValueError(
                f"Model '{model_key}' not supported.\n"
                f"Available models: {list(SUPPORTED_MODELS.keys())}"
            )

        config = SUPPORTED_MODELS[model_key]

        if config["provider"] == "openai":
            return ChatOpenAI(
                model=config["model_name"],
                temperature=temperature,
                max_tokens=max_tokens,
                streaming=streaming,
                api_key=os.getenv("OPENAI_API_KEY"),
            )

        elif config["provider"] == "anthropic":
            return ChatAnthropic(
                model=config["model_name"],
                temperature=temperature,
                max_tokens=max_tokens,
                streaming=streaming,
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )

        raise ValueError(f"Unknown provider: {config['provider']}")

    @staticmethod
    def list_models() -> list:
        return list(SUPPORTED_MODELS.keys())
