from typing import Dict, Any, Optional
import httpx
from ..config.settings import OPENAI_API_KEY

class APIService:
    def __init__(self):
        self.http_client = httpx.AsyncClient()
        self.openai_key = OPENAI_API_KEY

    async def get_embeddings(self, text: str) -> list[float]:
        try:
            response = await self.http_client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {self.openai_key}"},
                json={
                    "input": text,
                    "model": "text-embedding-ada-002"
                }
            )
            return response.json()["data"][0]["embedding"]
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            return []

    async def get_completion(
        self,
        prompt: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        try:
            response = await self.http_client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_key}"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    **({"max_tokens": max_tokens} if max_tokens else {})
                }
            )
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error getting completion: {e}")
            return ""

    async def lookup_property_info(self, address: str) -> Dict[str, Any]:
        # Implement property information lookup API
        pass

    async def check_credit_eligibility(
        self,
        customer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Implement credit check API
        pass

    async def get_utility_rates(
        self,
        zip_code: str,
        utility_type: str
    ) -> Dict[str, Any]:
        # Implement utility rate lookup API
        pass