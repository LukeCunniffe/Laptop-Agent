import os
import tempfile
import wave

import numpy as np
import sounddevice as sd
from dotenv import load_dotenv
from groq import Groq


load_dotenv()


SAMPLE_RATE = 16000
CHANNELS = 1


class VoiceRecorder:

    def __init__(self):
        self.stream = None
        self.audio_chunks = []
        self.is_recording = False

    def audio_callback(
        self,
        indata,
        frames,
        time,
        status,
    ) -> None:

        if status:
            print(status)

        if self.is_recording:
            self.audio_chunks.append(
                indata.copy()
            )

    def start_recording(self) -> None:

        if self.is_recording:
            return

        self.audio_chunks = []
        self.is_recording = True

        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            callback=self.audio_callback,
        )

        self.stream.start()

        print("Recording started.")

    def stop_and_transcribe(self) -> str:

        if not self.is_recording:
            return ""

        self.is_recording = False

        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        print("Recording stopped.")

        if not self.audio_chunks:
            return ""

        recording = np.concatenate(
            self.audio_chunks,
            axis=0,
        )

        file_descriptor, audio_path = tempfile.mkstemp(
            suffix=".wav"
        )

        os.close(file_descriptor)

        try:
            with wave.open(
                audio_path,
                "wb"
            ) as wav_file:

                wav_file.setnchannels(
                    CHANNELS
                )

                wav_file.setsampwidth(2)

                wav_file.setframerate(
                    SAMPLE_RATE
                )

                wav_file.writeframes(
                    recording.tobytes()
                )

            client = Groq()

            with open(
                audio_path,
                "rb"
            ) as audio_file:

                transcription = (
                    client.audio.transcriptions.create(
                        file=audio_file,
                        model="whisper-large-v3-turbo",
                        language="en",
                        response_format="json",
                    )
                )

            return transcription.text.strip()

        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)
