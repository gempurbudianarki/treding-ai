from loguru import logger
import requests
import json
from openai import OpenAI
from core.config import settings


class GeminiClient:
    def __init__(self):
        # ambil API key yang benar
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY

        # REST endpoint Gemini
        self.model_name = "gemini-1.5-flash"
        self.endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model_name}:generateContent?key={self.gemini_key}"
        )

        # OpenAI Fallback client
        self.client = OpenAI(api_key=self.openai_key)

        logger.info("GeminiClient loaded (REST + OpenAI fallback). Model fallback: gpt-4.1-mini")

    def _call_gemini_rest(self, text: str):
        try:
            payload = {
                "contents": [
                    {"parts": [{"text": text}]}
                ]
            }
            r = requests.post(
                self.endpoint,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=10
            )

            if r.status_code != 200:
                logger.warning(f"[Gemini REST] Error {r.status_code}: {r.text}")
                return None

            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

        except Exception as e:
            logger.warning(f"[Gemini REST] Exception: {e}")
            return None

    def analyze_text(self, text: str):
        # 1️⃣ Coba pakai Gemini REST dulu
        gemini_result = self._call_gemini_rest(text)
        if gemini_result:
            return gemini_result.strip()

        logger.warning("Fallback to OpenAI GPT...")

        # 2️⃣ Kalau gagal → fallback ke OpenAI GPT
        try:
            resp = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": text}],
                max_tokens=80,
            )
            return resp.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI fallback error: {e}")
            return "neutral"
