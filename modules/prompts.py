from typing import Any, Dict, List
from llama_index.core.base.llms.types import ChatMessage, MessageRole

# from llama_index.core.prompts import PromptTemplate, ChatPromptTemplate


class LlamaPromptsManager:
    pass


class LlamaMessagesManager:
    @staticmethod
    def create_messages(messages: List[Dict[str, Any]]):
        return [
            ChatMessage(role=MessageRole(it["role"]), content=it["content"])
            for it in messages
        ]
