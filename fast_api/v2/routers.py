from fastapi import APIRouter

from .endpoints import skills, vacancies

api_router_v2 = APIRouter(prefix="/api/v2")
api_router_v2.include_router(skills.router, prefix="/skills", tags=["skills"])
api_router_v2.include_router(vacancies.router, prefix="/vacancies", tags=["vacancies"])
