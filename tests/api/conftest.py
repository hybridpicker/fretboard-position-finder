"""Shared fixtures for the API test modules."""

import pytest
from django.core.cache import cache
from django.db import transaction


@pytest.fixture(autouse=True)
def _clear_cache():
    """chord-voicings is wrapped in cache_page, so keep tests independent."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api_get(client):
    """GET helper that survives database errors raised (and swallowed) inside a view.

    Some views swallow SQL errors with ``except Exception``. On PostgreSQL that leaves the
    surrounding test transaction aborted, so every request runs in its own savepoint
    which is rolled back afterwards (all endpoints are read-only).
    """

    def _get(url, **params):
        sid = transaction.savepoint()
        try:
            return client.get(url, params)
        finally:
            transaction.savepoint_rollback(sid)

    return _get


@pytest.fixture
def break_view_query_params(monkeypatch):
    """Make ``request.query_params`` raise for the view body.

    DRF reads ``query_params`` once itself (content negotiation), so the first access per
    request keeps working and every later access raises.
    """
    from rest_framework.request import Request

    seen = set()

    def _prop(self):
        if id(self) not in seen:
            seen.add(id(self))
            return self._request.GET
        raise RuntimeError("query_params broken")

    monkeypatch.setattr(Request, "query_params", property(_prop))
