import os

from openai import OpenAI
from typing import List

from ezpyai.constants import (
    ENV_VAR_NAME_TEXT_GENERATION_WEBUI_API_KEY,
    ENV_VAR_NAME_TEXT_GENERATION_WEBUI_BASE_URL,
)

from ezpyai.exceptions import UnsupportedModelError, UnsupportedLoraError

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

    Args:
        model (str): The model to use.
        loras (List[str] | None): The loras to use.
        base_url (str | None): The base URL of the API.
        api_key (str | None): The API key for authentication.
        temperature (float): The temperature to use.
        max_tokens (int): The maximum number of tokens to generate.

    Raises:
        UnsupportedModelError: If the model is not supported.
        UnsupportedLoraError: If any of the loras is not supported.
    """

    def __init__(
        self,
        model: str,
        loras: List[str] | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        temperature: float = _DEFAULT_TEMPERATURE,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
    ) -> None:
        if base_url is None:
            base_url = os.getenv(ENV_VAR_NAME_TEXT_GENERATION_WEBUI_BASE_URL)

        if api_key is None:
            api_key = os.getenv(ENV_VAR_NAME_TEXT_GENERATION_WEBUI_API_KEY)

        self._client = OpenAI(
            base_url=f"{base_url}/v1",
            api_key=api_key,
        )

        self._internal_client = HTTPClientTextGenerationWebUI(
            base_url=base_url,
            api_key=api_key,
        )

        self._cleanup()

        self._ensure_model_available(model=model)
        self._ensure_loras_exist(loras=loras)

        self._internal_client.load_model(model_name=model)

        if loras:
            self._internal_client.load_loras(loras=loras)

        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens

    def _cleanup(self):
        """
        Cleanup any resources used by the LLM provider.
        """

        self._internal_client.unload_loras()
        self._internal_client.unload_model()

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

    def _ensure_loras_exist(self, loras: List[str]):
        """
        Ensure that the given loras exist.

        Args:
            loras (List[str]): The loras to check.

        Raises:
            UnsupportedModelError: If the loras are not available.
        """

        available_loras = self._internal_client.list_loras()

        for lora in loras:
            if lora not in available_loras:
                raise UnsupportedLoraError(
                    f"Lora {lora} not available. Available loras: {available_loras}"
                )
