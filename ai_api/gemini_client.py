import os
import requests
import json
from loguru import logger
from openai import OpenAI

from core.config import settings


class GeminiClient:
    """
    Smart client:
    - Coba pakai Gemini REST API
    - Kalau error, fallback ke OpenAI GPT
    """

    def __init__(self):
        self.gemini_key = settings.GEMINI_KEY
        self.openai_key = settings.OPENAI_KEY

        # Model Gemini REST (yang benar & valid)
        self.gemini_model = "gemini-1.5-flash"

        # Endpoint REST Gemini
        self.endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.gemini_model}:generateContent?key={self.gemini_key}"
        )

        # Fallback OpenAI client
        self.oai = OpenAI(api_key=self.openai_key)

        logger.info(
            f"GeminiClient loaded (REST + OpenAI fallback). Model fallback: gpt-4.1-mini"
        )

    # =====================================================================
    # GEMINI REST CALL
    # =====================================================================
    def _call_gemini_rest(self, text: str):
        body = {
            "contents": [
                {
                    "parts": [
                        {"text": text}
                    ]
                }
            ]
        }

        try:
            res = requests.post(
                self.endpoint,
                headers={"Content-Type": "application/json"},
                data=json.dumps(body),
                timeout=10
            )

            if res.status_code != 200:
                logger.warning(f"[Gemini REST] Error {res.status_code}: {res.text}")
                return None

            data = res.json()
            output = data["candidates"][0]["content"]["parts"][0]["text"]
            return output

        except Exception as e:
            logger.error(f"[Gemini REST] Exception: {e}")
            return None

    # =====================================================================
    # OPENAI FALLBACK
    # =====================================================================
    def _call_openai(self, text: str):
        try:
            response = self.oai.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Analyze sentiment (bullish, bearish, neutral)."},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"[OpenAI Fallback] Error: {e}")
            return None

    # =====================================================================
    # MAIN PUBLIC METHOD
    # =====================================================================
    def analyze_text(self, text: str):
        """
        1. Coba Gemini REST
        2. Jika gagal → fallback OpenAI
        """
        # --- Try Gemini REST ---
        result = self._call_gemini_rest(text)
        if result:
            return result

        logger.warning("Fallback to OpenAI GPT...")
        # --- Fallback GPT ---
        result = self._call_openai(text)
        if result:
            return result

        # --- Kalau dua-duanya gagal ---
        return "neutral"
