import json
from ezpyai.llm.prompt import Prompt
from typing import Union, Dict, List, Any


_STRUCTURED_RESPONSE_OUTPUT_INSTRUCTIONS = (
    "Output instructions: your output must be JSON-formatted similar to the following:"
)


class BaseLLM:
    _name: str = None

    def __init__(self, name: str) -> None:
        self._name = name

    def __str__(self) -> str:
        return f"_BaseLLM(name={self._name})"

    def get_response(self, _: Prompt) -> str:
        return ""

    def _validate_response_format(
        self, data: Any, response_format: Union[Dict, List]
    ) -> bool:
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

    def get_structured_response(
        self, prompt: Prompt, response_format: Union[List, Dict]
    ) -> Union[List, Dict]:
        prompt = Prompt(
            user_message=prompt.get_user_message(),
            context=prompt.get_context(),
            system_message=f"{prompt.get_system_message()}. {_STRUCTURED_RESPONSE_OUTPUT_INSTRUCTIONS} {json.dumps(response_format)}",
        )

        response = remove_artifacts(self.get_response(prompt)).strip()

        structured_resp = json.loads(response)
        if self._validate_response_format(structured_resp, response_format):
            return structured_resp

        return None


def remove_artifacts(response: str) -> str:
    artifacts = ["```json", "```"]
    for artifact in artifacts:
        response = response.replace(artifact, "")

    return response
