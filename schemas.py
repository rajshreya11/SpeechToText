
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TranscriptionCreate(BaseModel):
    original_text: str
    language: Optional[str] = None


class TranscriptionResponse(BaseModel):
    id: int
    original_text: str
    language: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
