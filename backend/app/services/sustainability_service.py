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
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL_SMART)

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
            You are a **Lead Environmental Auditor** for a global certification body (like LEED or B Corp).
            Conduct a forensic **MULTIMODAL SUSTAINABILITY AUDIT** on:
            
            - **Product:** {product_name}
            - **Category:** {category}
            - **Claims:** {description}

            ## AUDIT PROTOCOL
            1. **Visual Packaging Inspection:** Scrutinize the image (if present) for non-recyclable materials (blister packs, styrofoam) vs eco-claims.
            2. **Material Reality Check:** Does "Vegan Leather" visually match PVC/Plastic or actual organic material?
            3. **Lifecycle Simulation:** Estimate the carbon cost from extraction to landfill.

            ## OUTPUT FORMAT (Strict JSON)
            {{
                "score": [0-100] (Be strict. 100 is impossible, 80 is rare),
                "label": "High Impact" | "Moderate" | "Eco-Friendly" | "Gold Standard",
                "color": "red" | "yellow" | "green" | "#0ea5e9" (Cyan for Gold),
                "reason": "Professional audit summary. Call out hypocrisies explicitly.",
                "visual_audit": "Detailed observations from the image (e.g., 'Excessive void-fill detected').",
                "greenwashing_flag": boolean (TRUE if marketing 'Eco' claims don't match material reality),
                "metrics": {{
                    "carbon_footprint": "Estimated kg CO2e (Scientific Estimate)",
                    "water_usage": "Estimated Liters (Scientific Estimate)",
                    "recyclability": "High/Medium/Low (with material justification)"
                }},
                "pros": ["Eco-Factor 1", "Eco-Factor 2"],
                "cons": ["Major Concern 1", "Major Concern 2"],
                "tips": "One expert recommendation for sustainable usage or disposal."
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
