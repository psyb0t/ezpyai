import requests

from typing import List, Dict, Any, Optional, Union

from ezpyai.constants import (
    HTTP_METHOD_GET,
    HTTP_METHOD_POST,
    HTTP_CONTENT_TYPE_JSON,
    HTTP_HEADER_CONTENT_TYPE,
    HTTP_HEADER_AUTHORIZATION,
)

from ezpyai._logger import logger


class HTTPClientTextGenerationWebUI:
    """
    A client for interacting with Text Generation Web UI's internal API endpoints.
    """

    # Endpoint constants
    _ENDPOINT_ENCODE = "/v1/internal/encode"
    _ENDPOINT_DECODE = "/v1/internal/decode"
    _ENDPOINT_TOKEN_COUNT = "/v1/internal/token-count"
    _ENDPOINT_LOGITS = "/v1/internal/logits"
    _ENDPOINT_CHAT_PROMPT = "/v1/internal/chat-prompt"
    _ENDPOINT_STOP_GENERATION = "/v1/internal/stop-generation"
    _ENDPOINT_MODEL_INFO = "/v1/internal/model/info"
    _ENDPOINT_MODEL_LIST = "/v1/internal/model/list"
    _ENDPOINT_MODEL_LOAD = "/v1/internal/model/load"
    _ENDPOINT_MODEL_UNLOAD = "/v1/internal/model/unload"
    _ENDPOINT_LORA_LIST = "/v1/internal/lora/list"
    _ENDPOINT_LORA_LOAD = "/v1/internal/lora/load"
    _ENDPOINT_LORA_UNLOAD = "/v1/internal/lora/unload"

    def __init__(self, base_url: str, api_key: str):
        """
        Initialize the API client.

        Args:
            base_url (str): The base URL of the API.
            api_key (str): The API key for authentication.
        """

        logger.debug(
            f"Initializing HTTPClientTextGenerationWebUI with base_url={base_url}"
        )

        self.base_url = base_url
        self.headers = {
            HTTP_HEADER_AUTHORIZATION: f"Bearer {api_key}",
            HTTP_HEADER_CONTENT_TYPE: HTTP_CONTENT_TYPE_JSON,
        }

    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Make an HTTP request to the API.

        Args:
            method (str): The HTTP method (GET, POST, etc.).
            endpoint (str): The API endpoint.
            data (Optional[Dict[str, Any]]): The request payload (for POST requests).

        Returns:
            Any: The JSON response from the API.
        """

        logger.debug(f"Making request to {self.base_url}{endpoint} with data={data}")

        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=self.headers, json=data)

        logger.debug(
            f"""Response:
Status: {response.status_code}
Content: {response.content}
"""
        )

        response.raise_for_status()

        return response.json()

    def encode_tokens(self, text: str) -> Dict[str, Union[List[int], int]]:
        """
        Encode text into tokens.

        Args:
            text (str): The text to encode.

        Returns:
            Dict[str, Union[List[int], int]]: A dictionary containing the tokens and token count.
        """

        return self._make_request(
            HTTP_METHOD_POST, self._ENDPOINT_ENCODE, {"text": text}
        )

    def decode_tokens(self, tokens: List[int]) -> Dict[str, str]:
        """
        Decode tokens back into text.

        Args:
            tokens (List[int]): The list of tokens to decode.

        Returns:
            Dict[str, str]: A dictionary containing the decoded text.
        """

        return self._make_request(
            HTTP_METHOD_POST, self._ENDPOINT_DECODE, {"tokens": tokens}
        )

    def count_tokens(self, text: str) -> Dict[str, int]:
        """
        Count the number of tokens in the given text.

        Args:
            text (str): The text to count tokens for.

        Returns:
            Dict[str, int]: A dictionary containing the token count.
        """

        return self._make_request(
            HTTP_METHOD_POST, self._ENDPOINT_TOKEN_COUNT, {"text": text}
        )

    def get_logits(self, prompt: str, **kwargs: Any) -> Dict[str, Dict[str, float]]:
        """
        Get the logits for the given prompt.

        Args:
            prompt (str): The input prompt.
            **kwargs (Any): Additional parameters for the logits calculation.

        Returns:
            Dict[str, Dict[str, float]]: A dictionary containing the logits.
        """

        data = {"prompt": prompt, **kwargs}

        return self._make_request(HTTP_METHOD_POST, self._ENDPOINT_LOGITS, data)

    def get_chat_prompt(
        self, messages: List[Dict[str, Any]], **kwargs: Any
    ) -> Dict[str, str]:
        """
        Generate a chat prompt from the given messages.

        Args:
            messages (List[Dict[str, Any]]): A list of message dictionaries.
            **kwargs (Any): Additional parameters for prompt generation.

        Returns:
            Dict[str, str]: A dictionary containing the generated prompt.
        """

        data = {"messages": messages, **kwargs}

        return self._make_request(HTTP_METHOD_POST, self._ENDPOINT_CHAT_PROMPT, data)

    def stop_generation(self) -> str:
        """
        Stop the current text generation process.

        Returns:
            str: A string indicating the result of the operation.
        """

        return self._make_request(HTTP_METHOD_POST, self._ENDPOINT_STOP_GENERATION)

    def get_model_info(self) -> Dict[str, Union[str, List[str]]]:
        """
        Get information about the currently loaded model.

        Returns:
            Dict[str, Union[str, List[str]]]: A dictionary containing model information.
        """

        return self._make_request(HTTP_METHOD_GET, self._ENDPOINT_MODEL_INFO)

    def list_models(self) -> List[str]:
        """
        Get a list of available models.

        Returns:
            List[str]: A list of model names.
        """

        return self._make_request(HTTP_METHOD_GET, self._ENDPOINT_MODEL_LIST)[
            "model_names"
        ]

    def load_model(
        self,
        model_name: str,
        args: Optional[Dict[str, Any]] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Load a specific model.

        Args:
            model_name (str): The name of the model to load.
            args (Optional[Dict[str, Any]]): Optional arguments for model loading.
            settings (Optional[Dict[str, Any]]): Optional settings for the model.

        Returns:
            str: A string indicating the result of the operation.
        """

        data = {
            "model_name": model_name,
            "args": args or {},
            "settings": settings or {},
        }

        return self._make_request(HTTP_METHOD_POST, self._ENDPOINT_MODEL_LOAD, data)

    def unload_model(self) -> str:
        """
        Unload the currently loaded model.

        Returns:
            str: A string indicating the result of the operation.
        """

        return self._make_request(HTTP_METHOD_POST, self._ENDPOINT_MODEL_UNLOAD)

    def list_loras(self) -> List[str]:
        """
        Get a list of available LoRA adapters.

        Returns:
            List[str]: A list of LoRA adapter names.
        """

        return self._make_request(HTTP_METHOD_GET, self._ENDPOINT_LORA_LIST)[
            "lora_names"
        ]

    def load_loras(self, loras: List[str]) -> str:
        """
        Load specific LoRA adapters.

        Args:
            loras (List[str]): A list of LoRA adapter names to load.

        Returns:
            str: A string indicating the result of the operation.
        """

        return self._make_request(
            HTTP_METHOD_POST, self._ENDPOINT_LORA_LOAD, {"lora_names": loras}
        )

    def unload_loras(self) -> str:
        """
        Unload all currently loaded LoRA adapters.

        Returns:
            str: A string indicating the result of the operation.
        """

        return self._make_request(HTTP_METHOD_POST, self._ENDPOINT_LORA_UNLOAD)
