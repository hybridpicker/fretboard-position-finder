import pytest

from positionfinder import search_utils


@pytest.fixture(autouse=True)
def clear_resolve_root_cache():
    """search_utils.resolve_root memoises Root rows (including misses) in a module-level dict.

    Without clearing it, a lookup made while the database was empty would leak into later tests.
    """
    cache = search_utils.resolve_root.__defaults__[0]
    cache.clear()
    yield
    cache.clear()
