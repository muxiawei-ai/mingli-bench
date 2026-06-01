"""
OpenAI model client implementation.
"""

import os
from typing import Optional
from openai import OpenAI

from .base import ModelClient
from .message_utils import describe_chat_response, extract_chat_message_text
from ..utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIClient(ModelClient):
    """Client for OpenAI models (GPT-3.5, GPT-4, etc.)"""
    
    def __init__(self, 
                 model_name: str = "gpt-4",
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 temperature: float = 0.0,
                 max_tokens: Optional[int] = None,
                 **kwargs):
        """
        Initialize OpenAI client.
        
        Args:
            model_name: Model to use (e.g., "gpt-4", "gpt-3.5-turbo")
            api_key: OpenAI API key (if not set, uses environment variable)
            base_url: Custom API base URL
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional configuration
        """
        # Initialize parent with API key handling
        super().__init__(
            model_name=model_name,
            api_key=api_key,
            api_key_env_vars=["OPENAI_API_KEY"],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Initialize client with timeout
        timeout_seconds = int(os.getenv("TIMEOUT", "30"))
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.reasoning_effort = os.getenv("OPENROUTER_REASONING_EFFORT")
        self.reasoning_exclude = _env_bool("OPENROUTER_REASONING_EXCLUDE")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=timeout_seconds
        )
        
        logger.info(f"Initialized OpenAI client with model: {model_name}, timeout: {timeout_seconds}s")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate response using OpenAI API.
        
        Args:
            prompt: Input prompt
            **kwargs: Override generation parameters
            
        Returns:
            Generated text
        """
        try:
            # Get parameters with overrides using base class method
            gen_params = self.get_generation_params(**kwargs)
            
            # Build API call parameters
            params = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                **gen_params
            }
            extra_body = self._extra_body()
            if extra_body:
                params["extra_body"] = extra_body
            
            logger.debug(f"Making API call with model: {params['model']}")
            
            # Make API call
            response = self.client.chat.completions.create(**params)
            
            # Extract text
            choice = response.choices[0]
            try:
                text = extract_chat_message_text(choice.message)
            except ValueError as error:
                detail = describe_chat_response(response)
                raise ValueError(
                    f"OpenAI-compatible response did not include text content: {detail}"
                ) from error
            
            return text
            
        except Exception as e:
            self.handle_api_error("OpenAI generation", e)
            raise
    
    def validate_api_key(self) -> bool:
        """
        Validate OpenAI API key.
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # Try a simple API call
            self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"Invalid OpenAI API key: {e}")
            return False

    def _extra_body(self) -> dict:
        """Build provider-specific OpenRouter extras from environment settings."""

        if not self._uses_openrouter():
            return {}
        reasoning = {}
        if self.reasoning_effort:
            reasoning["effort"] = self.reasoning_effort
        if self.reasoning_exclude is not None:
            reasoning["exclude"] = self.reasoning_exclude
        return {"reasoning": reasoning} if reasoning else {}

    def _uses_openrouter(self) -> bool:
        return bool(self.base_url and "openrouter.ai" in self.base_url)


def _env_bool(name: str) -> Optional[bool]:
    value = os.getenv(name)
    if value is None:
        return None
    return value.strip().lower() in {"1", "true", "yes", "on"}
