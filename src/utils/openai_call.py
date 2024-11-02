import openai
from llama_index.llms.openai import OpenAI
import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


llm = OpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

system_prompt = """From provided link, rewrite the name in vietnames with full tone mark. Only answer the refined name. Do not add additional information.
    Provided link: {link}"""


async def get_major_name_from_link(link):
    # Choose a Gemini API model.
    response = await llm.acomplete(system_prompt.format(link=link))
    return response
