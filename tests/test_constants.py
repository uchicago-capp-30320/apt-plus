import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.constants import WALKING_SPEED_PER_MIN, HP_BOUNDS


def test_constants():
    assert isinstance(HP_BOUNDS, list)
    assert isinstance(WALKING_SPEED_PER_MIN, int)
    print("Works as expected.")


if __name__ == "__main__":
    test_constants()
