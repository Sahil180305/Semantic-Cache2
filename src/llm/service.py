import json
import logging
from typing import Optional, AsyncGenerator, List, Any, Dict
import httpx

from src.core.config import LLMConfig
from src.utils.logging import get_logger

logger = get_logger(__name__)

class LLMService:
    """Service for interacting with language models (Gemini, OpenAI, Local Ollama)."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.provider = config.provider.lower()
        self.api_key = config.api_key
        self.model = config.model or "gemini-pro"
        
        # Local LLM configuration (Ollama)
        self.local_base_url = getattr(config, 'local_base_url', 'http://localhost:11434')
        self.local_model = getattr(config, 'local_model', 'qwen2.5:1.5b')
        self.local_temperature = getattr(config, 'local_temperature', 0.7)
        self.local_timeout = getattr(config, 'local_timeout', 60.0)
        self.local_stream_timeout = getattr(config, 'local_stream_timeout', 120.0)
        
        # Validate configuration based on provider
        if self.provider not in ("local", "ollama") and not self.api_key:
            logger.warning(f"No API key provided for LLM service (provider: {self.provider}). LLM features may fail.")
        
        if self.provider in ("local", "ollama"):
            logger.info(f"Local LLM configured: {self.local_model} at {self.local_base_url}")

    async def generate_with_history(
        self,
        query: str,
        history: Optional[List[Any]] = None,
        system_prompt: Optional[str] = None,
    ) -> Optional[str]:
        """Generate a response using full conversation history (no caching)."""
        messages: List[Dict[str, str]] = []
        for msg in history or []:
            role = msg.role if hasattr(msg, "role") else msg.get("role", "user")
            content = msg.content if hasattr(msg, "content") else msg.get("content", "")
            messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": query})

        if self.provider not in ("local", "ollama") and not self.api_key:
            logger.warning(f"No API key for cloud provider '{self.provider}', skipping generation")
            return None

        try:
            if self.provider in ("local", "ollama"):
                return await self._call_local_chat(messages, system_prompt)
            elif self.provider == "gemini":
                return await self._call_gemini_chat(messages, system_prompt)
            else:
                prompt = self._history_to_prompt(messages, system_prompt)
                return await self.generate_response(prompt, system_prompt=None)
        except Exception as e:
            logger.error(f"Error generating LLM response with history: {e}")
            return None

    @staticmethod
    def _history_to_prompt(messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        lines = []
        if system_prompt:
            lines.append(f"System: {system_prompt}\n")
        for msg in messages:
            role = msg.get("role", "user").capitalize()
            lines.append(f"{role}: {msg.get('content', '')}")
        lines.append("Assistant:")
        return "\n".join(lines)

    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """Generate a response using the configured LLM provider."""
        # Only gate on API key for cloud providers; local/Ollama never needs one
        if self.provider not in ("local", "ollama") and not self.api_key:
            logger.warning(f"No API key for cloud provider '{self.provider}', skipping generation")
            return None
            
        try:
            if self.provider == "gemini":
                return await self._call_gemini(prompt, system_prompt)
            elif self.provider == "openai":
                return await self._call_openai(prompt, system_prompt)
            elif self.provider in ("local", "ollama"):
                return await self._call_local(prompt, system_prompt)
            else:
                logger.error(f"Unsupported LLM provider: {self.provider}")
                return None
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return None

    async def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Generate a streaming response using the configured LLM provider."""
        # Only gate on API key for cloud providers; local/Ollama never needs one
        if self.provider not in ("local", "ollama") and not self.api_key:
            logger.warning(f"No API key for cloud provider '{self.provider}', skipping stream")
            return
            
        try:
            if self.provider == "gemini":
                async for chunk in self._stream_gemini(prompt, system_prompt):
                    yield chunk
            elif self.provider == "openai":
                async for chunk in self._stream_openai(prompt, system_prompt):
                    yield chunk
            elif self.provider in ("local", "ollama"):
                async for chunk in self._stream_local(prompt, system_prompt):
                    yield chunk
            else:
                logger.error(f"Unsupported LLM provider for streaming: {self.provider}")
                yield f"Error: Unsupported provider {self.provider}"
        except Exception as e:
            logger.error(f"Error streaming LLM response: {e}")
            yield f"Error: Generation failed due to internal error."

    async def check_local_health(self) -> bool:
        """Check if local Ollama service is available and responsive."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.local_base_url}/api/tags", timeout=5.0)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [m.get("name", "") for m in models]
                    logger.info(f"Ollama available. Models: {model_names}")
                    return True
                return False
        except Exception as e:
            logger.warning(f"Local Ollama health check failed: {e}")
            return False

    async def _call_local_chat(
        self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """Call local Ollama chat API with multi-turn history."""
        url = f"{self.local_base_url}/api/chat"
        payload = {
            "model": self.local_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.local_temperature,
                "num_predict": 2048,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=self.local_timeout)
                response.raise_for_status()
                data = response.json()
                if "error" in data:
                    return f"Error: {data['error']}"
                return data.get("message", {}).get("content", "").strip()
        except httpx.ConnectError:
            logger.error(f"Could not connect to local Ollama service at {self.local_base_url}")
            return "Error: Local LLM service is not available. Please ensure Ollama is running at " + self.local_base_url
        except httpx.TimeoutException:
            logger.error(f"Local LLM chat request timed out after {self.local_timeout}s")
            return "Error: Local LLM request timed out."
        except httpx.HTTPStatusError as e:
            logger.error(f"Local LLM chat HTTP error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 404:
                return f"Error: Model '{self.local_model}' not found. Please pull it using 'ollama pull {self.local_model}'"
            return f"Error: Local LLM returned error {e.response.status_code}"
        except Exception as e:
            logger.error(f"Error calling local LLM chat: {e}")
            return "Error: Failed to get response from local LLM."

    async def _call_gemini_chat(
        self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """Call Gemini with multi-turn conversation history."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System: {system_prompt}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})

        for msg in messages:
            role = "model" if msg.get("role") == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})

        payload = {"contents": contents}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=60.0)
            response.raise_for_status()
            data = response.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                logger.error(f"Unexpected response format from Gemini: {data}")
                return "Error: Could not parse response from Gemini."

    async def _call_local(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """Call local Ollama API for standard generation."""
        url = f"{self.local_base_url}/api/generate"
        
        payload = {
            "model": self.local_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.local_temperature,
                "num_predict": 2048  # Max tokens to generate
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=self.local_timeout)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "").strip()
        except httpx.ConnectError:
            logger.error(f"Could not connect to local Ollama service at {self.local_base_url}")
            return "Error: Local LLM service is not available. Please ensure Ollama is running at " + self.local_base_url
        except httpx.TimeoutException:
            logger.error(f"Local LLM request timed out after {self.local_timeout}s")
            return "Error: Local LLM request timed out. The model may be too slow or overloaded."
        except httpx.HTTPStatusError as e:
            logger.error(f"Local LLM returned HTTP error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 404:
                return f"Error: Model '{self.local_model}' not found. Please pull it using 'ollama pull {self.local_model}'"
            return f"Error: Local LLM returned error {e.response.status_code}"
        except Exception as e:
            logger.error(f"Error calling local LLM: {e}")
            return "Error: Failed to get response from local LLM."

    async def _stream_local(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Call local Ollama API for streaming generation."""
        url = f"{self.local_base_url}/api/generate"
        
        payload = {
            "model": self.local_model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": self.local_temperature,
                "num_predict": 2048
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", url, json=payload, timeout=self.local_stream_timeout) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        
                        try:
                            data = json.loads(line)
                            
                            # Check for errors in response
                            if "error" in data:
                                logger.error(f"Local LLM stream error: {data['error']}")
                                yield f"\n\n[Error: {data['error']}]"
                                break
                            
                            # Check if generation is complete
                            if data.get("done", False):
                                # Optionally yield final stats if needed
                                break
                            
                            # Yield the text chunk
                            if "response" in data:
                                text = data["response"]
                                if text:
                                    yield text
                                    
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse streaming data: {line}")
                        except Exception as e:
                            logger.error(f"Error processing stream chunk: {e}")
                            
        except httpx.ConnectError:
            logger.error(f"Could not connect to local Ollama service at {self.local_base_url}")
            yield "Error: Local LLM service is not available. Please ensure Ollama is running."
        except httpx.TimeoutException:
            logger.error(f"Local LLM streaming request timed out after {self.local_stream_timeout}s")
            yield "\n\n[Error: Streaming timed out]"
        except httpx.HTTPStatusError as e:
            logger.error(f"Local LLM stream HTTP error: {e.response.status_code}")
            yield f"\n\n[Error: HTTP {e.response.status_code}]"
        except Exception as e:
            logger.error(f"Error streaming from local LLM: {e}")
            yield "\n\n[Error: Streaming failed]"

    async def _call_gemini(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """Call Gemini REST API for standard generation."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        parts = []
        if system_prompt:
            parts.append({"text": f"System: {system_prompt}\n\n"})
        parts.append({"text": prompt})
        
        payload = {
            "contents": [
                {
                    "parts": parts
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError) as e:
                logger.error(f"Unexpected response format from Gemini: {data}")
                return "Error: Could not parse response from Gemini."

    async def _stream_gemini(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Call Gemini REST API for streaming generation."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:streamGenerateContent?alt=sse&key={self.api_key}"
        
        parts = []
        if system_prompt:
            parts.append({"text": f"System: {system_prompt}\n\n"})
        parts.append({"text": prompt})
        
        payload = {
            "contents": [
                {
                    "parts": parts
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=payload, timeout=60.0) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            if "candidates" in data and len(data["candidates"]) > 0:
                                candidate = data["candidates"][0]
                                if "content" in candidate and "parts" in candidate["content"]:
                                    part = candidate["content"]["parts"][0]
                                    if "text" in part:
                                        yield part["text"]
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse SSE data: {data_str}")
                        except Exception as e:
                            logger.error(f"Error processing stream chunk: {e}")

    async def _call_openai(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """Placeholder for OpenAI standard generation."""
        logger.warning("OpenAI integration not yet implemented")
        return "OpenAI integration not yet implemented"
        
    async def _stream_openai(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Placeholder for OpenAI streaming generation."""
        logger.warning("OpenAI streaming integration not yet implemented")
        yield "OpenAI streaming integration not yet implemented"