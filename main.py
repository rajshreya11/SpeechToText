
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from models import Transcription
from schemas import TranscriptionCreate, TranscriptionResponse

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Speech To Text API")


# Database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Health check
@app.get("/health")
def health():
    return {"status": "Healthy"}


# CREATE transcription
@app.post(
    "/api/transcriptions",
    response_model=TranscriptionResponse
)
def create_transcription(
    data: TranscriptionCreate,
    db: Session = Depends(get_db)
):
    new_transcription = Transcription(
        original_text=data.original_text,
        language=data.language
    )

    db.add(new_transcription)
    db.commit()
    db.refresh(new_transcription)

    return new_transcription


# READ all transcriptions
@app.get(
    "/api/transcriptions",
    response_model=list[TranscriptionResponse]
)
def get_transcriptions(db: Session = Depends(get_db)):
    return db.query(Transcription).order_by(
        Transcription.id.desc()
    ).all()


# UPDATE transcription
@app.put(
    "/api/transcriptions/{transcription_id}",
    response_model=TranscriptionResponse
)
def update_transcription(
    transcription_id: int,
    data: TranscriptionCreate,
    db: Session = Depends(get_db)
):
    transcription = db.query(Transcription).filter(
        Transcription.id == transcription_id
    ).first()

    if not transcription:
        raise HTTPException(
            status_code=404,
            detail="Transcription not found"
        )

    transcription.original_text = data.original_text
    transcription.language = data.language

    db.commit()
    db.refresh(transcription)

    return transcription


# # DELETE transcription
# @app.delete("/api/transcriptions/{transcription_id}")
# def delete_transcription(
#     transcription_id: int,
#     db: Session = Depends(get_db)
# ):
#     transcription = db.query(Transcription).filter(
#         Transcription.id == transcription_id
#     ).first()

#     if not transcription:
#         raise HTTPException(
#             status_code=404,
#             detail="Transcription not found"
#         )

#     db.delete(transcription)
#     db.commit()

#     return {"message": "Transcription deleted successfully"}
