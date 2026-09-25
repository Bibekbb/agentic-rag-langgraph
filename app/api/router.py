from fastapi import APIRouter
from app.api.routes import chat, ingest, health, eval as eval_route

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(chat.router)
api_router.include_router(ingest.router)
api_router.include_router(eval_route.router)
