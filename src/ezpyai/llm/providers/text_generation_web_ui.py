import os
from sys import api_version

import openai
from openai import OpenAI
from ezpyai._constants import (
    _ENV_VAR_NAME_TEXT_GENERATION_WEBUI_API_KEY,
    _ENV_VAR_NAME_TEXT_GENERATION_WEBUI_BASE_URL,
)
from ezpyai.llm.providers.openai import (
    LLMProviderOpenAI,
    _DEFAULT_TEMPERATURE,
    _DEFAULT_MAX_TOKENS,
)


class LLMProviderTextGenerationWebUI(LLMProviderOpenAI):
    """
    LLM provider for Text Generation Web UI's OpenAI compatible API.
    """

    def __init__(
        self,
        model: str,
        base_url: str = os.getenv(_ENV_VAR_NAME_TEXT_GENERATION_WEBUI_BASE_URL),
        temperature: float = _DEFAULT_TEMPERATURE,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
        api_key: str = os.getenv(_ENV_VAR_NAME_TEXT_GENERATION_WEBUI_API_KEY),
    ) -> None:
        openai.api_version = "2023-05-15"
        self._client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
