import re
from typing import List, Union, Any
import pandas as pd
import multiprocessing
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import urlparse
from tqdm import tqdm
from llama_index.readers.web import SimpleWebPageReader
from llama_index.core.schema import Document
from llama_index.core import SimpleDirectoryReader
from llama_parse import LlamaParse
from llama_parse.utils import Language, ResultType
import markdownify

load_dotenv()

class BaseLoader:
    def load_data(self, source: Union[str, List[str]]) -> List[Document]:
        raise NotImplementedError("Subclasses should implement this method")


class URLLoader(BaseLoader):
    @staticmethod
    def remove_duplicate_new_line(input_string: str) -> str:
        return re.sub(r'\n+', '\n', input_string)

    @staticmethod
    def extract_articles(html_text: str, delimiter: str = "\n\n") -> str:
        pattern = re.compile(r'<article.*?>(.*?)</article>', re.DOTALL)
        matches = pattern.findall(html_text)
        stripped_matches = [match.strip() for match in matches]
        return delimiter.join(stripped_matches)

    def load_data(self, urls: List[str]) -> List[Document]:
        reader = SimpleWebPageReader()
        documents = reader.load_data(urls)
        
        for doc in documents:
            articles = self.extract_articles(doc.text)
            articles = self.remove_duplicate_new_line(articles)
            markdown_text = markdownify.markdownify(articles)
            doc.text = markdown_text
        
        return documents


class ExcelLoader(BaseLoader):
    @staticmethod
    def convert_to_markdown(file_path: str) -> str:
        df = pd.read_excel(file_path)
        df.dropna(how='all', axis=0, inplace=True)
        df.dropna(how='all', axis=1, inplace=True)
        df.set_index(df.columns[0], inplace=True)
        df.replace(to_replace=r'\n', value='<br>', regex=True, inplace=True)
        return df.to_markdown()

    def load_data(self, files_list: List[str]) -> List[Document]:
        documents = []
        for file in files_list:
            markdown_text = self.convert_to_markdown(file)
            documents.append(Document(text=markdown_text, metadata={'file_path': file}))
        return documents


class PDFLoader(BaseLoader):
    def __init__(self,
                 result_type: ResultType = ResultType.MD, 
                 language: Language = Language.VIETNAMESE,
                 parsing_instruction: str = 'Parse and structure the information from the file provided. Write in Vietnamese'
                 ) -> None:
        
        self.num_workers = multiprocessing.cpu_count()
        self.parser = LlamaParse(
            result_type=result_type, 
            language=language,
            parsing_instruction=parsing_instruction,
            num_workers=9,
            invalidate_cache=True,
        )
        self.extensions = [
            ".xls", ".xlsx", ".csv", ".tsv",  # excel
            ".jpg", ".jpeg", ".png", ".svg", ".tiff", ".webp", ".bmp",  # image
            ".pdf"  # pdf
        ]
        self.file_extractor = {ext: self.parser for ext in self.extensions}

    def load_data(self, files_list: List[str]) -> List[Document]:
        try: 
            documents = SimpleDirectoryReader(input_files=files_list,
                                              file_extractor=self.file_extractor
                                             ).load_data(num_workers=self.num_workers)
        except Exception as e:
            print('Use default PDF, return text instead of markdown:', str(e))
            del self.file_extractor['.pdf']
            documents = SimpleDirectoryReader(input_files=files_list,
                                              file_extractor=self.file_extractor
                                             ).load_data(num_workers=self.num_workers)
        return documents


class GeneralLoader(BaseLoader):
    def __init__(self) -> None:
        self.pdf_loader = PDFLoader()
        self.excel_loader = ExcelLoader()
        self.url_loader = URLLoader()
        self.pdf_ext = ['.pdf']
        self.excel_ext = [".xls", ".xlsx", ".csv", ".tsv"]

    @staticmethod
    def is_valid_url(url: str, qualifying: tuple = ('scheme', 'netloc')) -> bool:
        tokens = urlparse(url)
        return all(getattr(tokens, qualifying_attr) for qualifying_attr in qualifying)

    def check_extension(self, file_path: str) -> str:
        path = Path(file_path)

        if path.is_file():
            if path.suffix in self.pdf_ext:
                return 'pdf'
            elif path.suffix in self.excel_ext:
                return 'excel'
        elif self.is_valid_url(file_path):
            return 'url'
        else:
            raise ValueError(f"Unsupported file type or invalid URL: {file_path}")

    def load_data(self, sources: List[str]) -> List[Document]:
        documents = []
        for source in tqdm(sources):
            source_type = self.check_extension(source)
            
            if source_type == 'pdf':
                documents.extend(self.pdf_loader.load_data([source]))
            elif source_type == 'excel':
                documents.extend(self.excel_loader.load_data([source]))
            elif source_type == 'url':
                documents.extend(self.url_loader.load_data([source]))
            else: 
                print('Source type is not supported:', source_type)
            
        return documents
