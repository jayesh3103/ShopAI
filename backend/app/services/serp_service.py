from serpapi import GoogleSearch
from backend.app.core.config import settings

def search_products_online(query: str):
    """
    Searches Google Shopping via SerpApi for the query and returns top results.
    """
    if not settings.SERPAPI_KEY:
        print("❌ SERPAPI_KEY is missing.")
        return []

    params = {
        "engine": "google_shopping",
        "q": query,
        "google_domain": "google.co.in", 
        "gl": "in",
        "hl": "en",
        "api_key": settings.SERPAPI_KEY
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        shopping_results = results.get("shopping_results", [])
        
        cleaned_products = []
        for item in shopping_results[:5]: # Top 5 items
            product = {
                "title": item.get("title"),
                "price": item.get("price"),
                "image": item.get("thumbnail"),
                "link": item.get("link"),
                "source": item.get("source")
            }
            cleaned_products.append(product)
            
        return cleaned_products
    except Exception as e:
        print(f"❌ Error querying SerpApi: {e}")
        return []
