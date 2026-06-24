from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_owned_knowledge_base
from app.models import ChatRecord, Document, DocumentChunk, User
from app.schemas.chat import ChatHistoryItem, ChatRequest, ChatResponse, SourceChunk
from app.services.ollama_client import OllamaClient
from app.services.rag import build_rag_prompt

router = APIRouter()


@router.post("/knowledge-bases/{kb_id}/chat", response_model=ChatResponse)
def chat_with_knowledge_base(
    kb_id: int,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_owned_knowledge_base(db, kb_id, current_user)

    ollama = OllamaClient()
    question_embedding = ollama.embed(payload.question)

    distance = DocumentChunk.embedding.cosine_distance(question_embedding).label("distance")
    statement = (
        select(DocumentChunk, Document.id, Document.filename, distance)
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(Document.knowledge_base_id == kb_id, Document.status == "processed")
        .order_by(distance)
        .limit(settings.top_k)
    )
    rows = db.execute(statement).all()
    if not rows:
        raise HTTPException(status_code=400, detail="知识库暂无已处理的文档片段")

    sources: list[SourceChunk] = []
    for chunk, document_id, filename, distance_value in rows:
        score = max(0.0, 1.0 - float(distance_value))
        sources.append(
            SourceChunk(
                document_id=document_id,
                document_name=filename,
                chunk_id=chunk.id,
                score=round(score, 4),
                content=chunk.content,
            )
        )

    prompt = build_rag_prompt(payload.question, sources)
    answer = ollama.chat(prompt)

    record = ChatRecord(
        user_id=current_user.id,
        knowledge_base_id=kb_id,
        question=payload.question,
        answer=answer,
        source_chunks=[source.model_dump() for source in sources],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return ChatResponse(record_id=record.id, answer=answer, sources=sources)


@router.get("/chat/history", response_model=list[ChatHistoryItem])
def list_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = (
        select(ChatRecord)
        .where(ChatRecord.user_id == current_user.id)
        .order_by(ChatRecord.created_at.desc())
    )
    return list(db.scalars(statement))

