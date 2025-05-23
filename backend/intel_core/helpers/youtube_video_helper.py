from dotenv import load_dotenv
import os
import re
import logging
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    TooManyRequests,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


# Load environment variables
load_dotenv()

api_key = os.getenv("YOUTUBE_API")


def extract_video_id(youtube_url):
    """
    Extract the video ID from a YouTube URL.
    """
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, youtube_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL. Could not extract video ID.")


def process_youtube_video(youtube_url):
    """
    Process a YouTube video by extracting subtitles and splitting into chunks.

    Args:
        youtube_url (str): The full YouTube video URL.

    Returns:
        list: A list of text chunks from the video's transcript.
    """
    try:
        video_id = extract_video_id(youtube_url)
    except ValueError as exc:
        logger.error(str(exc))
        return []

    try:
        transcript = (
            YouTubeTranscriptApi.get_transcript(
                video_id, youtube_api_key=api_key
            )
            if api_key
            else YouTubeTranscriptApi.get_transcript(video_id)
        )
    except NoTranscriptFound:
        logger.warning(f"No subtitles found for video {youtube_url}.")
        return []
    except (TranscriptsDisabled, VideoUnavailable, TooManyRequests) as exc:
        logger.error(f"Transcript unavailable for {youtube_url}: {exc}")
        return []
    except Exception as exc:
        # Retry without API key if first attempt failed and a key was used
        if api_key:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
            except Exception as inner_exc:
                logger.error(
                    f"Error fetching transcript for {youtube_url}: {inner_exc}"
                )
                return []
        else:
            logger.error(f"Error fetching transcript for {youtube_url}: {exc}")
            return []

    try:
        transcript_text = " ".join(item.get("text", "") for item in transcript)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        return text_splitter.split_text(transcript_text)
    except Exception as exc:
        logger.error(f"Error processing video {youtube_url}: {exc}")
        return []


# Example usage
# youtube_url = "https://www.youtube.com/watch?v=MaQ2SiVVUy8"
# chunks = process_youtube_video(youtube_url)

# # Check the resulting chunks
# print(chunks)
