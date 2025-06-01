from dotenv import load_dotenv
import os
import re
from utils.logging_utils import get_logger
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    TooManyRequests,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = get_logger(__name__)

DEBUG_TRANSCRIPT = os.getenv("DEBUG_TRANSCRIPT", "false").lower() == "true"


# Load environment variables
load_dotenv()

api_key = os.getenv("YOUTUBE_API")


def extract_video_id(youtube_url: str) -> str:
    """Return the video ID portion of a YouTube URL."""

    parsed = urlparse(youtube_url)
    query_params = parse_qs(parsed.query)
    if "v" in query_params:
        return query_params["v"][0]

    if parsed.hostname and parsed.hostname.endswith("youtu.be"):
        return parsed.path.lstrip("/")

    pattern = r"([0-9A-Za-z_-]{11})"
    match = re.search(pattern, youtube_url)
    if match:
        return match.group(1)

    raise ValueError("Invalid YouTube URL. Could not extract video ID.")


def _fetch_transcript(video_id: str):
    """Return a transcript list for the given video ID if available."""

    fetch_attempts = []

    if api_key:
        fetch_attempts.append(
            lambda: YouTubeTranscriptApi.get_transcript(video_id, youtube_api_key=api_key)
        )

    fetch_attempts.append(lambda: YouTubeTranscriptApi.get_transcript(video_id))

    def _list_transcripts():
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            return transcripts.find_transcript(["en"]).fetch()
        except Exception:
            try:
                return transcripts.find_generated_transcript(["en"]).fetch()
            except Exception:
                for t in transcripts:
                    try:
                        return t.fetch()
                    except Exception:
                        continue
                return None

    fetch_attempts.append(_list_transcripts)

    for attempt in fetch_attempts:
        try:
            return attempt()
        except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable, TooManyRequests) as exc:
            logger.error(f"Transcript unavailable for video {video_id}: {exc}")
            return None
        except Exception as exc:  # noqa: PERF203
            logger.debug(f"Transcript fetch attempt failed for {video_id}: {exc}")

    return None


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

    logger.info("[YT] Fetching transcript for video: %s", youtube_url)
    transcript = _fetch_transcript(video_id)
    if not transcript:
        logger.warning("Could not fetch content for video: %s", youtube_url)
        if DEBUG_TRANSCRIPT:
            logger.warning("[YT] Using sample transcript due to missing content")
            transcript = [{"text": "test segment"}]
        else:
            return []

    segments = transcript
    if not segments:
        logger.warning("No transcript segments found for %s", youtube_url)
        if DEBUG_TRANSCRIPT:
            segments = [{"text": "test segment"}]
        else:
            return []

    logger.info("[YT] Retrieved %d segments", len(segments))
    for i, seg in enumerate(segments[:3]):
        logger.debug("[YT] Segment %d: %s", i, seg.get("text", ""))

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
