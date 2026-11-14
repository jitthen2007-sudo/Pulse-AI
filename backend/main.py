import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
backend_dir = Path(__file__).resolve().parent
load_dotenv(backend_dir / ".env")
load_dotenv(backend_dir.parent / ".env")

# Import modular domain logic
from .chatbot import (
    ChatRequest, 
    ChatResponse, 
    generate_chat_response, 
    get_gemini_client, 
    get_gemini_model,
    GENAI_AVAILABLE
)
from .diet import (
    NutritionRequest, 
    NutritionResponse, 
    calculate_diet_plan
)
from .gym_recommender import (
    RoutineRequest, 
    RoutineResponse, 
    recommend_gyms_and_routines
)

app = FastAPI(
    title="Pulse AI - Core Fitness & Biomechanics API",
    description="Refactored modular backend powering Pulse AI's virtual coach, dietician, and gym recommender.",
    version="2.0.0"
)

# Configure CORS for local frontend (Next.js runs on port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    has_key = bool(api_key and api_key != "your_gemini_api_key_here")
    return {
        "status": "online",
        "service": "Pulse AI Refactored Backend",
        "gemini_configured": has_key,
        "gemini_model": get_gemini_model(),
        "genai_sdk_loaded": GENAI_AVAILABLE,
        "mode": "Gemini Live API" if has_key else "Autonomous Local Sports-Science Engine (No API Key Required)",
        "endpoints": ["/api/chat", "/api/nutrition", "/api/routines", "/api/health"]
    }

# ==============================================================================
# Module 1: Virtual Gym Buddy / Coach
# ==============================================================================
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        return await generate_chat_response(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")

# ==============================================================================
# Module 2: AI Dietician & Nutritionist
# ==============================================================================
@app.post("/api/nutrition", response_model=NutritionResponse)
@app.post("/api/diet", response_model=NutritionResponse)
async def diet_endpoint(req: NutritionRequest):
    try:
        return await calculate_diet_plan(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diet engine error: {str(e)}")

# ==============================================================================
# Module 3: Smart Gym & Routine Recommender
# ==============================================================================
@app.post("/api/routines", response_model=RoutineResponse)
@app.post("/api/gym", response_model=RoutineResponse)
async def gym_recommender_endpoint(req: RoutineRequest):
    try:
        return await recommend_gyms_and_routines(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gym recommender error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
