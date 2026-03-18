import json
import httpx
from app.ports.llm_port import LLMPort

class OllamaAdapter(LLMPort):
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def _chat(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
            )
            r.raise_for_status()
            data = r.json()
            return (data.get("response") or "").strip()

    async def generate_summary(self, text: str, max_length: int = 200) -> str:
        prompt = f"Summarize the following text in {max_length} words max:\n\n{text}"
        return await self._chat(prompt)

    async def generate_recommendation_reason(self, book_title: str, user_preferences: dict) -> str:
        prompt = f"Explain why '{book_title}' is recommended for a user with preferences: {user_preferences}."
        return await self._chat(prompt)

    async def analyze_sentiment(self, text: str) -> dict:
        prompt = (
            'Analyze sentiment of the text. '
            'Return ONLY valid JSON in this format: '
            '{"sentiment":"positive|neutral|negative","score":0.0}\n\n'
            f'Text:\n{text}'
        )
        raw = await self._chat(prompt)
        try:
            return json.loads(raw)
        except Exception:
            return {"sentiment": "unknown", "score": 0.5, "raw": raw}

    async def extract_keywords(self, text: str, max_keywords: int = 5) -> list[str]:
        prompt = (
            f"Extract {max_keywords} keywords from this text. "
            "Return ONLY a comma-separated list.\n\n"
            f"{text}"
        )
        raw = await self._chat(prompt)
        return [x.strip() for x in raw.split(",") if x.strip()][:max_keywords]