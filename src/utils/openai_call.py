# from llama_index.llms.openai import OpenAI
import os
from langchain_openai import AzureChatOpenAI

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# llm = OpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

llm = AzureChatOpenAI(
    azure_deployment="gptbot-o'",
    model="gpt-4o",  # or your deployment
    api_version="2024-02-15-preview",  # or your api version
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    azure_endpoint="https://bgsv-gpt.openai.azure.com/",
    openai_api_type="azure",
)


# system_prompt = """
# From provided link, rewrite the name in vietnames with full tone mark. Only answer the refined name. Do not add additional information.
# Provided link: {link}
# """


# async def get_major_name_from_link(link):
#     """
#     Get the major name from a link.

#     Args:
#         link (str): The link to extract the major name from.

#     Returns:
#         str: The major name extracted from the link.
#     """
#     response = await llm.acomplete(system_prompt.format(link=link))
#     return response

system_prompt = """
From provided link, rewrite the name in vietnames with full tone mark. Only answer the refined name. Do not add additional information.
Provided link: 
"""

async def get_major_name_from_link(link):
    """
    Get the major name from a link.

    Args:
        link (str): The link to extract the major name from.

    Returns:
        str: The major name extracted from the link.
    """
    messages = [
        (
            "system",
            system_prompt,
        ),
        ("human", link),
    ]
    ai_msg = await llm.ainvoke(messages)
    return ai_msg
