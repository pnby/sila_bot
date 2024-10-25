from abc import ABC, abstractmethod
from typing import List

from qdrant_client.http.models import UpdateResult

class BaseRAGProcessor(ABC):
    def __init__(self, coll_name: str, qdrant_host: str, qdrant_port: int):
        """
        Initialize the BaseRAGProcessor class.

        :param coll_name: Name of the collection in Qdrant.
        :param qdrant_host: Host of the Qdrant server.
        :param qdrant_port: Port of the Qdrant server.
        """
        self.coll_name = coll_name
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port

    @abstractmethod
    def get_emb(self, sentence: str) -> list:
        """
        Convert a sentence to a vector.

        :param sentence: The sentence to convert.
        :return: The vector representation of the sentence.
        """

    @abstractmethod
    def process_docx(self, file_path: str, sep: list, chunk_size: int, chunk_overlap: int) -> None:
        """
        Processes a .docx file by extracting its content, splitting it into chunks,
        and storing the chunk vectors in the vector database.

        :param file_path: The path to the .docx file.
        :param sep: A list of separators to use when splitting the text into chunks.
        :param chunk_size: The size of each text chunk.
        :param chunk_overlap: The overlap between chunks.

        Returns:
            None
        """

    @abstractmethod
    def content_to_chunks(self, content: str, sep: list, chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        Split the content into chunks.

        :param content: The content to split.
        :param sep: List of separators.
        :param chunk_size: Size of each chunk.
        :param chunk_overlap: Overlap between chunks.
        :return: List of chunks.
        """

    @abstractmethod
    def chunks_to_vecdb(self, chunks: List[str], embs: List[list]) -> UpdateResult:
        """
        Insert chunks and their vector representations into the vector database.

        :param chunks: List of chunks.
        :param embs: List of vector representations.
        :return: Operation info from the vector database.
        """

    @abstractmethod
    def vec_search(self, query: str, n_top_cos: int) -> List[str]:
        """
        Search for chunks similar to the query.

        :param query: The query string.
        :param n_top_cos: Number of top results to return.
        :return: List of top chunks.
        """

    @abstractmethod
    def get_prompt(self, top_chunks: List[str], query: str) -> str:
        """
        Generate a prompt from the top chunks and query.

        :param top_chunks: List of top chunks.
        :param query: The query string.
        :return: The generated prompt.
        """

    @abstractmethod
    async def llm_request(self, prompt: str) -> str:
        """
        Send a request to the LLM.

        :param prompt: The prompt to send.
        :return: The response from the LLM.
        """

    @abstractmethod
    def initialize_collection(self) -> None:
        """
        Initialize the collection in the vector database.

        :return: None
        """

    @abstractmethod
    async def query_docx(self, query: str, n_top_cos: int) -> str:
        """
        Query the DOCX content and get an answer from the LLM.

        :param query: The query string.
        :param n_top_cos: Number of top results to return.
        :return: The answer from the LLM.
        """