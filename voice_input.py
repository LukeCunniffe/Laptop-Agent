import os
import tempfile
import wave

from dotenv import load_dotenv

load_dotenv()

import sounddevice as sd
from groq import Groq

SAMPLE_RATE = 16000
CHANNELS = 1
RECORD_SECONDS = 5

def record_and_transcribe() -> str:
    """Record microphone audio and return the transcription"""

    print("Recording...")

    recording = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            )

    sd.wait()

    print("Recording finished.")

    file_descriptor, audio_path = tempfile.mkstemp(
            suffix=".wav"
            )
    os.close(file_descriptor)

    try:
        with wave.open(audio_path, "wb") as wav_file:
            wav_file.setnchannels(CHANNELS)
            wav_file.setsampwidth(2)
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(recording.tobytes())

        client = Groq()

        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3-turbo",
                    language="en",
                    response_format="json",
                    )

        return transcription.text.strip()

    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
