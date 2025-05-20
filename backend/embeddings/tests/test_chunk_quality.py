import os
import importlib.util

chunk_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "document_services", "chunking.py")
)
spec = importlib.util.spec_from_file_location("chunking", chunk_path)
ck = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ck)


def test_merge_small_chunks():
    chunks = ["alpha beta", "gamma delta", "large chunk here with many words"]
    results = ck.merge_and_score_chunks(chunks, small_threshold=3, max_total_tokens=10)
    assert len(results) == 2
    text1, score1, notes1 = results[0]
    assert "gamma" in text1  # merged with next
    assert notes1 == "merged with next"
    assert score1 == 1.0  # combined tokens exceed threshold


def test_discard_duplicate_and_header():
    chunks = ["Page 1 of 2", "repeat chunk", "repeat chunk"]
    results = ck.merge_and_score_chunks(chunks, small_threshold=5)
    assert results[0][1] == 0.0 and "header" in results[0][2]
    assert results[2][1] == 0.0 and "duplicate" in results[2][2]


def test_score_levels():
    chunks = ["short one", "adequate length chunk with many words"]
    res = ck.merge_and_score_chunks(chunks, small_threshold=4)
    assert res[0][1] == 0.5
    assert res[1][1] == 1.0
