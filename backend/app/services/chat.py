import logging
import google.generativeai as genai
from typing import List, Tuple, Optional
from backend.app.core.config import settings
from backend.app.services.vector_db import get_collection
from backend.app.services.embeddings import get_embeddings_service
from backend.app.services.asset_index import AssetIndex

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)

class ChatService:
    def __init__(self):
        self.collection = get_collection()
        self.embedding_service = get_embeddings_service()
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL_SMART)
        self.asset_index = AssetIndex()

    def _retrieve_context(self, query: str, limit: int = 5) -> Tuple[str, List[dict]]:
        """Retrieve relevant manual chunks."""
        try:
            query_embedding = self.embedding_service.embed_query(query)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where={"type": "manual"}
            )
            
            context_text = ""
            sources = []
            
            if results["ids"]:
                for i in range(len(results["ids"][0])):
                    doc_text = results["documents"][0][i]
                    metadata = results["metadatas"][0][i]
                    context_text += f"[Product: {metadata['product_name']}] {doc_text}\n\n"
                    sources.append(metadata)
            
            return context_text, sources
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return "", []

    def chat(self, message: str, history: List[dict] = []) -> Tuple[str, List[dict], Optional[str]]:
        """
        RAG Chat with Visual Aid detection.
        Returns: (response_text, sources, visual_aid_url)
        """
        
        context, sources = self._retrieve_context(message)
        available_assets = list(self.asset_index._ASSETS.keys())
        
        system_prompt = f"""You are a **Senior Product Support Engineer** for ShopAI, a premium e-commerce platform.
        
        ## Your Knowledge Base (Strict Context):
        {context}
        
        ## Available Visual Guides:
        {available_assets}
        
        ## Instructions:
        1. **Grounding:** Answer the user's question using **ONLY** the information provided in the "Knowledge Base" above. Do not invent features or procedures.
        2. **Verification:** If the answer is not in the context, politely state: "I consulted the product manuals, but I couldn't find specific information on that. Could you verify the product model?"
        3. **Tone:** Professional, empathetic, and technical but accessible.
        4. **Language:** 
           - If the user writes in Hindi/Hinglish, reply in **Hinglish**.
           - Otherwise, reply in Standard English.
        5. **Visual Aid Protocol:** 
           - If a "Visual Guide" listed above directly helps solve the user's issue (e.g., "how to clean filter"), append the tag `<VIDEO:key>` at the *very end* of your response.
           - Example: "You can remove the dust bin by sliding the latch... <VIDEO:cleaning_guide>"
        
        ## Reasoning Process:
        - First, analyze the User's question.
        - Second, scan the Knowledge Base for matches.
        - Third, formulate the answer.
        """
        
        # Start a chat session
        chat_session = self.model.start_chat(history=history or [])
        
        # Send message with context
        full_prompt = f"{system_prompt}\n\nUser Question: {message}"
        response = chat_session.send_message(full_prompt)
        text_response = response.text
        
        # Parse Visual Aid Tag
        visual_aid_url = None
        if "<VIDEO:" in text_response:
            try:
                # Extract key
                start = text_response.find("<VIDEO:") + 7
                end = text_response.find(">", start)
                video_key = text_response[start:end]
                
                # Get URL
                visual_aid_url = self.asset_index.get_visual_aid(video_key)
                
                # Remove tag from user-facing text
                text_response = text_response.replace(f"<VIDEO:{video_key}>", "").strip()
            except Exception as e:
                logger.error(f"Error parsing video tag: {e}")
        
        return text_response, sources, visual_aid_url
