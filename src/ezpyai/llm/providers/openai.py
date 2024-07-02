import os
import ezpyai.llm.exceptions as exceptions

from typing import Annotated
from openai import OpenAI as _OpenAI
from ezpyai._logger import logger
from ezpyai.llm.providers._llm_provider import BaseLLMProvider
from ezpyai.llm.prompt import Prompt

from ezpyai._constants import (
    ENV_VAR_NAME_OPENAI_API_KEY,
    ENV_VAR_NAME_OPENAI_ORGANIZATION,
    ENV_VAR_NAME_OPENAI_PROJECT,
)


# Constants for OpenAI GPT models with context window sizes and specific versions
MODEL_GPT_4O: str = (
    "gpt-4o-2024-05-13"  # context window = 128,000 tokens, trained up to Oct 2023
)
MODEL_GPT_4_TURBO: str = (
    "gpt-4-turbo-2024-04-09"  # context window = 128,000 tokens, trained up to Dec 2023
)
MODEL_GPT_4_TURBO_PREVIEW: str = (
    "gpt-4-0125-preview"  # context window = 128,000 tokens, trained up to Dec 2023
)
MODEL_GPT_4_1106_PREVIEW: str = (
    "gpt-4-1106-preview"  # context window = 128,000 tokens, trained up to Apr 2023
)
MODEL_GPT_4_VISION_PREVIEW: str = (
    "gpt-4-1106-vision-preview"  # context window = 128,000 tokens, trained up to Apr 2023, to be deprecated Dec 2024
)
MODEL_GPT_4: str = "gpt-4-0613"  # context window = 8,192 tokens, trained up to Sep 2021
MODEL_GPT_4_32K: str = (
    "gpt-4-32k-0613"  # context window = 32,768 tokens, trained up to Sep 2021, to be deprecated June 2025
)
MODEL_GPT_3_5_TURBO: str = (
    "gpt-3.5-turbo-0125"  # context window = 16,385 tokens, trained up to Sep 2021
)
MODEL_GPT_3_5_TURBO_1106: str = (
    "gpt-3.5-turbo-1106"  # context window = 16,385 tokens, trained up to Sep 2021
)
MODEL_GPT_3_5_TURBO_INSTRUCT: str = (
    "gpt-3.5-turbo-instruct"  # context window = 4,096 tokens, trained up to Sep 2021
)
MODEL_GPT_3_5_TURBO_16K: str = (
    "gpt-3.5-turbo-16k-0613"  # context window = 16,385 tokens, trained up to Sep 2021, to be deprecated June 2024
)

_DEFAULT_MODEL: str = MODEL_GPT_3_5_TURBO
_DEFAULT_TEMPERATURE: float = 0.7
_DEFAULT_MAX_TOKENS: int = 150


class LLMProviderOpenAI(BaseLLMProvider):

    def __init__(
        self,
        model: str = _DEFAULT_MODEL,
        temperature: float = _DEFAULT_TEMPERATURE,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
        api_key: str = None,
        organization: str = None,
        project: str = None,
    ) -> None:
        if api_key is None:
            api_key = os.getenv(ENV_VAR_NAME_OPENAI_API_KEY)

        if organization is None:
            organization = os.getenv(ENV_VAR_NAME_OPENAI_ORGANIZATION)

        if project is None:
            project = os.getenv(ENV_VAR_NAME_OPENAI_PROJECT)

        self._client = _OpenAI(
            api_key=api_key,
            organization=organization,
            project=project,
        )

        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(model={self._model}, temperature={self._temperature}, max_tokens={self._max_tokens})"

    def _get_system_message(self, message: str) -> dict:
        return {"role": "system", "content": message}

    def _get_user_message(self, message: str) -> dict:
        return {"role": "user", "content": message}

    def _prompt_to_messages(
        self, prompt: Prompt
    ) -> Annotated[list[dict], "Raises exceptions.NoUserMessage"]:
        messages = []
        if prompt.has_system_message():
            messages.append(self._get_system_message(prompt.get_system_message()))

        if prompt.has_context():
            messages.append(self._get_user_message(prompt.get_context_as_string()))

        if not prompt.has_user_message():
            raise exceptions.NoUserMessage()

        messages.append(self._get_user_message(prompt.get_user_message()))

        return messages

    def get_response(self, prompt: Prompt) -> Annotated[
        str,
        "Raises exceptions.NoUserMessage, exceptions.NoLLMResponseMessage, exceptions.InvokeError",
    ]:
        messages = self._prompt_to_messages(prompt)

        try:
            logger.debug(f"Sending messages: {messages} to model {self._model}")

            response = self._client.chat.completions.create(
                model=self._model,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
                messages=messages,
            )
        except Exception as e:
            raise exceptions.InvokeError() from e

        if not response.choices:
            raise exceptions.NoLLMResponseMessage()

        return response.choices[0].message.content
