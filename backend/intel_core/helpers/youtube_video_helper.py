from dotenv import load_dotenv
import os
import re
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from langchain_text_splitters import RecursiveCharacterTextSplitter


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
        # Extract video ID from URL
        video_id = extract_video_id(youtube_url)

        # Fetch transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Extract text
        transcript_text = " ".join([item["text"] for item in transcript])

        # Split text into manageable chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        chunks = text_splitter.split_text(transcript_text)

        return chunks

    except NoTranscriptFound:
        print(f"Error: No subtitles found for video {youtube_url}.")
        return []
    except Exception as e:
        print(f"Error processing video {youtube_url}: {e}")
        return []


# Example usage
# youtube_url = "https://www.youtube.com/watch?v=MaQ2SiVVUy8"
# chunks = process_youtube_video(youtube_url)

# # Check the resulting chunks
# print(chunks)
