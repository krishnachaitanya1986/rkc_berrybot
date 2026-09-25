import os
import tempfile
from faster_whisper import WhisperModel


# Load Whisper only once
model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)


def transcribe_audio(audio_data) -> str:
    temp_path = None

    try:
        # Get raw bytes from Streamlit audio object
        if hasattr(audio_data, "getvalue"):
            audio_bytes = audio_data.getvalue()

        elif isinstance(audio_data, bytes):
            audio_bytes = audio_data

        else:
            raise ValueError(
                f"Unsupported audio type: {type(audio_data)}"
            )

        if not audio_bytes:
            raise ValueError("Audio recording is empty.")

        # Save Streamlit audio into a real temporary WAV file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as temp_audio:

            temp_audio.write(audio_bytes)
            temp_path = temp_audio.name

        # faster-whisper can reliably process the file path
        segments, info = model.transcribe(
            temp_path,
            beam_size=5,
            language="en"
        )

        transcription = " ".join(
            segment.text.strip()
            for segment in segments
        ).strip()

        return transcription

    except Exception as e:
        raise RuntimeError(
            f"Transcription failed: {e}"
        )

    finally:
        # Clean temporary file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)