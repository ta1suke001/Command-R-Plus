import os
import uuid
import asyncio
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from src.utils.logger import setup_logger

logger = setup_logger()

class ElevenLabsService:
    def __init__(self, api_key):
        self.client = ElevenLabs(api_key=api_key)
        self.voice_id = "YOUR_ELEVENLABS_VOICE_MODEL_ID"
        self.output_dir = os.path.join("data", "mp3_voice")
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate_speech(self, text):
        try:
            logger.debug(f"Generating speech for text: {text}")
            logger.debug(f"Using voice_id: {self.voice_id}")

            response = await asyncio.to_thread(
                self.client.text_to_speech.convert,
                voice_id=self.voice_id,
                optimize_streaming_latency="0",
                output_format="mp3_22050_32",
                text=text,
                model_id="eleven_multilingual_v2",

                #仮設定
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.3,
                    use_speaker_boost=True,
                ),
            )
            logger.debug("ElevenLabs API call successful")

            save_file_name = f"{uuid.uuid4()}.mp3"
            save_file_path = os.path.join(self.output_dir, save_file_name)

            logger.debug(f"Saving audio file to: {save_file_path}")
            with open(save_file_path, "wb") as f:
                for chunk in response:
                    if chunk:
                        f.write(chunk)
            logger.info(f"{save_file_path}: A new audio file was saved successfully!")
            return save_file_path

        except Exception as e:
            logger.error(f"Error during text-to-speech conversion: {str(e)}")
            return None

    def set_voice(self, voice_id):
        self.voice_id = voice_id
        logger.info(f"Voice ID set to: {voice_id}")

    def cleanup_audio_file(self, file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Deleted audio file: {file_path}")
        except Exception as e:
            logger.error(f"Error while deleting audio file: {str(e)}")