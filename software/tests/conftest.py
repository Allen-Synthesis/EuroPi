import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent / "firmware"))
sys.path.append(str(Path(__file__).parent.parent))  # contrib
sys.path.append(str(Path(__file__).parent.parent / "tests" / "mocks"))


from mock_hardware import MockHardware


@pytest.fixture
def mockHardware(monkeypatch):
    return MockHardware(monkeypatch)
