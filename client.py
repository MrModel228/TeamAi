# client.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class CloudRUClient:
    def __init__(self):
        self.api_key = os.getenv("FM_TOKEN")
        self.base_url = os.getenv("FM_BASE_URL", "https://foundation-models.api.cloud.ru/v1")
        self.model = os.getenv("MODEL_NAME", "zai-org/GLM-4.7")
        
        if not self.api_key:
            raise Exception("❌ FM_TOKEN не найден в .env")
        
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def chat(self, messages, temperature=0.3):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=8192
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"🛑 Ошибка API Cloud.ru: {str(e)}"

client = CloudRUClient()
