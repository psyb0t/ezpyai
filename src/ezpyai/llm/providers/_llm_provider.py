import json
from abc import ABC, abstractmethod
from typing import Union, Dict, List, Any

from ezpyai.llm.prompt import Prompt
from ezpyai.llm.providers.exceptions import JSONParseError


_STRUCTURED_RESPONSE_OUTPUT_INSTRUCTIONS = (
    "Output instructions: your output must be JSON-formatted similar to the following:"
)


class LLMProvider(ABC):
    @abstractmethod
    def get_response(self, prompt: Prompt) -> str:
        pass

    @abstractmethod
    def get_structured_response(
        self, prompt: Prompt, response_format: Union[List, Dict]
    ) -> Union[List, Dict]:
        pass


class BaseLLMProvider(LLMProvider):
    """
    Base class for LLM providers.
    """

    @abstractmethod
    def get_response(self, _: Prompt) -> str:
        """
        Get the response for the given prompt.

        Args:
            prompt (Prompt): The input prompt.

        Returns:
            str: The response.
        """

        return ""

    def _validate_response_format(
        self, data: Any, response_format: Union[Dict, List]
    ) -> bool:
        """
        Validate the response format.

        Args:
            data (Any): The data to validate.
            response_format (Union[Dict, List]): The response format.

        Returns:
            bool: True if the response format is valid, False otherwise.
        """

        if not response_format:
            return True
        if isinstance(response_format, dict):
            if not isinstance(data, dict):
                return False

            return all(key in data for key, _ in response_format.items())

        if isinstance(response_format, list):
            if not isinstance(data, list):
                return False

            return all(
                self._validate_response_format(item, spec)
                for item, spec in zip(data, response_format)
            )

    def remove_artifacts(self, response: str) -> str:
        """
        Remove artifacts from the response.

        Args:
            response (str): The response to remove artifacts from.

        Returns:
            str: The response without artifacts.
        """

        artifacts = ["```json", "```"]
        for artifact in artifacts:
            response = response.replace(artifact, "")

        return response

    def get_structured_response(
        self, prompt: Prompt, response_format: Union[List, Dict]
    ) -> Union[List, Dict]:
        """
        Get the structured response for the given prompt.

        Args:
            prompt (Prompt): The input prompt.
            response_format (Union[Dict, List]): The response format.

        Returns:
            Union[List, Dict]: The structured response.

        Raises:
            JSONParseError: If the response cannot be parsed as JSON.
        """

        prompt = Prompt(
            user_message=prompt.get_user_message(),
            context=prompt.get_context(),
            system_message=f"{prompt.get_system_message()}. {_STRUCTURED_RESPONSE_OUTPUT_INSTRUCTIONS} {json.dumps(response_format)}",
        )

        response = self.remove_artifacts(self.get_response(prompt)).strip()

        try:
            structured_resp = json.loads(response)
        except:
            raise JSONParseError(f"Failed to parse structured response: {response}")

        if self._validate_response_format(structured_resp, response_format):
            return structured_resp

        return None
