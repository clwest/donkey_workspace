from intel_core.utils.processing import process_videos
from intel_core.helpers.youtube_video_helper import process_youtube_video


def load_videos(
    video_urls, user_provided_title=None, project_name="General", session_id=None
):
    """
    Load and process YouTube videos from the given URLs.

    Args:
        video_urls (list): List of YouTube video URLs.
        video_title (str): Title to assign to the Videos
        project_name (str): Name of the project for metadata
        session_id (str): UUID of the session

    Returns:
        list: List of processed Document objects.
    """

    processed_documents = []
    for url in video_urls:
        try:
            # Load the video content
            chunks = process_youtube_video(url)
            if not chunks:
                print(f"Could not fetch content for video: {url}")
                continue

            # Assign metadata
            video_title = user_provided_title or "Uploaded Video"

            # Process each chunk
            for chunk in chunks:
                document = {
                    "page_content": chunk,
                    "metadata": {
                        "title": video_title,
                        "source_type": "YouTube",
                        "source_url": url,
                        "project": project_name,
                        "session_id": session_id,  # Include session_id here
                    },
                }

                processed_document = process_videos(
                    document,
                    video_title=video_title,
                    project_name=project_name,
                    session_id=session_id,
                )
                processed_documents.append(processed_document)

        except Exception as e:
            print(f"Failed to process YouTube video {url}: {e}")

    return processed_documents
