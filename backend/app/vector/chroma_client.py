import chromadb
from app.core.config import settings
import uuid

class ChromaClient:
    def __init__(self):
        # Use settings for host and port
        self.client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        # Get or create a default collection for document chunks
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, document_id: int, chunks: list[str], embeddings: list[list[float]]):
        if not chunks:
            return
            
        ids = [f"{document_id}_{i}" for i in range(len(chunks))]
        metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )

    def query(self, query_embedding: list[float], n_results: int = 5):
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        # Returns a dict with 'ids', 'distances', 'metadatas', 'embeddings', 'documents'
        # We generally care about 'documents'
        if not results['documents']:
            return []
        return results['documents'][0]

chroma_client = ChromaClient()
