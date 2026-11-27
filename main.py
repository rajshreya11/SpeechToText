
import os
import tempfile
from pathlib import Path

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form
)

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from models import Transcription
from schemas import TranscriptionCreate, TranscriptionResponse

from whisper_service import transcribe_audio


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(title="Speech To Text API")


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------------------------------------------
# LANGUAGE CONFIGURATION
# --------------------------------------------------

def normalize_language(selected_language: str) -> str:
    language = selected_language.strip().lower()

    if language in ("hindi", "hi", "hi-in", "hindi (हिंदी)"):
        return "hi"

    if language in ("english", "en", "en-in"):
        return "en"

    raise HTTPException(
        status_code=400,
        detail="Please select Hindi or English."
    )


def get_language_name(language_code: str) -> str:
    language_names = {
        "hi": "Hindi",
        "en": "English"
    }

    return language_names.get(language_code, "Unknown")


# --------------------------------------------------
# AUDIO FILE VALIDATION AND TEMPORARY STORAGE
# --------------------------------------------------

def save_audio_file(file: UploadFile) -> str:

    allowed_extensions = {
        ".wav",
        ".mp3",
        ".m4a",
        ".mp4",
        ".webm",
        ".ogg",
        ".flac",
        ".mpeg"
    }

    suffix = Path(file.filename or "").suffix.lower()

    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported audio format."
        )

    audio_data = file.file.read()

    if not audio_data:
        raise HTTPException(
            status_code=400,
            detail="Uploaded audio file is empty."
        )

    if len(audio_data) > 25 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Audio file must be smaller than 25 MB."
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            temp_file.write(audio_data)
            temp_path = temp_file.name

        return temp_path

    except Exception:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        raise


# --------------------------------------------------
# WHISPER TRANSCRIPTION HELPER
# --------------------------------------------------

def process_audio_transcription(
    audio_path: str,
    selected_language: str
):

    language_code = normalize_language(selected_language)

    print("-----------------------------------")
    print("USER SELECTED LANGUAGE:", selected_language)
    print("WHISPER LANGUAGE:", language_code)
    print("-----------------------------------")

    result = transcribe_audio(
        audio_path,
        selected_language=language_code
    )

    print("DETECTED LANGUAGE:", result["language"])
    print(
        "LANGUAGE PROBABILITY:",
        result["language_probability"]
    )
    print("TRANSCRIPT:", result["original_text"])
    print("-----------------------------------")

    return result


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "Healthy",
        "message": "Speech To Text API is running"
    }


# --------------------------------------------------
# LIVE TRANSCRIPTION PREVIEW
# NO DATABASE SAVE
# --------------------------------------------------

@app.post("/api/transcriptions/preview")
def preview_transcription(
    file: UploadFile = File(...),
    language: str = Form(...)
):

    temp_path = None

    try:
        temp_path = save_audio_file(file)

        result = process_audio_transcription(
            temp_path,
            language
        )

        return {
            "original_text": result["original_text"],
            "language": result["language"],
            "language_probability": result["language_probability"]
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Preview transcription error:", error)

        raise HTTPException(
            status_code=500,
            detail="Preview transcription failed."
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        file.file.close()


# --------------------------------------------------
# FINAL WHISPER TRANSCRIPTION
# SAVE TO DATABASE
# --------------------------------------------------

@app.post(
    "/api/transcriptions/whisper",
    response_model=TranscriptionResponse
)
def transcribe_with_whisper(
    file: UploadFile = File(...),
    language: str = Form(...),
    db: Session = Depends(get_db)
):

    temp_path = None

    try:
        temp_path = save_audio_file(file)

        result = process_audio_transcription(
            temp_path,
            language
        )

        transcript_text = result.get(
            "original_text",
            ""
        ).strip()

        if not transcript_text:
            raise HTTPException(
                status_code=422,
                detail="No speech detected in the audio."
            )

        selected_language_code = normalize_language(language)

        detected_language = result.get(
            "language",
            selected_language_code
        )

        language_name = get_language_name(
            detected_language
        )

        if language_name == "Unknown":
            language_name = get_language_name(
                selected_language_code
            )

        print("FINAL DETECTED LANGUAGE:", detected_language)
        print("FINAL TRANSCRIPT:", transcript_text)

        new_transcription = Transcription(
            original_text=transcript_text,
            language=language_name
        )

        db.add(new_transcription)
        db.commit()
        db.refresh(new_transcription)

        print("SAVED TRANSCRIPTION ID:", new_transcription.id)

        return new_transcription

    except HTTPException:
        raise

    except Exception as error:
        db.rollback()

        print("Whisper transcription error:", error)

        raise HTTPException(
            status_code=500,
            detail="Whisper transcription failed."
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        file.file.close()


# --------------------------------------------------
# CREATE TRANSCRIPTION
# --------------------------------------------------

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

    try:
        db.add(new_transcription)
        db.commit()
        db.refresh(new_transcription)

        return new_transcription

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to save transcription"
        )


# --------------------------------------------------
# READ ALL TRANSCRIPTIONS
# --------------------------------------------------

@app.get(
    "/api/transcriptions",
    response_model=list[TranscriptionResponse]
)
def get_transcriptions(
    db: Session = Depends(get_db)
):

    return (
        db.query(Transcription)
        .order_by(Transcription.id.desc())
        .all()
    )


# --------------------------------------------------
# UPDATE TRANSCRIPTION
# --------------------------------------------------

@app.put(
    "/api/transcriptions/{transcription_id}",
    response_model=TranscriptionResponse
)
def update_transcription(
    transcription_id: int,
    data: TranscriptionCreate,
    db: Session = Depends(get_db)
):

    transcription = (
        db.query(Transcription)
        .filter(Transcription.id == transcription_id)
        .first()
    )

    if not transcription:
        raise HTTPException(
            status_code=404,
            detail="Transcription not found"
        )

    transcription.original_text = data.original_text
    transcription.language = data.language

    try:
        db.commit()
        db.refresh(transcription)

        return transcription

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to update transcription"
        )


# --------------------------------------------------
# DELETE TRANSCRIPTION
# --------------------------------------------------

@app.delete(
    "/api/transcriptions/{transcription_id}"
)
def delete_transcription(
    transcription_id: int,
    db: Session = Depends(get_db)
):

    transcription = (
        db.query(Transcription)
        .filter(Transcription.id == transcription_id)
        .first()
    )

    if not transcription:
        raise HTTPException(
            status_code=404,
            detail="Transcription not found"
        )

    try:
        db.delete(transcription)
        db.commit()

        return {
            "message": "Transcription deleted successfully",
            "id": transcription_id
        }

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to delete transcription"
        )
