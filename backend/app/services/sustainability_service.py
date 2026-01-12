import logging
import json
import os
import requests
from PIL import Image
from io import BytesIO
from pathlib import Path
import google.generativeai as genai
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)

class SustainabilityService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def _load_image(self, image_url: str):
        """Loads image from local path or URL."""
        try:
            # Local Path (e.g., /static/images/...)
            if image_url.startswith("/static"):
                # Assuming backend run from project root
                relative_path = image_url.lstrip("/")
                full_path = Path(os.getcwd()) / "backend" / relative_path
                return Image.open(full_path)
            
            # External URL
            elif image_url.startswith("http"):
                response = requests.get(image_url)
                return Image.open(BytesIO(response.content))
            
            return None
        except Exception as e:
            logger.error(f"Image load failed: {e}")
            return None

    def calculate_eco_score(self, product_name: str, category: str, description: str, image_url: str = None) -> dict:
        """
        Multimodal Sustainability Audit.
        """
        try:
            inputs = []
            
            # Add Image if available
            if image_url:
                img = self._load_image(image_url)
                if img:
                    inputs.append(img)
                    logger.info("Image added to Eco-Audit.")

            prompt = f"""
            You are an expert Environmental Scientist & Sustainability Auditor.
            Conduct a rigorous MULTIMODAL AUDIT of this product.
            
            Product: {product_name}
            Category: {category}
            Description: {description}

            **Visual Audit Instructions:**
            1. Analyze the image for **Material Reality** (e.g., does "Eco-Wood" look like plastic?).
            2. Check for **Excessive Packaging** (blister packs, shrink wrap).
            
            **Deep Metrics Estimation (Use Industry Averages):**
            - **Carbon Footprint:** Estimate kg CO2e for this product type.
            - **Water Usage:** Estimate Liters used in production.

            **Output Strict JSON:**
            {{
                "score": [0-100],
                "label": "High Impact", "Moderate", "Eco-Friendly", or "Sustainable Choice",
                "color": "red", "yellow", or "green",
                "reason": "1 concise sentence summary.",
                "visual_audit": "What you detected from the image (e.g., 'Detected single-use plastic packaging').",
                "greenwashing_flag": boolean (True if marketing contradicts visual reality),
                "metrics": {{
                    "carbon_footprint": "e.g. 5.2 kg CO2e",
                    "water_usage": "e.g. 2000 L",
                    "recyclability": "e.g. Low - Mixed Materials"
                }},
                "pros": ["List 2 positive eco-factors"],
                "cons": ["List 2 negative eco-factors"],
                "tips": "1 actionable tip for disposal or better choice."
            }}
            """
            inputs.append(prompt)

            response = self.model.generate_content(inputs, generation_config={"response_mime_type": "application/json"})
            return json.loads(response.text)

        except Exception as e:
            logger.error(f"Eco-score calculation failed: {e}")
            return {
                "score": 50,
                "label": "Unknown",
                "color": "gray",
                "reason": "Could not analyze sustainability data.",
                "visual_audit": "Image analysis failed.",
                "greenwashing_flag": False,
                "metrics": {"carbon_footprint": "?", "water_usage": "?", "recyclability": "?"},
                "pros": [],
                "cons": [],
                "tips": "Check local recycling guidelines."
            }
