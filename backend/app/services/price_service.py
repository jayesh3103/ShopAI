import logging
import json
from datetime import datetime
import google.generativeai as genai
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)

class PriceService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def predict_price_trend(self, product_name: str, current_price: float, category: str = "") -> dict:
        """
        Analyzes market trends to predict price movement.
        """
        try:
            today_date = datetime.now().strftime("%Y-%m-%d")
            
            prompt = f"""
            You are an expert Market Analyst AI.
            Predict the short-term price trend for this product.

            Product: {product_name}
            Category: {category}
            Current Price: {current_price}
            Date: {today_date}

            Analyze factors:
            1. Seasonality (e.g., Electronics, Clothes).
            2. Product Lifecycle (Is a new version coming?).
            3. Upcoming Sales Events (Black Friday, Prime Day, Regional Festivals).

            Output strict JSON:
            {{
                "recommendation": "BUY_NOW" or "WAIT",
                "confidence": [0-100],
                "reason": "Short explanation (max 2 sentences). If product is Indian or context implies India, use Hinglish/Indian context.",
                "predicted_drop": "e.g., 'Likely 10% drop in 2 weeks' or 'Stable'"
            }}
            """

            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            result = json.loads(response.text)
            return result

        except Exception as e:
            logger.error(f"Price prediction failed: {e}")
            return {
                "recommendation": "BUY_NOW", # Fallback to Buy
                "confidence": 0,
                "reason": "Could not analyze market data at this moment.",
                "predicted_drop": "Unknown"
            }
