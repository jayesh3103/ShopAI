import json
import os
import sys

# Ensure backend imports work
sys.path.append(os.getcwd())

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.app.services.vector_db import get_collection
from backend.app.services.embeddings import get_embeddings_service
from backend.app.core.config import settings

def ingest_data():
    print("🚀 Starting ingestion process...")
    
    # 1. Load Data
    data_path = os.path.join("data", "products.json")
    if not os.path.exists(data_path):
        print(f"❌ Error: {data_path} not found. Run scripts/create_mock_data.py first.")
        return

    with open(data_path, "r") as f:
        products = json.load(f)

    # 2. Prepare Documents
    documents = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    print(f"📦 Processing {len(products)} products...")

    for product in products:
        # Index Description (for semantic search)
        if product.get("description"):
            doc = Document(
                page_content=product["description"],
                metadata={
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "price": product["price"],
                    "image_url": product["image_url"],
                    "type": "description"
                }
            )
            documents.append(doc)

        # Index Manual (for RAG)
        manual_text = product.get("manual_text", "")
        if manual_text:
            chunks = text_splitter.split_text(manual_text)
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "product_id": product["id"],
                        "product_name": product["name"],
                        "type": "manual",
                        "chunk_id": i
                    }
                )
                documents.append(doc)

    print(f"📄 Prepared {len(documents)} document chunks.")

    # 3. Embedding & Indexing
    try:
        embedding_service = get_embeddings_service()
        collection = get_collection()
        
        # Prepare lists for ChromaDB
        # Generate unique IDs including type to avoid collisions
        ids = []
        for doc in documents:
            if doc.metadata['type'] == 'description':
                 ids.append(f"{doc.metadata['product_id']}_desc")
            else:
                 ids.append(f"{doc.metadata['product_id']}_manual_{doc.metadata['chunk_id']}")
                 
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        print("🧠 Generating embeddings...")
        embeddings = embedding_service.embed_documents(texts)
        
        print("💾 Storing in ChromaDB...")
        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
        # 4. Test / Verify
        count = collection.count()
        print(f"✅ Success! Collection now has {count} documents.")
        
        # Optional: Peek at one result
        # print("Peek:", collection.peek(limit=1))
        
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        print("💡 Hint: Check your GOOGLE_API_KEY in .env")

if __name__ == "__main__":
    ingest_data()
