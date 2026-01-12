import google.generativeai as genai
import logging
from typing import List
from backend.app.core.config import settings

logger = logging.getLogger(__name__)
genai.configure(api_key=settings.GOOGLE_API_KEY)

class CompareService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-flash-latest')

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
        You are a smart shopping assistant. Create a detailed Comparison Table for these products.

        Products Info:
        {products_text}

        Instructions:
        1. Output a Markdown Table.
        2. Columns: Product Name, Price (in ₹), Key Features, Pros, Cons, Best For.
        3. Highlight the "Best Value" choice in **bold green** within the table if possible, or mention it in a summary below.
        4. Be concise.
        5. IMPORTANT: Display all prices in Indian Rupees (₹).
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Comparison generation failed: {e}")
            return "Sorry, I couldn't generate the comparison at this moment."
