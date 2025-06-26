import uvicorn
from fastapi import Depends
from app.config import settings
from app.api import router as api_router
from app.create_fastapi_app import create_app
from app.dependencies.auth import verify_api_key



app = create_app(
    create_custom_static_urls=True,
)

app.include_router(
    api_router,
    dependencies=[Depends(verify_api_key)]
)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    ) 
