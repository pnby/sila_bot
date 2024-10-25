import asyncio
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import override, List

from FlagEmbedding import BGEM3FlagModel
from docx import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from qdrant_client.http.models import UpdateResult

from app.bot.api.ollama.impl.ollama import Ollama
from app.bot.api.rag.base_rag import BaseRAGProcessor
from app.bot.config import UPLOADS_DIR, user_prompt, system_prompt
from app.bot.utils.singleton import singleton


@singleton
class RAGProcessor(BaseRAGProcessor):
    def __init__(self, coll_name: str = 'test', qdrant_host: str = 'qdrant', qdrant_port: int = 6333):
        super().__init__(coll_name, qdrant_host, qdrant_port)
        self.encoder = BGEM3FlagModel('USER-bge-m3', device='cuda')
        self.qdrant_client = QdrantClient(qdrant_host, port=qdrant_port)
        self.coll_name = coll_name
        self.prompt_temp = user_prompt

    @override
    def get_emb(self, sentence: str) -> list:
        emb = self.encoder.encode(sentence)['dense_vecs']
        return emb

    @override
    def process_docx(self, file_path: str, sep: list, chunk_size: int, chunk_overlap: int) -> None:
        doc = Document(file_path)
        content = "\n".join([p.text for p in doc.paragraphs])
        chunks = self.content_to_chunks(content, sep, chunk_size, chunk_overlap)
        embs = [self.get_emb(chunk) for chunk in chunks]
        self.chunks_to_vecdb(chunks, embs)

    @override
    def content_to_chunks(self, content: str, sep: list, chunk_size: int, chunk_overlap: int) -> List[str]:
        cleaned_content = content.replace('\n', ' ').replace('\r', '').strip()
        text_splitter = RecursiveCharacterTextSplitter(
            separators=sep,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
            add_start_index=False
        )
        return text_splitter.split_text(cleaned_content)

    @override
    def chunks_to_vecdb(self, chunks: List[str], embs: List[list]) -> UpdateResult:
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=[x / (sum(emb) + 1e-9) for x in emb],
                payload={'chunk': chunk}
            )
            for chunk, emb in zip(chunks, embs)
        ]
        return self.qdrant_client.upsert(
            collection_name=self.coll_name,
            wait=True,
            points=points
        )

    @override
    def vec_search(self, query: str, n_top_cos: int) -> List[str]:
        query_emb = self.get_emb(query)
        potential_chunks = self.qdrant_client.search(
            collection_name=self.coll_name,
            query_vector=query_emb,
            limit=50,
            with_vectors=True
        )
        filtered_chunks = [
            x.payload['chunk'] for x in potential_chunks
            if query.lower() in x.payload['chunk'].lower()
        ]
        return filtered_chunks[:n_top_cos] or [
            x.payload['chunk'] for x in potential_chunks[:n_top_cos]
        ]

    @override
    def get_prompt(self, top_chunks: List[str], query: str) -> str:
        chunks_join = '\n'.join(top_chunks)
        return self.prompt_temp.format(chunks_join=chunks_join, query=query)

    @override
    async def llm_request(self, prompt: str) -> str:
        ollama = Ollama(prompt, system_prompt=system_prompt)
        await ollama.send_request()
        return ollama.get_formatted_response()

    @override
    def initialize_collection(self) -> None:
        self.qdrant_client.delete_collection(collection_name=self.coll_name)
        self.qdrant_client.create_collection(
            collection_name=self.coll_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )

    @override
    async def query_docx(self, query: str, n_top_cos: int) -> str:
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as executor:
            top_chunks = await loop.run_in_executor(executor, self.vec_search, query, n_top_cos)
        prompt = self.get_prompt(top_chunks, query)
        return await self.llm_request(prompt)

    def load_all_documents(self, directory: str, sep: list, chunk_size: int, chunk_overlap: int) -> None:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.docx'):
                    file_path = os.path.join(root, file)
                    self.process_docx(file_path, sep, chunk_size, chunk_overlap)


processor = RAGProcessor()

def load_documents():
    processor.initialize_collection()
    processor.load_all_documents(UPLOADS_DIR, ['\n\n', '\n'], 500, 300)