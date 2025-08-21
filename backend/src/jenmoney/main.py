from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jenmoney.api.v1.router import api_router
from jenmoney.config import settings
from jenmoney.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_str)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy", "version": settings.version}


def main() -> None:
    uvicorn.run(
        "jenmoney.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
