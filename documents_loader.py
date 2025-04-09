"""Module for parsing documents from local storage"""
import os
from typing import List, Tuple
from langchain_community.document_loaders import DirectoryLoader

class DocumentLoader():
    """Docs parser"""

    def __init__(self, path: str,
                 file_formats: List[str] | Tuple[str] | str = "**/[!.]*",
                 specify_file_format:bool = False) -> None:
        """Initializaation"""

        self.path = path

        assert os.path.exists(path)

        if specify_file_format:
            self.loader = DirectoryLoader(path=self.path,
                                          glob=file_formats,
                                          show_progress=True,
                                          use_multithreading=True)
        else:
            self.loader = DirectoryLoader(path=self.path,
                                          show_progress=True,
                                          use_multithreading=True)

    def load_documents(self):
        """Return list of scanned docs"""

        return self.loader.load()