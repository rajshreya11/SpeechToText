

from faster_whisper import WhisperModel

# Load multilingual Whisper model once
model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)


def transcribe_audio(audio_path: str, selected_language: str = "auto"):

    print("-----------------------------------")
    print("SELECTED LANGUAGE:", selected_language)
    print("WHISPER LANGUAGE: AUTO DETECTION")
    print("-----------------------------------")

    # Automatically detect Hindi, English or other supported languages
    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        vad_filter=True,
        language=None,
        task="transcribe"
    )

    transcript = " ".join(
        segment.text.strip()
        for segment in segments
    ).strip()

    print("DETECTED LANGUAGE:", info.language)
    print("LANGUAGE PROBABILITY:", info.language_probability)
    print("TRANSCRIPT:", transcript)
    print("-----------------------------------")

    return {
        "original_text": transcript,
        "language": info.language,
        "language_probability": info.language_probability
    }

