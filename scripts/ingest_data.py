import json
import os
import sys

# Add the project root to the python path to allow imports from backend
sys.path.append(os.getcwd())

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.app.services.vector_db import get_collection
from backend.app.services.embeddings import get_embeddings_service

def ingest_data():
    # 1. Load Data
    data_path = os.path.join("data", "products.json")
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Run create_mock_data.py first.")
        return

    with open(data_path, "r") as f:
        products = json.load(f)

    # 2. Prepare Documents
    documents = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    for product in products:
        manual_text = product.get("manual_text", "")
        if not manual_text:
            continue
            
        chunks = text_splitter.split_text(manual_text)
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "chunk_id": i
                }
            )
            documents.append(doc)

    print(f"Prepared {len(documents)} document chunks from {len(products)} products.")

    # 3. Embedding & Indexing
    try:
        embedding_service = get_embeddings_service()
        collection = get_collection()
        
        # Prepare data for ChromaDB
        ids = [f"{doc.metadata['product_id']}_{doc.metadata['chunk_id']}" for doc in documents]
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        # Generate embeddings
        print("Generating embeddings... This may take a moment.")
        embeddings = embedding_service.embed_documents(texts)
        
        # Add to collection
        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
        print(f"Successfully indexed {len(documents)} chunks into ChromaDB.")
        
    except Exception as e:
        print(f"Error during ingestion: {e}")
        print("Please ensure your GOOGLE_API_KEY is set correctly in .env")

if __name__ == "__main__":
    ingest_data()
