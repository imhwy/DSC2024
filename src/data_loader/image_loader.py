from src.data_loader.base_loader import BaseLoader
from llama_index.core.schema import Document
import google.generativeai as genai
import PIL.Image
from typing import List

from dotenv import load_dotenv

load_dotenv()
specific_prompt = """
1. Correct any obvious OCR errors.
2. Format the content into a clear, structured Markdown document.
3. Ensure proper formatting of tables, lists, and headings.
4. For table data:
   - Maintain the original order of rows as they appear in the OCR result.
   - Ensure each row of data stays together and is not split across different sections.
5. Preserve any important formatting in the original text.
6. Add any necessary explanations or notes at the end.
"""


class ImageLoader(BaseLoader):
    def __init__(self):
        self.genai = genai
        # self.genai.configure(api_key=api_key)

    async def load_image(self, filepath):
        return PIL.Image.open(filepath)

    async def perform_ocr(self, image):
        # Step 1: Perform OCR
        ocr_response = await self.genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest"
        ).generate_content_async(
            [
                image,
                "Perform OCR on this image and return the raw text result.\
                Do not modify or format the text in any way.",
            ]
        )
        return ocr_response.text

    async def post_process_ocr(self, ocr_text):
        # Step 2: Post-process and format the OCR result
        post_process_prompt = f"""
        Post-process and format the following OCR result:

        {ocr_text}
        {specific_prompt}
        """
        formatted_response = await self.genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest"
        ).generate_content_async(post_process_prompt)
        return formatted_response.text

    def load_data(self, sources: List[str]) -> List[Document]:
        """
        Load data from a list of image files and return a list of Document objects.

        Args:
            files_list (List[str]): A list of paths to image files.

        Returns:
            List[Document]: A list of Document objects containing the loaded data.
        """
        documents = []
        for source in sources:
            image = self.load_image(source)
            ocr_result = self.perform_ocr(image)
            formatted_result = self.post_process_ocr(ocr_result)
            documents.append(
                Document(text=formatted_result, metadata={"file_path": source})
            )
        return documents

    async def aload_data(self, sources: List[str]) -> List[Document]:
        """
        Load data from a list of image files and return a list of Document objects.

        Args:
            files_list (List[str]): A list of paths to image files.

        Returns:
            List[Document]: A list of Document objects containing the loaded data.
        """
        documents = []
        for source in sources:
            image = await self.load_image(source)
            ocr_result = await self.perform_ocr(image)
            formatted_result = await self.post_process_ocr(ocr_result)
            documents.append(
                Document(text=formatted_result, metadata={"file_path": source})
            )
        return documents


# Example usage:
# loader = ImageLoader()
# # Specify the path to the image file you want to process
# image_path = "images/phuong_thuc_xet_tuyen.jpeg"
# formatted_response = loader.load_data([image_path])
# # Print the formatted result
# Markdown(formatted_response)
