from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.api import endpoints

app = FastAPI(title="Multimodal Shopping Assistant API")

# Mount Static Files for images
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# CORS (Allow all for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Multimodal Shopping Assistant API"}

# --- Video Analysis Endpoint ---
from backend.app.services.video_service import VideoService
video_service = VideoService()

@app.post("/api/analyze-video")
async def analyze_video(file: UploadFile = File(...), context: str = Form("")):
    """
    Analyze uploaded video for diagnostics.
    """
    return {"analysis": await video_service.analyze_video(file, context)}

# --- Price Prediction Endpoint ---
from backend.app.services.price_service import PriceService
from pydantic import BaseModel

price_service = PriceService()

class PriceRequest(BaseModel):
    product_name: str
    current_price: float
    category: str = ""

@app.post("/api/predict-price")
async def predict_price(request: PriceRequest):
    """
    Predict price trend for a product.
    """
    return price_service.predict_price_trend(request.product_name, request.current_price, request.category)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
