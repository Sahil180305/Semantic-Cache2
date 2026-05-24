import json
import logging
from typing import List, Optional, Dict, Any, Union, AsyncGenerator
import httpx
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# for normalisation so that cache hits are more likely even if user uses abbreviations in query. This is a simple regex-based approach and can be expanded with more patterns as needed.
import re

# Common tech/domain abbreviations map
ABBREVIATION_MAP = {
    r'\bai\b': 'artificial intelligence',
    r'\bml\b': 'machine learning',
    r'\bdl\b': 'deep learning',
    r'\bnlp\b': 'natural language processing',
    r'\bllm\b': 'large language model',
    r'\bgovt\.?\b': 'government',
    r'\bjs\b': 'javascript',
    r'\bpy\b': 'python',
    r'\bts\b': 'typescript',
    r'\bdb\b': 'database',
    r'\bui\b': 'user interface',
    r'\bux\b': 'user experience',
    r'\bio\b': 'input output',
    r'\bos\b': 'operating system',
}

def normalize_abbreviations(self, text: str) -> str:
    """Replace common abbreviations with full forms using regex."""
    normalized = text.lower() # Work in lowercase for matching
    for pattern, replacement in ABBREVIATION_MAP.items():
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
    return normalized

class LocalLLMService:
    """Service for processing text via local LLM via Ollama.
    Uses stateless client-side history and supports robust direct REST calls.
    Includes general chat capabilities alongside specialized query processing functions.
    """
    
    def __init__(
        self, 
        base_url: str = "http://localhost:11434", 
        model_name: str = "qwen2.5:1.5b",
        chat_temperature: float = 0.7,
        task_temperature: float = 0.0,
        timeout: float = 30.0,
        stream_timeout: float = 120.0,
        max_tokens: int = 2048
    ):
        self.base_url = base_url
        self.model_name = model_name
        self.chat_temperature = chat_temperature
        self.task_temperature = task_temperature
        self.timeout = timeout
        self.stream_timeout = stream_timeout
        self.max_tokens = max_tokens
        
        # Try to import ollama SDK (for potential future use)
        try:
            import ollama
            self._ollama_sdk = ollama
            self._has_sdk = True
            logger.info("Ollama Python SDK successfully loaded.")
        except ImportError:
            self._ollama_sdk = None
            self._has_sdk = False
            logger.info("Ollama Python SDK not found. Using direct HTTP REST calls.")

        self._dedup_model: Optional[SentenceTransformer] = None

    @property
    def dedup_model(self) -> SentenceTransformer:
        """Lazy-load embedding model for sub-query deduplication."""
        if self._dedup_model is None:
            self._dedup_model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._dedup_model

    def _deduplicate_sub_queries(self, query: str, sub_queries: List[str]) -> List[str]:
        """Remove near-duplicate sub-queries while keeping intent-aligned splits."""
        if len(sub_queries) <= 1:
            return sub_queries if sub_queries else [query]

        embeddings = self.dedup_model.encode(sub_queries)
        original_embedding = self.dedup_model.encode([query])[0]

        kept: List[str] = []
        for sq, emb in zip(sub_queries, embeddings):
            if kept:
                kept_embs = self.dedup_model.encode(kept)
                sims = cosine_similarity([emb], kept_embs)[0]
                if max(sims) > 0.92:
                    continue
            orig_sim = cosine_similarity([emb], [original_embedding])[0][0]
            if orig_sim > 0.7:
                kept.append(sq)

        return kept if kept else [query]

    async def health_check(self) -> Dict[str, Any]:
        """Check if Ollama service is available and return available models."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
                response.raise_for_status()
                data = response.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                return {
                    "available": True,
                    "models": models,
                    "current_model": self.model_name,
                    "model_loaded": self.model_name in models or any(self.model_name.split(":")[0] in m for m in models)
                }
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "current_model": self.model_name
            }

    async def _generate(
        self, 
        prompt: str, 
        system: Optional[str] = None, 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Helper to invoke Ollama generation via direct REST API."""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature if temperature is not None else self.task_temperature,
                "num_predict": max_tokens if max_tokens is not None else self.max_tokens
            }
        }
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                # Check for errors in response
                if "error" in data:
                    raise Exception(data["error"])
                    
                return data.get("response", "").strip()
        except httpx.ConnectError:
            raise ConnectionError(f"Cannot connect to Ollama at {self.base_url}. Is it running?")
        except httpx.TimeoutException:
            raise TimeoutError(f"Ollama request timed out after {self.timeout}s")
        except httpx.HTTPStatusError as e:
            error_msg = e.response.text if e.response else str(e)
            if e.response.status_code == 404:
                raise ValueError(f"Model '{self.model_name}' not found. Run: ollama pull {self.model_name}")
            raise Exception(f"Ollama HTTP error {e.response.status_code}: {error_msg}")
        except Exception as e:
            if isinstance(e, (ConnectionError, TimeoutError, ValueError)):
                raise
            raise Exception(f"Failed to query local Ollama: {e}")

    async def _generate_stream(
        self, 
        prompt: str, 
        system: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> AsyncGenerator[str, None]:
        """Helper to invoke Ollama streaming generation via direct REST API."""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature if temperature is not None else self.chat_temperature,
                "num_predict": self.max_tokens
            }
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=payload, timeout=self.stream_timeout) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    
                    try:
                        data = json.loads(line)
                        
                        if "error" in data:
                            raise Exception(data["error"])
                        
                        if data.get("done", False):
                            break
                        
                        if "response" in data:
                            text = data["response"]
                            if text:
                                yield text
                                
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse streaming data: {line}")
                    except Exception as e:
                        if "error" in str(e).lower() or isinstance(e, (ConnectionError, TimeoutError)):
                            raise
                        logger.error(f"Error processing stream chunk: {e}")

    # ==================== General Chat Methods ====================

    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate a general chat response using local LLM.
        
        This method can be used as a drop-in replacement for external LLM services.
        """
        default_system = "You are a helpful, friendly AI assistant. Provide clear and concise responses."
        system = system_prompt or default_system
        
        return await self._generate(
            prompt=prompt, 
            system=system,
            temperature=temperature if temperature is not None else self.chat_temperature
        )

    async def generate_stream_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming chat response using local LLM."""
        default_system = "You are a helpful, friendly AI assistant. Provide clear and concise responses."
        system = system_prompt or default_system
        
        async for chunk in self._generate_stream(
            prompt=prompt,
            system=system,
            temperature=temperature if temperature is not None else self.chat_temperature
        ):
            yield chunk

    async def generate_with_history(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate response with full conversation history using Ollama chat API."""
        url = f"{self.base_url}/api/chat"
        
        formatted_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted_messages.append({"role": role, "content": content})
        
        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "stream": False,
            "options": {
                "temperature": temperature if temperature is not None else self.chat_temperature,
                "num_predict": self.max_tokens
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                if "error" in data:
                    raise Exception(data["error"])
                    
                return data.get("message", {}).get("content", "").strip()
        except httpx.ConnectError:
            raise ConnectionError(f"Cannot connect to Ollama at {self.base_url}")
        except httpx.TimeoutException:
            raise TimeoutError(f"Ollama chat request timed out after {self.timeout}s")
        except Exception as e:
            if isinstance(e, (ConnectionError, TimeoutError)):
                raise
            raise Exception(f"Failed to chat with local Ollama: {e}")

    async def generate_stream_with_history(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response with full conversation history."""
        url = f"{self.base_url}/api/chat"
        
        formatted_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted_messages.append({"role": role, "content": content})
        
        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "stream": True,
            "options": {
                "temperature": temperature if temperature is not None else self.chat_temperature,
                "num_predict": self.max_tokens
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=payload, timeout=self.stream_timeout) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    
                    try:
                        data = json.loads(line)
                        
                        if "error" in data:
                            raise Exception(data["error"])
                        
                        if data.get("done", False):
                            break
                        
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
                            
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse chat stream data: {line}")
                    except Exception as e:
                        if "error" in str(e).lower() or isinstance(e, (ConnectionError, TimeoutError)):
                            raise
                        logger.error(f"Error processing chat stream chunk: {e}")

    # ==================== Specialized Query Processing Methods ====================

    async def rewrite_query(self, query: str, history: List[Any]) -> str:
        """Rewrite a contextual query into a standalone query using conversation history."""
        if not history or len(history) == 0:
            return query
            
        # Format the conversation history
        history_lines = []
        for msg in history:
            # Handle both pydantic models and dictionaries
            role = "User" if getattr(msg, "role", "").lower() == "user" or (isinstance(msg, dict) and msg.get("role", "").lower() == "user") else "Assistant"
            content = getattr(msg, "content", "") if hasattr(msg, "content") else (msg.get("content", "") if isinstance(msg, dict) else str(msg))
            history_lines.append(f"{role}: {content}")
        
        history_text = "\n".join(history_lines)
        
        system_prompt = (
            "You are an expert search query rewriter. "
            "Your task is to rewrite the latest user query to be a standalone, clear, and search-friendly query "
            "that contains all necessary context (e.g. replacing pronouns like 'it', 'he', 'that' with their referents from the conversation history). "
            "Do NOT answer the query. Do NOT explain your answer. Output ONLY the rewritten standalone query."
        )
        
        prompt = (
            f"Conversation History:\n{history_text}\n\n"
            f"Latest User Query: {query}\n\n"
            f"Rewritten Standalone Query:"
        )
        
        try:
            rewritten = await self._generate(prompt, system=system_prompt)
            # Basic cleaning in case model adds prefixes
            if rewritten.lower().startswith("rewritten standalone query:"):
                rewritten = rewritten[len("rewritten standalone query:"):].strip()
            # Clean outer quotes if any
            if (rewritten.startswith('"') and rewritten.endswith('"')) or (rewritten.startswith("'") and rewritten.endswith("'")):
                rewritten = rewritten[1:-1].strip()
            return rewritten if rewritten else query
        except Exception as e:
            logger.warning(f"Error during query rewriting: {e}. Using original query.")
            return query

    async def decompose_query(self, query: str) -> List[str]:
        """Decompose a complex multi-intent query into simpler, independent sub-queries."""
        system_prompt = (
            "You are a query decomposition and normalization assistant.\n\n"
            "YOUR TASK:\n"
            "1. Break down complex multi-intent queries into independent sub-queries.\n"
            "2. EXPAND all abbreviations, acronyms, and shortforms into their full formal terms.\n"
            "3. If the query has ONLY ONE intent, return a JSON list with ONLY the normalized original query.\n\n"
            "NORMALIZATION RULES:\n"
            "- 'ai' → 'artificial intelligence'\n"
            "- 'ml' → 'machine learning'\n"
            "- 'dl' → 'deep learning'\n"
            "- 'nlp' → 'natural language processing'\n"
            "- 'govt' or 'govt.' → 'government'\n"
            "- 'db' → 'database'\n"
            "- 'api' → 'application programming interface' (only if context implies technical definition, otherwise keep API)\n"
            "- 'js' → 'javascript'\n"
            "- 'py' → 'python'\n"
            "- 'cs' → 'computer science'\n"
            "- Always use lowercase for common nouns, proper case for proper nouns.\n\n"
            "OUTPUT FORMAT:\n"
            "- Output ONLY a valid JSON list of strings.\n"
            "- Use DOUBLE quotes.\n"
            "- NO markdown, NO explanations, NO trailing commas.\n\n"
            "EXAMPLES:\n"
            'Input: "what is ai"\n'
            'Output: ["what is artificial intelligence"]\n\n'
            'Input: "explain ml and dl"\n'
            'Output: ["explain machine learning", "explain deep learning"]\n\n'
            'Input: "how to use govt data for ai projects"\n'
            'Output: ["how to use government data for artificial intelligence projects"]\n\n'
            'Input: "features of python"\n'
            'Output: ["features of python"]\n\n'
            'Input: "compare js and py for web dev"\n'
            'Output: ["compare javascript and python for web development"]\n\n'
            "NOW PROCESS THE USER QUERY. OUTPUT JSON ONLY:"
        )
        
        
        prompt = f"Query: {query}\nJSON List of sub-queries:"
        
        try:
            raw_response = await self._generate(prompt, system=system_prompt,temperature=0.1,
            top_p=0.9,
            max_tokens=256,
            stop=["\n\n", "###"]  # Help model stop cleanly
            )
        
            # 🔥 DEBUG: Log raw output to see what model actually returns
            logger.debug(f"Raw decomposition response: {repr(raw_response)}")
            
            # Clean response for JSON parsing
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Try to parse JSON
            sub_queries = json.loads(cleaned)
            if isinstance(sub_queries, list):
                result = [str(item).strip() for item in sub_queries if item]
                result = result if result else [query]
                return self._deduplicate_sub_queries(query, result)
            return [query]
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse query decomposition JSON: {e}")
            return [query]
        except Exception as e:
            logger.error(f"Error during query decomposition: {e}")
            return [query]

    async def synthesize_response(
        self,
        original_query: str,
        sub_answers: Union[List[str], List[Dict[str, Any]]],
    ) -> str:
        """Synthesize answers from sub-queries into a cohesive response answering the original query."""
        sub_answers_lines = []
        for i, item in enumerate(sub_answers):
            if isinstance(item, dict):
                q = item.get("query", f"Part {i+1}")
                a = item.get("response", "No answer found.")
                sub_answers_lines.append(f"Sub-Query: {q}\nAnswer: {a}")
            else:
                sub_answers_lines.append(f"Answer Part {i+1}: {item}")

        sub_answers_text = "\n\n".join(sub_answers_lines)

        if len(sub_answers) == 1:
            if isinstance(sub_answers[0], dict):
                return sub_answers[0].get("response", "No answer found.")
            return str(sub_answers[0])

        system_prompt = (
            "You are an answer synthesis assistant. Your task is to combine the provided answers to sub-queries "
            "into a single, cohesive, comprehensive, and natural-sounding response that directly and fully answers the original user query. "
            "Do NOT mention 'sub-queries' or 'synthesized response' in your output. Just output the final cohesive response."
        )

        prompt = (
            f"Original Query: {original_query}\n\n"
            f"Sub-Answers:\n{sub_answers_text}\n\n"
            f"Final Cohesive Response:"
        )

        return await self._generate(prompt, system=system_prompt)

    async def classify_intent(self, query: str, intents: List[str]) -> Dict[str, Any]:
        """Classify the intent of a query from a list of possible intents."""
        intents_str = json.dumps(intents)
        
        system_prompt = (
            "You are an intent classification assistant. Classify the user query into one of the provided intents. "
            "Output ONLY a valid JSON object with 'intent' (the matched intent string) and 'confidence' (a float 0-1)."
        )
        
        prompt = f"Query: {query}\nPossible Intents: {intents_str}\nClassification:"
        
        try:
            response = await self._generate(prompt, system=system_prompt)
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            result = json.loads(cleaned)
            return {
                "intent": result.get("intent", intents[0] if intents else "unknown"),
                "confidence": float(result.get("confidence", 0.0))
            }
        except Exception as e:
            logger.error(f"Error during intent classification: {e}")
            return {"intent": intents[0] if intents else "unknown", "confidence": 0.0}

    async def extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from a query for search purposes."""
        system_prompt = (
            "You are a keyword extraction assistant. Extract the most important search keywords from the query. "
            "Output ONLY a valid JSON list of keyword strings. Remove stop words, keep only meaningful terms."
        )
        
        prompt = f"Query: {query}\nKeywords:"
        
        try:
            response = await self._generate(prompt, system=system_prompt)
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            keywords = json.loads(cleaned)
            if isinstance(keywords, list):
                return [str(k).strip().lower() for k in keywords if k]
            return []
        except Exception as e:
            logger.error(f"Error during keyword extraction: {e}")
            return []