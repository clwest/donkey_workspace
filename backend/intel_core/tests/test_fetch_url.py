from intel_core.helpers import document_helpers as helper

class DummyResponse:
    def __init__(self, text):
        self.text = text
        self.ok = True
        self.status_code = 200


def test_fetch_url_falls_back_to_requests(monkeypatch):
    dummy_resp = DummyResponse("<html>ok</html>")

    def failing_playwright(*args, **kwargs):
        raise Exception("playwright missing")

    monkeypatch.setattr(helper, "sync_playwright", failing_playwright)
    monkeypatch.setattr(helper.requests, "get", lambda *a, **kw: dummy_resp)

    result = helper.fetch_url("http://example.com")
    assert result == "<html>ok</html>"
