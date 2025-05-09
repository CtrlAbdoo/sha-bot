"""
OpenRouter API client for handling LLM API requests.
"""
import aiohttp
from typing import Dict, List, Any, Optional
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings


class OpenRouterError(Exception):
    """Exception for OpenRouter API errors"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"OpenRouter API error ({status_code}): {message}")


class OpenRouterClient:
    """Client for interacting with OpenRouter API"""
    
    @staticmethod
    async def check_status() -> bool:
        """
        Check if OpenRouter API is accessible
        
        Returns:
            True if accessible, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(settings.openrouter_status_url, timeout=5) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to OpenRouter: {e}")
            return False
    
    @staticmethod
    def _prepare_headers() -> Dict[str, str]:
        """
        Prepare headers for OpenRouter API request
        
        Returns:
            Dict of headers
        """
        return {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.render_url,
            "X-Title": "College Chatbot"
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, OpenRouterError)),
        reraise=True
    )
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model_id: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate completion from OpenRouter API
        
        Args:
            messages: List of messages in the conversation
            model_id: OpenRouter model ID
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (0.0-1.0)
            
        Returns:
            API response
            
        Raises:
            OpenRouterError: If the API request fails
        """
        headers = self._prepare_headers()
        payload = {
            "model": model_id,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        logger.debug(f"Request to model: {model_id}")
        logger.debug(f"Using API key: {settings.openrouter_api_key[:4]}...{settings.openrouter_api_key[-4:]}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    settings.openrouter_url,
                    headers=headers,
                    json=payload,
                    timeout=60
                ) as response:
                    response_text = await response.text()
                    logger.debug(f"OpenRouter response status: {response.status}")
                    
                    if response.status != 200:
                        error_msg = self._process_error_response(response.status, response_text)
                        raise OpenRouterError(response.status, error_msg)
                    
                    result = await response.json()
                    logger.debug(f"Tokens used: {result.get('usage', {}).get('total_tokens', 'unknown')}")
                    
                    return result
        except aiohttp.ClientError as e:
            logger.error(f"Connection error with OpenRouter API: {e}")
            raise
    
    @staticmethod
    def _process_error_response(status_code: int, response_text: str) -> str:
        """
        Process error response from OpenRouter
        
        Args:
            status_code: HTTP status code
            response_text: Response text
            
        Returns:
            Processed error message
        """
        response_lower = response_text.lower()
        
        if status_code == 401:
            if "no auth credentials found" in response_lower:
                return "Authentication failed: API key not recognized. Please get a valid key from https://openrouter.ai/keys"
            elif "exceed" in response_lower or "limit" in response_lower:
                return "Authentication failed: Usage limits exceeded. Check your account at https://openrouter.ai"
            else:
                return f"Authentication failed: {response_text}"
        elif status_code == 429:
            return "Rate limit exceeded. Please try again later."
        elif status_code >= 500:
            return "OpenRouter server error. Please try again later."
        else:
            return f"Error from OpenRouter API: {response_text}"


# Global OpenRouter client instance
openrouter_client = OpenRouterClient() 