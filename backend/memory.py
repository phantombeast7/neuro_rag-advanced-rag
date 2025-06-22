from langchain.memory import ConversationBufferMemory
from typing import Dict

class MemoryManager:
    def __init__(self):
        self.memories: Dict[str, ConversationBufferMemory] = {}

    def get_memory(self, session_id: str) -> ConversationBufferMemory:
        if session_id not in self.memories:
            self.memories[session_id] = ConversationBufferMemory(return_messages=True)
        return self.memories[session_id]

    def reset_memory(self, session_id: str):
        if session_id in self.memories:
            del self.memories[session_id]

    def list_sessions(self):
        return list(self.memories.keys())

memory_manager = MemoryManager() 