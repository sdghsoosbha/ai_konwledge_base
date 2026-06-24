from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_owned_knowledge_base
from app.models import Document, DocumentChunk, User
from app.schemas.document import DocumentResponse
from app.services.file_parser import (
    DocumentParseError,
    UnsupportedFileTypeError,
    get_file_type,
    parse_document,
)
from app.services.ollama_client import OllamaClient, OllamaUnavailableError
from app.services.text_splitter import split_pages

router = APIRouter()


@router.post(
    "/knowledge-bases/{kb_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    kb_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_owned_knowledge_base(db, kb_id, current_user)

    try:
        file_type = get_file_type(file.filename or "")
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    max_bytes = settings.max_upload_mb * 1024 * 1024
    content = file.file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail=f"文件最大 {settings.max_upload_mb} MB ")

    document = Document(
        filename=file.filename or "uploaded-file",
        file_type=file_type,
        status="processing",
        knowledge_base_id=kb_id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        pages = parse_document(document.filename, content)
        chunks = split_pages(pages, chunk_size=settings.chunk_size, overlap=settings.chunk_overlap)
        if not chunks:
            raise DocumentParseError("未能从文档提取有效文本切片")

        ollama = OllamaClient()
        for index, chunk in enumerate(chunks):
            embedding = ollama.embed(chunk.content)
            db.add(
                DocumentChunk(
                    document_id=document.id,
                    content=chunk.content,
                    chunk_index=index,
                    chunk_metadata=chunk.metadata,
                    embedding=embedding,
                )
            )

        document.status = "上传完成"
        document.chunk_count = len(chunks)
        document.error_message = None
        db.commit()
        db.refresh(document)
        return document
    except DocumentParseError as exc:
        _mark_document_failed(db, document.id, str(exc))
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except OllamaUnavailableError:
        _mark_document_failed(db, document.id, "Ollama embedding service unavailable")
        raise


@router.get("/knowledge-bases/{kb_id}/documents", 
            response_model=list[DocumentResponse],
            summary="查看知识库文档")
def list_documents(
    kb_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_owned_knowledge_base(db, kb_id, current_user)
    statement = (
        select(Document)
        .where(Document.knowledge_base_id == kb_id)
        .order_by(Document.created_at.desc())
    )
    return list(db.scalars(statement))


def _mark_document_failed(db: Session, document_id: int, message: str) -> None:
    db.rollback()
    document = db.get(Document, document_id)
    if document:
        document.status = "failed"
        document.error_message = message
        db.commit()

