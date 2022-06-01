import sys
import pytest
import utime


@pytest.fixture
def mock_time_module(monkeypatch):
    """the time module isn't as easily mocked as the utime module is,
    but we can just swap it out for our mock for this test"""
    monkeypatch.setitem(sys.modules, "time", utime)


def test_menu_imports(mock_time_module):
    import contrib.menu
