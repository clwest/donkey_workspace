"""Tests for cache helper utilities in ``intel_core.helpers.cache_core``."""

from types import SimpleNamespace

import pytest

import intel_core.helpers.cache_core as cc


class DummyCache:
    """Simple in-memory stand in for Django's cache."""

    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value, timeout=None):
        self.store[key] = value

    def delete(self, key):
        self.store.pop(key, None)

    def clear(self):
        self.store.clear()


@pytest.fixture(autouse=True)
def patch_cache(monkeypatch):
    dummy = DummyCache()
    monkeypatch.setattr(cc, "cache", dummy)
    return dummy


def test_redis_cache_hit_miss(patch_cache):
    """Set, retrieve and clear values using the cache helpers."""

    # Cache miss when key absent
    assert cc.get_cache("foo") is None

    # Set and retrieve value
    assert cc.set_cache("foo", "bar", timeout=10) is True
    assert cc.get_cache("foo") == "bar"

    # Delete the key and verify miss
    cc.delete_cache("foo")
    assert cc.get_cache("foo") is None

    # Clear removes all keys
    cc.set_cache("a", 1)
    cc.set_cache("b", 2)
    cc.clear_cache()
    assert patch_cache.store == {}
