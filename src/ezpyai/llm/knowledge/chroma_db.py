import chromadb
import chromadb.utils.embedding_functions as ef

from typing import Dict, List
from ezpyai._logger import logger
from ezpyai.constants import DICT_KEY_SUMMARY
from ezpyai.llm.providers._llm_provider import LLMProvider
from ezpyai.llm.knowledge._knowledge_db import BaseKnowledgeDB
from ezpyai.llm.knowledge._knowledge_gatherer import KnowledgeGatherer
from ezpyai.llm.knowledge.knowledge_item import KnowledgeItem


EMBEDDING_FUNCTION_ONNX_MINI_LM_L6_V2: ef.EmbeddingFunction = ef.ONNXMiniLM_L6_V2()


class ChromaDB(BaseKnowledgeDB):
    """
    ChromaDB is a wrapper around the Chroma library for
    storing and retrieving embeddings from a Chroma database.
    """

    def __init__(
        self,
        name: str,
        dsn: str,
        embedding_function: ef.EmbeddingFunction = EMBEDDING_FUNCTION_ONNX_MINI_LM_L6_V2,
    ) -> None:
        """
        Initialize the ChromaDB with the given name, dsn and embedding
        function(default: EMBEDDING_FUNCTION_ONNX_MINI_LM_L6_V2).
        """
        super().__init__(name, dsn)

        self._client = chromadb.PersistentClient(
            path=dsn,
            settings=chromadb.Settings(
                allow_reset=True,
                anonymized_telemetry=False,
            ),
        )

        self._embedding_function = embedding_function

        logger.debug(f"ChromaDB initialized with name={name} and dsn={dsn}")

    def destroy(self) -> None:
        """Destroy the ChromaDB."""
        logger.debug("ChromaDB destroyed")

        self._client.reset()

    def store(
        self, collection: str, data_path: str, summarizer: LLMProvider = None
    ) -> None:
        """
        Store the data in the given collection.

        Args:
            collection (str): The name of the collection.
            data_path (str): The path to the data.
            summarizer (LLMProvider): The LLMProvider summarizer to use for knowledge collection.
        """
        logger.debug(f"Storing data in collection: {collection} from: {data_path}")

        knowledge_gatherer: KnowledgeGatherer = KnowledgeGatherer(
            summarizer=summarizer,
        )

        knowledge_gatherer.gather(data_path)
        knowledge_items = knowledge_gatherer.get_items()

        logger.debug(f"Collected knowlege items: {knowledge_items}")

        collection: chromadb.Collection = self._client.get_or_create_collection(
            name=collection,
            embedding_function=self._embedding_function,
        )

        logger.debug(
            f"Storing {len(knowledge_items)} items in collection: {collection}"
        )

        document_ids: List[str] = []
        documents: List[str] = []
        metadatas: List[Dict[str, str]] = []

        for _, knowledge_item in knowledge_items.items():
            logger.debug(f"Pre-processing item: {knowledge_item}")

            metadata = knowledge_item.metadata
            metadata[DICT_KEY_SUMMARY] = knowledge_item.summary

            document_ids.append(knowledge_item.id)
            documents.append(knowledge_item.content)
            metadatas.append(metadata)

        collection.add(
            ids=document_ids,
            documents=documents,
            metadatas=metadatas,
        )

        logger.debug(
            f"Stored {len(document_ids)} items in collection: "
            f"{collection} with document IDs: {document_ids}"
        )

    def search(
        self,
        collection: str,
        query: str,
        num_results: int = 1,
    ) -> List[KnowledgeItem]:
        """
        Search the collection for the given query.

        Args:
            collection (str): The name of the collection.
            query (str): The query to search for.

        Returns:
            List[KnowledgeItem]: The search results as a list of KnowledgeItem objects.
        """
        logger.debug(f"Searching collection: {collection} with query: {query}")

        collection: chromadb.Collection = self._client.get_or_create_collection(
            name=collection,
            embedding_function=self._embedding_function,
        )

        result: chromadb.QueryResult = collection.query(
            include=["documents", "metadatas"],
            query_texts=[query],
            n_results=num_results,
        )

        ids = result["ids"][0]
        documents = result["documents"][0]
        metadatas = result["metadatas"][0]
        knowledge_items: List[KnowledgeItem] = []

        for i in range(len(documents)):
            summary = ""
            if DICT_KEY_SUMMARY in metadatas[i]:
                summary = metadatas[i].pop(DICT_KEY_SUMMARY, "")

            knowledge_items.append(
                KnowledgeItem(
                    id=ids[i],
                    content=documents[i],
                    summary=summary,
                    metadata=metadatas[i],
                )
            )

        return knowledge_items
