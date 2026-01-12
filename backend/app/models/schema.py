from pydantic import BaseModel, Field
from typing import List, Optional

class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    image_url: str
    link: str = "#" # Default link to prevent KeyError
    score: float = 0.0

class SearchRequest(BaseModel):
    query: Optional[str] = None
    image_data: Optional[str] = None # Base64 encoded image

class ChatRequest(BaseModel):
    message: str
class ChatResponse(BaseModel):
    response: str
    sources: List[dict] = []
    visual_aid_url: Optional[str] = None

class SearchResponse(BaseModel):
    products: List[Product]
    ai_description: Optional[str] = None

class SustainabilityRequest(BaseModel):
    product_name: str
    category: str
    description: str
    image_url: Optional[str] = None
