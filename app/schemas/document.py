from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    status: str
    chunk_count: int
    error_message: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

