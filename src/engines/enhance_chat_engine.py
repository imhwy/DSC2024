"""
"""
import re
import json
from typing import List, Any
from llama_index.llms.openai import OpenAI
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.chat_engine.context import ContextChatEngine
from llama_index.core.schema import NodeWithScore

from src.prompt.instruction_prompt import MERGE_PROMPT, CHECK_PROMPT
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
        token_limit: int = 1500,
        index: Any = None
    ) -> None:
        """
        """
        self._llm = llm
        self._retriever = index.as_retriever(
            vector_store_query_mode="hybrid",
            similarity_top_k=10,
            alpha=0.5
        )
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
            retriever=self._retriever,
            llm=self._llm,
            memory=self._memory,
            prefix_messages=self._prefix_messages
        )
        self._funny_chat_engine = ContextChatEngine(
            retriever=retriever,
            llm=self._llm,
            memory=self._memory,
            prefix_messages=self._prefix_outdomain_messages,
        )
        self._chat_memory_tracker = chat_memory_tracker

    async def process_retrieval_nodes(
        self,
        retrieval_nodes: List[NodeWithScore] = None
    ) -> List[str]:
        """
        """
        source_text = []
        for node in retrieval_nodes:
            temp_text = "File name: " + \
                node.metadata["file_name"] + "\nText: " + node.text
            source_text.append(temp_text)
        return source_text

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
            record = f"user question: {idx + 1}: {chat['query']}\nsystem response: {idx + 1}: {chat['answer']}"
            conversation_history.append(
                ChatMessage(
                    role="user",
                    content=record
                )
            )
        return conversation_history

    async def enhance_chat(
        self,
        query: str,
        chat_history: List[ChatMessage]
    ) -> str:
        response = self._chat_engine.chat(
            message=query,
            chat_history=chat_history
        )
        source_nodes = await self.process_retrieval_nodes(
            retrieval_nodes=response.source_nodes
        )
        return response.response, source_nodes

    async def enhance_funny_chat(
        self,
        room_id: str,
        query: str
    ) -> Any:
        """
        """
        chat_history = await self.history_config(
            room_id=room_id
        )
        result = await self.classify_query(text=query, history_tracking=chat_history)
        if result['conclusion']:
            return True
        response = self._funny_chat_engine.chat(
            message=query,
            chat_history=chat_history
        )
        print(type(response.source_nodes))
        print(response.source_nodes)
        return response.response

    async def classify_query(self, text, history_tracking):
        """
        """
        prompt = CHECK_PROMPT.format(query=text, history_chat=history_tracking)
        response = await self._llm.acomplete(prompt)
        string_processed = re.sub(r"```json|```", "", response.text)
        query_processed = json.loads(string_processed)
        return query_processed
