from contextlib import asynccontextmanager
from fastapi import FastAPI,status, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
import traceback

from app.db import async_engine, sync_engine, create_db_and_tables
from app.routers.admin import router as admin_router
from app.routers.users import router as users_router
from app.routers.categories import router as categories_router
from app.routers.products import router as products_router
from app.logging_config.logging_middleware import LoggingMiddleware
from app.logging_config.logger import logger
from app.config import Environment, get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.environment == Environment.DEV:
        await create_db_and_tables()
        
    yield
    
    await async_engine.dispose()
    if sync_engine:
        sync_engine.dispose()


app = FastAPI(lifespan=lifespan)
app.add_middleware(LoggingMiddleware)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled Exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )

@app.get("/", summary="Root", tags=["Root"], status_code=status.HTTP_200_OK)
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to Online Store API"}


app.include_router(admin_router, prefix="/api/v1", tags=["Admin"])
app.include_router(users_router, prefix="/api/v1", tags=["Users"])
app.include_router(categories_router, prefix="/api/v1",tags=["Categories"])
app.include_router(products_router, prefix="/api/v1", tags=["Products"])