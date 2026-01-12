import chromadb
from backend.app.core.config import settings

def get_chroma_client():
    return chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)

def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(name=settings.COLLECTION_NAME)
