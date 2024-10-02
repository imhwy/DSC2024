"""
"""
from typing import List
from llama_index.llms.openai import OpenAI
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.chat_engine.context import ContextChatEngine

from src.prompt.instruction_prompt import MERGE_PROMPT
from src.prompt.funny_chat_prompt import PROMPT_ENHANCE_FUNNY_FLOW
from src.repositories.chat_repository import ChatRepository


class EnhanceChatEngine:
    """
    """

    def __init__(
        self,
        llm: OpenAI = None,
        retriever: BaseRetriever = None,
        chat_memory_tracker: ChatRepository = None,
        token_limit: int = 1500
    ) -> None:
        """
        """
        self._llm = llm
        self._retriever = retriever
        self._memory = ChatMemoryBuffer.from_defaults(
            token_limit=token_limit
        )
        self._prefix_messages = [
            ChatMessage(
                role="system",
                content=MERGE_PROMPT
            )
        ]
        self._prefix_outdomain_messages = [
            ChatMessage(
                role="system",
                content=PROMPT_ENHANCE_FUNNY_FLOW
            )
        ]
        self._chat_engine = ContextChatEngine(
            retriever=retriever,
            llm=self._llm,
            memory=self._memory,
            prefix_messages=self._prefix_messages,
        )
        self._funny_chat_engine = ContextChatEngine(
            retriever=retriever,
            llm=self._llm,
            memory=self._memory,
            prefix_messages=self._prefix_outdomain_messages,
        )
        self._chat_memory_tracker = chat_memory_tracker

    async def history_config(
        self,
        room_id: str
    ) -> List[ChatMessage]:
        """
        """
        conversation_history = []
        lastest_chats = await self._chat_memory_tracker.get_last_chat(
            room_id=room_id
        )
        lastest_chats = list(lastest_chats)
        for idx, chat in enumerate(reversed(lastest_chats)):
            record = f"user question: {idx + 1}: {chat['query']}\nsystem resoponse: {idx + 1}: {chat['answer']}"
            conversation_history.append(
                ChatMessage(
                    role="user",
                    content=record
                )
            )
        return conversation_history

    async def enhance_chat(
        self,
        room_id: str,
        query: str
    ) -> str:
        chat_history = await self.history_config(
            room_id=room_id
        )
        response = self._chat_engine.chat(
            message=query,
            chat_history=chat_history
        )
        return response.response

    async def enhance_funny_chat(
        self,
        room_id: str,
        query: str
    ) -> str:
        """
        """
        chat_history = await self.history_config(
            room_id=room_id
        )
        response = self._funny_chat_engine.chat(
            message=query,
            chat_history=chat_history
        )
        return response.response
