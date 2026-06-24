from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api import auth, chat, documents, knowledge_bases
from app.core.database import init_db
from app.services.ollama_client import OllamaUnavailableError


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI Knowledge Base API",
    description="FastAPI RAG backend with JWT auth, PostgreSQL pgvector, and Ollama.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(status_code=500, content={"detail": "数据库错误"})


@app.exception_handler(OllamaUnavailableError)
async def ollama_exception_handler(request: Request, exc: OllamaUnavailableError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


app.include_router(auth.router, prefix="/auth", tags=["认证"])
app.include_router(knowledge_bases.router, prefix="/knowledge-bases", tags=["知识库"])
app.include_router(documents.router, tags=["文档"])
app.include_router(chat.router, tags=["对话"])

