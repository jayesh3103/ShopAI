import google.generativeai as genai
import json
import logging
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)

class AdminService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def analyze_product_image(self, image_b64: str):
        """
        Analyzes an image and returns structured product metadata.
        """
        try:
            prompt = """
            Analyze this product image for an e-commerce catalog.
            Return a JSON object with the following fields:
            - name: A catchy, professional product title.
            - category: The main category (e.g., Footwear, Electronics).
            - description: A compelling marketing description (2-3 sentences).
            - features: A list of 3 key features.
            - estimated_price_inr: A realistic estimated price in Indian Rupees (number only).
            - seo_tags: A list of 5-7 SEO keywords/tags.
            - seo_meta: A concise meta description for search engines (max 160 chars).
            - material: Best guess at material composition (e.g., "100% Cotton", "Plastic & Metal").
            - sustainability_rating: Estimate eco-friendliness 1-10 (1=Bad, 10=Green).
            
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
