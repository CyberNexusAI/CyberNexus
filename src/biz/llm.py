from volcenginesdkarkruntime import Ark
from src.biz.chat import Chat

class LLMManager:
    # Only support Volcengine Ark for now
    def __init__(self, api_key):
        self.client = Ark(api_key=api_key)

    def start_chat(self, instruction):
        chat = Chat(self.client, instruction)
        return chat
