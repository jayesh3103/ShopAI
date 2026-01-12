import google.generativeai as genai
import logging
from typing import List
from backend.app.core.config import settings

logger = logging.getLogger(__name__)
genai.configure(api_key=settings.GOOGLE_API_KEY)

class CompareService:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL_SMART)

    def compare_products(self, products: List[dict]) -> str:
        """
        Generates a Markdown comparison table for the given list of products.
        """
        if not products or len(products) < 2:
            return "Please select at least 2 products to compare."

        # Construct context for the prompt
        products_text = ""
        for p in products:
            products_text += f"""
            Product: {p.get('name')}
            Price: {p.get('price')}
            Description: {p.get('description')}
            Manual/Features: {p.get('manual_text', '')}
            ---
            """

        prompt = f"""
        You are a **Consumer Research Expert** (like Wirecutter or RTINGS).
        Create a decisive comparison table for these products to help a buyer choose.

        ## PRODUCTS
        {products_text}

        ## INSTRUCTIONS
        1. **Verdict-First Approach:** The first row must be the "Verdict" (e.g., "Winner", "Runner-up", "Best Value").
        2. **Markdown Table:** Use strict Markdown.
        3. **Currency:** All prices in INR (₹).
        4. **Columns:** Verdict, Product, Price, Key Specs, Real-World Performance, Best For (Persona).
        
        ## STYLE GUIDE
        - Be objective but opinionated.
        - Highlight the winner's name in **Bold Green**.
        - Highlight the runner-up's name in **Bold Orange**.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Comparison generation failed: {e}")
            return "Sorry, I couldn't generate the comparison at this moment."
