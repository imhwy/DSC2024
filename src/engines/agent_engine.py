"""
"""
import os
from typing import List
from dotenv import load_dotenv
from llama_index.core.retrievers import BaseRetriever
from llama_index.core import VectorStoreIndex
from llama_index.core.objects import ObjectIndex
from llama_index.core.agent import ReActAgent
from llama_index.core.base.llms.types import ChatMessage
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import (ToolMetadata,
                                    RetrieverTool,
                                    FunctionTool)

from src.prompt.agent_prompt import AGENT_INSTRUCTION_PROMPT
from src.utils.utility import (convert_value,
                               sum_subjects,
                               compare_score,
                               get_uit_national_high_school_graduation_scores_2024,
                               get_uit_competency_assessment_scores_2024)

load_dotenv()

TOOL_SIMILARITY = convert_value(os.getenv("TOOL_SIMILARITY"))
MAX_ITERATIONS = convert_value(os.getenv("MAX_ITERATIONS"))


class AgentEngine:
    """
    """

    def __init__(
        self,
        retriever: BaseRetriever = None,
        index: VectorStoreIndex = None,
        llm: OpenAI = None,
        tool_similarity: int = TOOL_SIMILARITY
    ) -> None:
        """
        """
        self._retriever = retriever
        self._tool_similarity = tool_similarity

        self._retriever_tool = RetrieverTool(
            retriever=self._retriever,
            metadata=ToolMetadata(
                name="retriever_tool",
                description=(
                    "Using for retrieval relevant information from user's query."
                ),
            ),
        )
        self._sum_tool = FunctionTool.from_defaults(
            fn=sum_subjects,
            name="sum_subjects",
            description="This tool is used to sum all user's subjects"
        )
        self._compare_tool = FunctionTool.from_defaults(
            fn=compare_score,
            name="compare_score",
            description="This tool is used to compare user's total score to all the major's cutoff score"
        )
        self._get_uit_competency_assessment_score_2024_tool = FunctionTool.from_defaults(
            fn=get_uit_competency_assessment_scores_2024,
            name="get uit competency assessment score 2024",
            description="This tool is used to get UIT competency assessment score for 2024"
        )
        self._get_uit_national_high_school_graduation_scores_2024 = FunctionTool.from_defaults(
            fn=get_uit_national_high_school_graduation_scores_2024,
            name="get uit national high school graduation scores 2024",
            description="This tool is used to get UIT national high school graduation scores for 2024"
        )
        self._tools = [
            self._retriever_tool,
            self._sum_tool,
            self._compare_tool,
            self._get_uit_competency_assessment_score_2024_tool,
            self._get_uit_national_high_school_graduation_scores_2024
        ]
        self._obj_index = ObjectIndex.from_objects(
            self._tools,
            index=index
        )
        self._agent = ReActAgent.from_tools(
            tool_retriever=self._obj_index.as_retriever(similarity_top_k=10),
            llm=llm,
            verbose=True,
            max_iterations=MAX_ITERATIONS,
            system_prompt=AGENT_INSTRUCTION_PROMPT
        )

    async def reasoning_agent(
        self,
        chat: str = None,
        chat_history: List[ChatMessage] = List[None]
    ) -> str:
        """
        """
        response = await self._agent.achat(
            message=chat,
            chat_history=chat_history
        )
        return response.response
