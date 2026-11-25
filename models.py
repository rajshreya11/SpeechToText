
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from database import Base


class Transcription(Base):

    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)

    original_text = Column(Text, nullable=False)

    language = Column(String(50), nullable=True)

    created_at = Column(
        DateTime(timezone=False),
        server_default=func.now()
    )
