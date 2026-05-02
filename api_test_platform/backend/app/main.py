"""
FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.environment import router as environment_router
from app.api.api_management import router as api_management_router
from app.api.execution import router as execution_router
from app.api.test_case import router as test_case_router
from app.api.test_case_module import router as test_case_module_router
from app.db.session import engine
from app.db.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API Testing Platform - Environment & API Management Module",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(environment_router, prefix="/api/v1")
app.include_router(api_management_router, prefix="/api/v1")
app.include_router(execution_router, prefix="/api/v1")
app.include_router(test_case_router, prefix="/api/v1")
app.include_router(test_case_module_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
