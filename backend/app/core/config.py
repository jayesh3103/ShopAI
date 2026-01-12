import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
    CHROMA_DB_DIR: str = os.path.join(os.getcwd(), "data", "chroma_db")
    COLLECTION_NAME: str = "product_manuals"
    
    # AI Models
    GEMINI_MODEL_SMART: str = "gemini-2.5-flash"
    GEMINI_MODEL_FAST: str = "gemini-2.5-flash"

    class Config:
        env_file = ".env"

settings = Settings()
