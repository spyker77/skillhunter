from typing import List

from django.conf import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fast_api.v2.routers import api_router_v2

API_VERSIONS_ROUTERS = {
    "v2": api_router_v2,
}


def create_application(api_versions: List[str] = ["v2"]) -> FastAPI:
    application = FastAPI(title="SkillHunter API", version=api_versions[0])
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    for version in api_versions:
        application.include_router(API_VERSIONS_ROUTERS[version])
    return application
