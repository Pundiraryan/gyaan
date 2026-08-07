from qdrant_client import QdrantClient
import os

class VectorStore:
    def __init__(self):
        self.host = os.getenv("QDRANT_HOST", "localhost")
        self.port = int(os.getenv("QDRANT_PORT", "6333"))
        self.client = QdrantClient(host=self.host, port=self.port)
        self.collection_name = os.getenv("QDRANT_COLLECTION", "gyaan_concepts")

    def ensure_collection(self):
        if self.collection_name not in [collection.name for collection in self.client.get_collections().collections]:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vector_size=1536,
                distance="Cosine",
            )

    def upsert_vectors(self, points):
        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(self, query_vector, limit=10):
        return self.client.search(collection_name=self.collection_name, query_vector=query_vector, limit=limit)
