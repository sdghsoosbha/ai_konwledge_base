from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class SourceChunk(BaseModel):
    document_id: int
    document_name: str
    chunk_id: int
    score: float
    content: str


class ChatResponse(BaseModel):
    record_id: int
    answer: str
    sources: list[SourceChunk]


class ChatHistoryItem(BaseModel):
    id: int
    knowledge_base_id: int
    question: str
    answer: str
    source_chunks: list[dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

