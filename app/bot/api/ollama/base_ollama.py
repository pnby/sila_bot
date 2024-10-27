from abc import ABC, abstractmethod
from typing import Optional, AsyncGenerator

from app.bot.config import available_llm_models


class BaseOllama(ABC):
    def __init__(self, prompt: str, model: available_llm_models = available_llm_models,
                 stream: bool = False, endpoint: str = "http://ollama:11434/api/generate",
                 system_prompt: Optional[str] = None, temperature: float = 0,
                 max_context: int = 32768, jsonify: bool = False):
        """
        Initialize the BaseLlama class.

        Args:
            prompt (str): The input prompt for the model.
            model (Literal["qwen2"], optional): The model to use. Defaults to "qwen2".
            stream (bool, optional): Whether to stream the response. Defaults to False.
            endpoint (str, optional): The API endpoint to send the request to. Defaults to "http://ollama:11434/api/generate".
            system_prompt (str, optional): System prompt for the model.
        """
        self.prompt = prompt
        self.model = model
        self.stream = stream
        self.endpoint = endpoint
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_context = max_context
        self.jsonify = jsonify
        self.response = None

    @abstractmethod
    async def send_request(self) -> None:
        """
        Send a request to the model.

        This method should be implemented by subclasses to send a request to the model
        and store the response in self.response.
        """

    @abstractmethod
    async def stream_response(self) -> AsyncGenerator[str, None]:
        """
        Stream the response from the model.

        This method should be implemented by subclasses to send a streaming request to the model
        and yield parts of the response as they are received.

        Yields:
            str: The next part of the response.
        """

    @abstractmethod
    def get_formatted_response(self) -> str:
        """
        Get the formatted response from the model.

        This method should be implemented by subclasses to format the response
        stored in self.response and return it as a string.

        Returns:
            str: The formatted response.
        """