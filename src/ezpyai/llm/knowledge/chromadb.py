import logging
import chromadb
import chromadb.utils.embedding_functions as ef

from typing import Dict, List
from ezpyai.llm.knowledge._knowledge import BaseKnowledge
from ezpyai.llm.knowledge._knowledge_gatherer import KnowledgeGatherer
from ezpyai.llm.knowledge.knowledge_item import KnowledgeItem

EMBEDDING_FUNCTION_ONNX_MINI_LM_L6_V2: ef.EmbeddingFunction = ef.ONNXMiniLM_L6_V2()


class ChromaDB(BaseKnowledge):
    """
    ChromaDB is a wrapper around the Chroma library for
    storing and retrieving embeddings from a Chroma database.
    """

    _client: chromadb.ClientAPI = None
    _embedding_function: ef.EmbeddingFunction = EMBEDDING_FUNCTION_ONNX_MINI_LM_L6_V2

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
            settings=chromadb.Settings(anonymized_telemetry=False),
        )

        self._embedding_function = embedding_function

        logging.debug(f"ChromaDB initialized with name={name} and dsn={dsn}")

    def __str__(self) -> str:
        return f"ChromaDB({super()})"

    def destroy(self) -> None:
        """Destroy the ChromaDB."""
        logging.debug("ChromaDB destroyed")

        self._client.reset()

    def store(self, collection: str, data_path: str) -> None:
        """
        Store the data in the given collection.

        Args:
            collection (str): The name of the collection.
            data_path (str): The path to the data.
        """
        logging.debug(f"Storing data in collection: {collection} from: {data_path}")

        knowledge_gatherer: KnowledgeGatherer = KnowledgeGatherer()
        knowledge_gatherer.gather(data_path)

        collection: chromadb.Collection = self._client.get_or_create_collection(
            name=collection,
            embedding_function=self._embedding_function,
        )

        knowledge_items = knowledge_gatherer.get_items()

        logging.debug(
            f"Storing {len(knowledge_items)} items in collection: {collection}"
        )

        document_ids: List[str] = []
        documents: List[str] = []
        metadatas: List[Dict[str, str]] = []

        for key, knowledge_item in knowledge_items.items():
            logging.debug(
                f"Pre-processing item: {key} in collection: {collection} with metadata: "
                f"{knowledge_item.metadata} and content length: {len(knowledge_item.content)}"
            )

            document_ids.append(key)
            documents.append(knowledge_item.content)
            metadatas.append(knowledge_item.metadata)

        collection.add(
            ids=document_ids,
            documents=documents,
            metadatas=metadatas,
        )

        logging.debug(
            f"Stored {len(document_ids)} items in collection: "
            f"{collection} with document IDs: {document_ids}"
        )

    def search(self, collection: str, query: str) -> List[KnowledgeItem]:
        """
        Search the collection for the given query.

        Args:
            collection (str): The name of the collection.
            query (str): The query to search for.

        Returns:
            List[KnowledgeItem]: The search results as a list of KnowledgeItem objects.
        """
        logging.debug(f"Searching collection: {collection} with query: {query}")

        collection: chromadb.Collection = self._client.get_or_create_collection(
            name=collection,
            embedding_function=self._embedding_function,
        )

        result: chromadb.QueryResult = collection.query(
            include=["documents", "metadatas"],
            query_texts=[query],
            n_results=2,
        )

        documents = result["documents"][0]
        metadatas = result["metadatas"][0]
        knowledge_items: List[KnowledgeItem] = []

        for i in range(len(documents)):
            knowledge_items.append(
                KnowledgeItem(
                    content=documents[i],
                    metadata=metadatas[i],
                )
            )

        return knowledge_items
