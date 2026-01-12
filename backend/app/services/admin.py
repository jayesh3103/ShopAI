import google.generativeai as genai
import json
import logging
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)

class AdminService:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL_SMART)

    def analyze_product_image(self, image_b64: str):
        """
        Analyzes an image and returns structured product metadata.
        """
        try:
            prompt = """
            You are a **Senior Catalog Specialist** for a luxury e-commerce platform.
            
            ## MISSION
            Transform this raw product image into a high-converting catalog entry.

            ## OUTPUT FORMAT (Strict JSON)
            {
                "name": "Professional, catchy product title (Max 10 words).",
                "category": "Precise taxonomy (e.g., 'Men's Footwear', 'Smart Home').",
                "description": "2-3 sentences of persuasive copy focusing on benefits and lifestyle appeal. Use premium vocabulary.",
                "features": ["Feature 1", "Feature 2", "Feature 3"],
                "estimated_price_inr": 0000 (Number only, realistic market estimate in Rupees),
                "seo_tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
                "seo_meta": "Concise meta description for search engines (Max 160 chars).",
                "material": "Detailed material composition (e.g., 'Aerospace-grade Aluminum', 'Organic Cotton').",
                "sustainability_rating": [1-10] (1=Toxic, 10=Regenerative)
            }
            
            Ensure the output is valid JSON.
            """
            
            response = self.model.generate_content([
                {'mime_type': 'image/jpeg', 'data': image_b64},
                prompt
            ])
            
            # extract json from response
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {"error": str(e)}

    def save_product(self, product_data: dict):
        """
        Saves the new product to products.json (and ideally ChromaDB).
        For prototype, we just append to products.json.
        """
        try:
            file_path = "data/products.json"
            with open(file_path, "r") as f:
                products = json.load(f)
            
            products.append(product_data)
            
            with open(file_path, "w") as f:
                json.dump(products, f, indent=4)
                
            return {"status": "success", "message": "Product saved successfully!"}
        except Exception as e:
            logger.error(f"Save failed: {e}")
            return {"status": "error", "message": str(e)}
