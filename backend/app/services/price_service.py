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
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL_SMART)

    def predict_price_trend(self, product_name: str, current_price: float, category: str = "") -> dict:
        """
        Analyzes market trends to predict price movement.
        """
        try:
            today_date = datetime.now().strftime("%Y-%m-%d")
            
            prompt = f"""
            You are a **Senior Market Analyst** at a top-tier investment firm, specializing in retail commodities.
            
            ## OBJECTIVE
            Forecast the short-term price trajectory for the following asset.

            ## ASSET DATA
            - **Product:** {product_name}
            - **Category:** {category}
            - **Current Price:** {current_price}
            - **Analysis Date:** {today_date}

            ## ANALYTICAL FRAMEWORK
            1. **Seasonality Protocol:** deeply analyze if this item is currently in-season or off-season (e.g., ACs in Winter, Wool in Summer).
            2. **Lifecycle Check:** Is a newer model likely launching soon? (Depreciating current stock).
            3. **Event Horizon:** Check for upcoming major sales events (Diwali, Black Friday, Great Indian Festival) relative to today's date.

            ## OUTPUT FORMAT (Strict JSON)
            {{
                "recommendation": "BUY_NOW" | "WAIT",
                "confidence": [0-100],
                "reason": "Expert analysis in 2 sentences. Focus on the *why*. Use professional financial tone mixed with consumer advice. If context implies India, use Hinglish nuances.",
                "predicted_drop": "Specific prediction, e.g., 'Expect 15% correction by [Month]' or 'Prices stabilizing'."
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
