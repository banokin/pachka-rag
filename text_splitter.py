"""Module for splitting documents on chuncks"""
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents.base import Document

class TextSplitter():
    """Split docs on chunks"""

    def __init__(self,
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200) -> None:
        """Initialization"""

        self.splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                                       chunk_overlap=chunk_overlap)

    def split_docs(self, docs: List[Document]) -> List[Document]:
        """Return docs splitted on chunk"""

        return self.splitter.split_documents(docs)
    
    