from fastapi import APIRouter, HTTPException, UploadFile, File
from backend.app.models.schema import Product, SearchRequest, ChatRequest, ChatResponse, SearchResponse
from backend.app.services.search import SearchService
from backend.app.services.chat import ChatService

router = APIRouter()

# Instantiate services once (singleton-ish)
search_service = SearchService()
chat_service = ChatService()

@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search for products by text query or image description.
    """
    if request.image_data:
        products, desc = search_service.search_by_image(request.image_data)
        return SearchResponse(products=products, ai_description=desc)
        
    if request.query:
        products = search_service.search_products(request.query)
        return SearchResponse(products=products, ai_description=None)
        
    return SearchResponse(products=[], ai_description=None)

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    RAG Chat with product manuals.
    """
    try:
        response_text, sources, visual_url = chat_service.chat(request.message, request.history)
        
        # Convert sources to dicts if they aren't already
        source_dicts = []
        for s in sources:
            source_dicts.append({
                "product_name": s.get("product_name"),
                "chunk_id": s.get("chunk_id")
            })
    
        return ChatResponse(
            response=response_text,
            sources=source_dicts,
            visual_aid_url=visual_url
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/external-search")
async def external_search(request: SearchRequest):
    """
    Search for products online via SerpApi.
    """
    from backend.app.services.serp_service import search_products_online
    
    # We use the 'query' field from SearchRequest
    if request.query:
        return search_products_online(request.query)
    return []

# --- Admin Endpoints ---
from backend.app.services.admin import AdminService
admin_service = AdminService()

@router.post("/admin/analyze")
async def analyze_product(request: SearchRequest):
    """
    Analyze generic image for cataloging. Uses SearchRequest.image_data
    """
    if request.image_data:
        return admin_service.analyze_product_image(request.image_data)
    return {"error": "No image provided"}

@router.post("/admin/add-product")
async def add_product(product: dict):
    """
    Save validated product to database and index it.
    """
    # 1. Save to JSON
    result = admin_service.save_product(product)
    
    # 2. Index to Chroma (Real-time compatibility)
    if result.get("status") == "success":
        search_service.index_product(product)
        
    return result

# --- Compare Endpoints ---
from backend.app.services.compare import CompareService
from typing import List
from backend.app.models.schema import Product

compare_service = CompareService()

@router.post("/compare")
async def compare_products(products: List[dict]):
    """
    Generate markdown comparison for list of products.
    """
    return {"markdown": compare_service.compare_products(products)}

# --- Sustainability Endpoint ---
from backend.app.services.sustainability_service import SustainabilityService
from backend.app.models.schema import SustainabilityRequest

sustainability_service = SustainabilityService()

@router.post("/eco-score")
async def get_eco_score(request: SustainabilityRequest):
    """
    Calculate sustainability score for a product.
    """
    return sustainability_service.calculate_eco_score(
        request.product_name, 
        request.category, 
        request.description
    )
