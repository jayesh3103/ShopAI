from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend.app.core.config import settings

def get_embeddings_service():
    if not settings.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is not set in environment or .env file.")
    
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=settings.GOOGLE_API_KEY
    )
