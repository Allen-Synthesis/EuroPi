import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "firmware"))
sys.path.append(str(Path(__file__).parent.parent))  # contrib
sys.path.append(str(Path(__file__).parent.parent / "tests" / "mocks"))
