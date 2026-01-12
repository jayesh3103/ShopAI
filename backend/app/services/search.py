import logging
import google.generativeai as genai
from typing import List
from backend.app.services.vector_db import get_collection
from backend.app.services.embeddings import get_embeddings_service
from backend.app.models.schema import Product
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        self.collection = get_collection()
        self.embedding_service = get_embeddings_service()

    def search_products(self, query: str, limit: int = 5) -> List[Product]:
        """
        Search for products by description using semantic search.
        """
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_service.embed_query(query)
            
            # Query ChromaDB for descriptions
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where={"type": "description"} # Filter by type
            )
            
            products = []
            if results["ids"]:
                for i in range(len(results["ids"][0])):
                    metadata = results["metadatas"][0][i]
                    # In a real app, we might fetch full product details from a SQL DB here
                    # For now, we reconstruct from what we have or just return basics
                    # Since we don't store image_url in chroma metadata, we'll need to fetch it 
                    # from our products.json or add it to metadata during ingest.
                    # For MVP, let's just return what we have in metadata.
                    
                    products.append(Product(
                        id=metadata["product_id"],
                        name=metadata["product_name"],
                        description=results["documents"][0][i],
                        price=metadata.get("price", 0.0),
                        image_url=metadata.get("image_url", ""),
                        link=metadata.get("link", f"https://www.google.com/search?q={metadata['product_name']}"), # Fallback to Google Search
                        score=results["distances"][0][i] if results["distances"] else 0.0
                    ))
            
            return products
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
            
    def search_by_image(self, image_data: str, limit: int = 5) -> tuple[List[Product], str]:
        """
        Search using the description generated from an image.
        Returns: (List[Products], generated_description)
        """
        try:
            # Generate description using Gemini
            model = genai.GenerativeModel(settings.GEMINI_MODEL_SMART)
            
            # Simple prompt
            prompt = "Describe this product in detail so I can find similar items. Focus on category, color, material, and key features. Return a single paragraph description."
            
            # Create the image part (assuming standard base64 from frontend)
            # We need to clean the base64 string if it has headers
            if "base64," in image_data:
                image_data = image_data.split("base64,")[1]
                
            image_part = {
                "mime_type": "image/jpeg", 
                "data": image_data
            }
            
            response = model.generate_content([prompt, image_part])
            description = response.text
            
            logger.info(f"Generated Image Description: {description}")
            
            # Search using the description
            return self.search_products(description, limit), description
            
        except Exception as e:
            logger.error(f"Image search failed: {e}")
            return [], "Error analyzing image."
    def index_product(self, product: dict):
        """
        Add a single product to the ChromaDB index immediately.
        """
        try:
            # Generate embedding
            text_to_embed = f"{product['name']} - {product['description']} - {product['category']}"
            embedding = self.embedding_service.embed_query(text_to_embed)
            
            # Prepare metadata (flat dict)
            # Ensure all values are strings, ints, or floats
            metadata = {
                "product_id": product['id'],
                "product_name": product['name'],
                "price": float(product['price']),
                "image_url": product['image_url'],
                "link": product.get("link", "#"),
                "category": product.get("category", ""),
                "type": "description"
            }
            
            # Add to collection
            self.collection.add(
                ids=[product['id']],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[product['description']]
            )
            logger.info(f"Indexed product: {product['name']}")
            return True
        except Exception as e:
            logger.error(f"Indexing failed: {e}")
            return False
