import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class CloudRUClient:
    def __init__(self):
        self.api_key = os.getenv("FM_TOKEN")
        self.base_url = os.getenv("FM_BASE_URL")
        self.model = os.getenv("MODEL_NAME", "zai-org/GLM-4.7")
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def chat(self, messages, temperature=0.3):
        res = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        return res.choices[0].message.content

client = CloudRUClient()