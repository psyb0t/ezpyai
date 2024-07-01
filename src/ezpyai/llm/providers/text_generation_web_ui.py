import os

from openai import OpenAI
from typing import List

from ezpyai._constants import (
    ENV_VAR_NAME_TEXT_GENERATION_WEBUI_API_KEY,
    ENV_VAR_NAME_TEXT_GENERATION_WEBUI_BASE_URL,
)

from ezpyai.llm.providers.exceptions import UnsupportedModelError

from ezpyai.llm.providers.openai import (
    LLMProviderOpenAI,
    _DEFAULT_TEMPERATURE,
    _DEFAULT_MAX_TOKENS,
)

from ezpyai.llm.providers._http_clients.text_generation_web_ui import (
    HTTPClientTextGenerationWebUI,
)


class LLMProviderTextGenerationWebUI(LLMProviderOpenAI):
    """
    LLM provider for Text Generation Web UI's OpenAI compatible API.
    """

    _loaded_model: str = None

    def __init__(
        self,
        model: str,
        base_url: str = None,
        api_key: str = None,
        temperature: float = _DEFAULT_TEMPERATURE,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
    ) -> None:
        if base_url is None:
            base_url = os.getenv(ENV_VAR_NAME_TEXT_GENERATION_WEBUI_BASE_URL)

        if api_key is None:
            api_key = os.getenv(ENV_VAR_NAME_TEXT_GENERATION_WEBUI_API_KEY)

        self._client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

        self._internal_client = HTTPClientTextGenerationWebUI(
            base_url=base_url,
            api_key=api_key,
        )

        self._ensure_model_available(model=model)

        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens

    def _ensure_model_available(self, model: str):
        """
        Ensure that the given model is available.

        Args:
            model (str): The model name to check.

        Raises:
            UnsupportedModelError: If the model is not available.
        """

        available_models = self._internal_client.list_models()

        if model not in available_models:
            raise UnsupportedModelError(
                f"Model {model} not available. Available models: {available_models}"
            )
