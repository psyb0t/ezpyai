import os
import json
import magic
import tempfile
import zipfile
import shutil
import hashlib
import logging
import pandas as pd
import xml.etree.ElementTree as ET
import ezpyai.llm.knowledge.exceptions as exceptions

from bs4 import BeautifulSoup
from typing import Dict
from PyPDF2 import PdfReader
from docx import Document
from ezpyai.llm.knowledge.knowledge_item import KnowledgeItem

_MIMETYPE_TEXT = "text/plain"
_MIMETYPE_JSON = "application/json"
_MIMETYPE_PDF = "application/pdf"
_MIMETYPE_DOCX = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
_MIMETYPE_ZIP = "application/zip"
_MIMETYPE_CSV = "text/csv"
_MIMETYPE_HTML = "text/html"
_MIMETYPE_XML = "text/xml"


class KnowledgeGatherer:
    """
    A class to gather knowledge from files within a directory or from a single file.

    This class supports reading and processing text, JSON, PDF, DOCX, and ZIP files,
    converting their content into plain text.
    It adds each file's data to the _items dictionary with its SHA256 hash as the key.

    Attributes:
        _items (Dict[str, KnowledgeItem]): A dictionary containing file paths
        and their processed content indexed by SHA256 hashes of the content.
    """

    def __init__(self):
        """Initialize the KnowledgeGatherer with an empty _items dictionary."""
        self._items: Dict[str, KnowledgeItem] = {}

        logging.debug("KnowledgeGatherer initialized with an empty _items dictionary.")

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(data={self._items.keys()})"

    def _get_knowledge_item_from_file_paragraph(
        self,
        file_path: str,
        paragraph: str,
        paragraph_number: int = 0,
    ) -> KnowledgeItem:
        """
        Get the knowledge item from the given file and paragraph content.

        Args:
            file_path (str): The path to the file.
            content (str): The content of the paragraph.

        Returns:
            KnowledgeItem: The knowledge item from the file and paragraph content.
        """
        logging.debug(
            f"Getting knowledge item from file: {file_path}, paragraph_number: {paragraph_number}"
        )

        file_dir = os.path.dirname(file_path)
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        file_ext = os.path.splitext(file_path)[1]

        return KnowledgeItem(
            content=paragraph,
            metadata={
                "file_dir": file_dir,
                "file_name": file_name,
                "file_ext": file_ext,
                "paragraph_number": paragraph_number,
            },
        )

    def _process_file(self, file_path: str):
        """
        Process the given file and add its data to the _items dictionary.

        Args:
            file_path (str): The path to the file.

        Raises:
            UnsupportedFileTypeError: If the file type is not supported.
            FileReadError: If there is an error reading the file.
        """
        logging.debug(f"Processing file: {file_path}")

        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(file_path)

        try:
            if _MIMETYPE_TEXT in mime_type:
                logging.debug(f"Processing file: {file_path} as {_MIMETYPE_TEXT}")

                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
            elif _MIMETYPE_JSON in mime_type:
                logging.debug(f"Processing file: {file_path} as {_MIMETYPE_JSON}")

                with open(file_path, "r", encoding="utf-8") as file:
                    content = json.dumps(json.load(file))
            elif _MIMETYPE_PDF in mime_type:
                logging.debug(f"Processing file: {file_path} as {_MIMETYPE_PDF}")

                reader = PdfReader(file_path)
                content = " ".join(page.extract_text() or "" for page in reader.pages)
            elif _MIMETYPE_DOCX in mime_type:
                logging.debug(f"Processing file: {file_path} as {_MIMETYPE_DOCX}")

                doc = Document(file_path)
                content = " ".join(para.text for para in doc.paragraphs if para.text)
            elif _MIMETYPE_CSV in mime_type:
                logging.debug(f"Processing file: {file_path} as {_MIMETYPE_CSV}")

                df = pd.read_csv(file_path)
                content = df.to_string()
            elif _MIMETYPE_HTML in mime_type:
                logging.debug(f"Processing file: {file_path} as {_MIMETYPE_HTML}")

                with open(file_path, "r", encoding="utf-8") as file:
                    soup = BeautifulSoup(file, "html.parser")
                    content = soup.get_text()
            elif _MIMETYPE_XML in mime_type:
                logging.debug(f"Processing file: {file_path} as {_MIMETYPE_XML}")

                tree = ET.parse(file_path)
                root = tree.getroot()
                content = "".join(root.itertext())
            elif _MIMETYPE_ZIP in mime_type:
                logging.debug(f"Processing file: {file_path} as {_MIMETYPE_ZIP}")

                self._process_zip(file_path)
                return
            else:
                raise exceptions.UnsupportedFileTypeError(
                    f"Unsupported file type for {file_path}"
                )
        except Exception as e:
            raise exceptions.FileReadError(
                f"Error reading {file_path}: {str(e)}"
            ) from e

        paragraphs = content.split("\n")
        paragraph_counter = 1
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            paragraph_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            self._items[paragraph_hash] = self._get_knowledge_item_from_file_paragraph(
                file_path=file_path,
                paragraph=paragraph,
                paragraph_number=paragraph_counter,
            )

            paragraph_counter += 1

            logging.debug(f"Added to data dictionary with key {paragraph_hash}")

        logging.debug(
            f"Processed file: {file_path} and added {len(paragraphs)} paragraphs to data dictionary"
        )

    def _process_zip(self, zip_path: str):
        """
        Extract a zip file to a temporary directory and process its contents.

        Args:
            zip_path (str): The path to the zip file.

        Raises:
            FileProcessingError: If an error occurs during the processing of the ZIP file.
        """
        logging.debug(f"Processing ZIP file: {zip_path}")

        temp_dir = tempfile.mkdtemp()

        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            self._process_directory(temp_dir)
        except Exception as e:
            raise exceptions.FileProcessingError(
                f"Error processing ZIP file {zip_path}: {str(e)}"
            ) from e
        finally:
            shutil.rmtree(temp_dir)

    def _process_directory(self, directory: str):
        """
        Recursively process all files in the specified directory.

        Args:
            directory (str): The path to the directory.
        """
        logging.debug(f"Processing directory: {directory}")

        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                self._process_file(file_path)

    def gather(self, file_path: str):
        """
        Determine if the given path is a directory or a file and process it accordingly.

        Args:
            file_path (str): The path to the file or directory.
        """
        logging.debug(f"Gathering data from: {file_path}")

        if os.path.isdir(file_path):
            self._process_directory(file_path)

            return

        self._process_file(file_path)

    def get_items(self) -> Dict[str, KnowledgeItem]:
        """
        Return the list of collected knowledge data

        Returns:
            Dict[str, KnowledgeItem]: A dictionary containing file paths
            and their processed content indexed by SHA256 hashes of the content.
        """
        return self._items
