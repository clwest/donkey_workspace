import pytest

from intel_core.helpers import youtube_video_helper as helper


class DummySplitter:
    def __init__(self, *args, **kwargs):
        pass

    def split_text(self, text):
        return [text]


def test_extract_video_id_with_time_param():
    url = "https://www.youtube.com/watch?v=f0-t_jIW9yY&t=849s"
    assert helper.extract_video_id(url) == "f0-t_jIW9yY"


def test_process_youtube_video_returns_empty_on_failure(monkeypatch):
    def fail_get_transcript(*args, **kwargs):
        raise Exception("no element found: line 1, column 0")

    def fail_list_transcripts(*args, **kwargs):
        raise Exception("no transcripts")

    monkeypatch.setattr(
        helper.YouTubeTranscriptApi,
        "get_transcript",
        staticmethod(fail_get_transcript),
    )
    monkeypatch.setattr(
        helper.YouTubeTranscriptApi, "list_transcripts", staticmethod(fail_list_transcripts)
    )
    monkeypatch.setattr(helper, "RecursiveCharacterTextSplitter", DummySplitter)

    chunks = helper.process_youtube_video(
        "https://www.youtube.com/watch?v=f0-t_jIW9yY&t=849s"
    )
    assert chunks == []


def test_process_youtube_video_falls_back_to_any_language(monkeypatch):
    class DummyTranscript:
        def fetch(self):
            return [
                {"text": "Hello"},
            ]

    def fail_get_transcript(*args, **kwargs):
        raise Exception("fail")

    monkeypatch.setattr(
        helper.YouTubeTranscriptApi, "get_transcript", staticmethod(fail_get_transcript)
    )

    monkeypatch.setattr(
        helper.YouTubeTranscriptApi,
        "list_transcripts",
        staticmethod(lambda *args, **kwargs: [DummyTranscript()]),
    )
    monkeypatch.setattr(helper, "RecursiveCharacterTextSplitter", DummySplitter)

    chunks = helper.process_youtube_video("https://www.youtube.com/watch?v=abcdEFGhijk")
    assert chunks == ["Hello"]
