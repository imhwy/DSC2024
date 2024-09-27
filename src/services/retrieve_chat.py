"""
this service provides retrieve and chat module for chatbot
"""
from src.engines.chat_engine import ChatEngine
from src.engines.retriever_engine import HybridRetriever
from src.engines.semantic_engine import SemanticSearch
from src.engines.preprocess_engine import PreprocessQuestion
from src.repositories.chat_repository import ChatRepository
from src.models.chat import Chat
from src.prompt.postprocessing_prompt import FAIL_CASES, RESPONSE_FAIL_CASE


class RetrieveChat:
    """
    RetrieveChat: A class designed to retrieve chat responses.
    """

    def __init__(
        self,
        retriever: HybridRetriever = None,
        chat: ChatEngine = None,
        preprocess: PreprocessQuestion = None,
        semantic: SemanticSearch = None,
        chat_history_tracker: ChatRepository = None,
        max_chat_token: float = 2000
    ):
        self._retriever = retriever
        self._chat = chat
        self._preprocess = preprocess
        self._semantic = semantic
        self._chat_history_tracker = chat_history_tracker
        self._max_chat_token = max_chat_token

    async def history_chat_config(
        self,
        room_id: str
    ):
        """
        """
        lastest_chats = await self._chat_history_tracker.get_last_chat(
            room_id=room_id
        )
        lastest_chats = list(lastest_chats)
        combine_history_chat = ""
        sum_token = 0
        for idx, chat in enumerate(reversed(lastest_chats)):
            record = f"question {idx + 1}: {chat['query']}\nanswer {idx + 1}: {chat['answer']}"
            tokens = len(self._retriever.token_counter.encode(record))
            if tokens + sum_token > self._max_chat_token:
                break
            combine_history_chat = combine_history_chat + record + "\n"
            sum_token += tokens
        return combine_history_chat

    async def retriever_config(
        self,
        query: str,
    ):
        """
        """
        combined_retrieved_nodes, retrieved_nodes = await self._retriever.retrieve_nodes(
            query=query
        )
        response = await self._chat.generate_response(
            user_query=query,
            relevant_information=combined_retrieved_nodes
        )
        if response in FAIL_CASES:
            return Chat(
                response=RESPONSE_FAIL_CASE,
                is_outdomain=False,
                retrieved_nodes=[]
            )
        list_nodes = []
        for retrieved_node in retrieved_nodes:
            list_nodes.append(retrieved_node.text)
        return Chat(
            response=response,
            is_outdomain=False,
            retrieved_nodes=list_nodes
        )

    async def retrieve_chat(
        self,
        query: str,
        room_id: str
    ) -> Chat:
        """
        Processes a user"s query by retrieving relevant information and generating a chat response.

        Parameters:
            query(str): The user"s input query.

        Returns:
            response (str): The chat response generated for the query.
            is_outdomain (bool): True if the query is outside the domain scope, otherwise False.
        """
        history_chat = await self.history_chat_config(
            room_id=room_id
        )
        conversation_tracking = await self._chat.conversation_tracking(
            history=history_chat,
            query=query
        )
        print(conversation_tracking)
        if isinstance(conversation_tracking, dict):
            if conversation_tracking["is_answer"]:
                return Chat(
                    response=conversation_tracking["query"],
                    is_outdomain=False,
                    retrieved_nodes=[]
                )
            else:
                result = await self.retriever_config(
                    query=conversation_tracking["query"]
                )
                return result
        return await self.retriever_config(
            query=query
        )

    async def preprocess_query(
        self,
        query: str,
        room_id: str
    ) -> Chat:
        """
        Preprocesses the user's query and generates an appropriate response.

        Args:
            query (str): The input query from the user.

        Returns:
            Chat: A Chat object containing the response, a flag indicating if the response
                is out of domain, and a list of retrieved nodes.
        """
        processed_query = await self._preprocess.preprocess_text(
            text_input=query
        )
        print(processed_query)
        if processed_query.is_short_chat:
            return Chat(
                response=processed_query.query,
                is_outdomain=True,
                retrieved_nodes=[]
            )
        if processed_query.language is False:
            return Chat(
                response=processed_query.query,
                is_outdomain=True,
                retrieved_nodes=[]
            )
        if processed_query.is_prompt_injection:
            return Chat(
                response=processed_query.query,
                is_outdomain=True,
                retrieved_nodes=[]
            )
        if processed_query.is_outdomain:
            history_chat = await self.history_chat_config(
                room_id=room_id
            )
            conversation_tracking = await self._chat.conversation_tracking(
                history=history_chat,
                query=query
            )
            if isinstance(conversation_tracking, dict):
                if conversation_tracking["is_answer"]:
                    return Chat(
                        response=conversation_tracking["query"],
                        is_outdomain=True,
                        retrieved_nodes=[]
                    )
            answer = await self._semantic.get_relevant_answer(
                query=conversation_tracking["query"]
            )
            if answer:
                return Chat(
                    response=answer,
                    is_outdomain=True,
                    retrieved_nodes=[]
                )
            result = await self._chat.funny_chat(
                query=processed_query.query
            )
            return Chat(
                response=result,
                is_outdomain=True,
                retrieved_nodes=[]
            )
        return await self.retrieve_chat(
            query=processed_query.query,
            room_id=room_id
        )
