# test_runway_call.py (or use a Django shell)

import os
from runwayml import RunwayML
from dotenv import load_dotenv

load_dotenv()

# Replace this with your actual ngrok URL!
NGROK_IMAGE_URL = "https://169a-2605-b40-1301-4000-d9e5-56c-4542-67.ngrok-free.app/media/images/donk-wizard.png"

client = RunwayML(
    api_key=os.environ.get("RUNWAYML_API_SECRET"),  # Or hardcode for testing
)

response = client.image_to_video.create(
    model="gen4_turbo",
    prompt_image=NGROK_IMAGE_URL,
    prompt_text="The donkey wizard creates a swirling portal of stars and steps through it.",
)

print(f"🎥 Runway Video ID: {response.id}")
