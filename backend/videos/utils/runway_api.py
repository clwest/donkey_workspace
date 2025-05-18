# runway/utils/runway_api.py
import runway
import os
import logging

logger = logging.getLogger("django")

RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY")


def generate_gen4_video_with_image(prompt: str, image_path: str) -> bytes:
    try:
        client = runway.Client(api_key=RUNWAY_API_KEY)
        logger.info("🚀 Calling Runway Gen-4...")

        with open(image_path, "rb") as f:
            input_bytes = f.read()

        video_bytes = client.run(
            model="gen-4",  # use latest if available
            inputs={
                "image": input_bytes,
                "prompt": prompt,
            },
        )

        if not video_bytes:
            raise ValueError("Runway returned no video bytes")

        return video_bytes

    except Exception as e:
        logger.exception(f"🔥 Runway Gen-4 error: {e}")
        raise
