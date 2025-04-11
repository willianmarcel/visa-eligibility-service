from fastapi import APIRouter
from app.api.v1.endpoints import eligibility

api_router = APIRouter()

api_router.include_router(
    eligibility.router,
    prefix="/eligibility",
    tags=["eligibility"]
) 