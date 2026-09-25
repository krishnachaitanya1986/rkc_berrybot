import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def transcribe_audio(audio_file) -> str:
    """
    Transcribe a file path, bytes, or a Streamlit UploadedFile.
    Returns the recognized text.
    """
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file.")

    client = Groq()
    model = os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3-turbo")

    if isinstance(audio_file, (str, Path)):
        path = Path(audio_file)
        with path.open("rb") as file:
            result = client.audio.transcriptions.create(
                file=(path.name, file.read()),
                model=model,
                language="en",
                response_format="json",
            )
    elif isinstance(audio_file, bytes):
        result = client.audio.transcriptions.create(
            file=("answer.wav", audio_file),
            model=model,
            language="en",
            response_format="json",
        )
    elif hasattr(audio_file, "getvalue"):
        # Streamlit UploadedFile
        result = client.audio.transcriptions.create(
            file=(getattr(audio_file, "name", "answer.wav"), audio_file.getvalue()),
            model=model,
            language="en",
            response_format="json",
        )
    else:
        raise TypeError(
            "audio_file must be a file path, bytes, or Streamlit UploadedFile"
        )

    return result.text.strip()