from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

from app.db.database import async_session_factory, engine



@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await engine.dispose()


def register_static_docs_routes(app: FastAPI):
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        )

def create_app(
    create_custom_static_urls: bool = False,
) -> FastAPI:
    app = FastAPI(
        title="API Organizations",
        description="Для взаимодействия с API необходимо передать в заголовках запроса X-API-Key. (supersecret)",
        contact={
            "name": "Sergey Kuzmin",
            "email": "sergozero90@gmail.com",
        },
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
        docs_url=None if create_custom_static_urls else "/docs",
        redoc_url=None if create_custom_static_urls else "/redoc",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    if create_custom_static_urls:
        register_static_docs_routes(app)
    return app
