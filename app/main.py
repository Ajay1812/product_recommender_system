from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.recommender import OccasionRecommender, load_products


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "products.json"

products = load_products(DATA_PATH)
recommender = OccasionRecommender(products)

app = FastAPI(title="Occasion-Based Product Recommender")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    suggestions = [
        "Birthday",
        "Wedding",
        "Anniversary",
        "Diwali",
        "Valentine's Day",
        "Office Party",
        "Baby Shower",
        "Housewarming",
    ]
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "suggestions": suggestions,
            "catalog_size": len(products),
        },
    )


@app.get("/api/recommend")
async def recommend(
    occasion: str = Query("", min_length=1, max_length=100),
    limit: int = Query(8, ge=1, le=24),
) -> dict:
    recommendations = recommender.recommend(occasion, limit=limit)
    return {
        "occasion": occasion,
        "count": len(recommendations),
        "results": recommendations,
    }
