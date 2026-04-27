from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from pathlib import Path


class Status(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARN = "WARN"
    SKIPPED = "SKIPPED"
    BROKEN = "BROKEN"


# Display metadata for each status (icon + label used in summary report)
STATUS_DISPLAY: dict[Status, tuple[str, str]] = {
    Status.PASSED: ("\u2705", "Passed"),
    Status.FAILED: ("\u274c", "Failed"),
    Status.WARN: ("\u26a0\ufe0f", "Warning"),
    Status.SKIPPED: ("\u23ed\ufe0f", "Skipped"),
    Status.BROKEN: ("\U0001f4a5", "Broken"),
}


@dataclass
class TestResult:
    test_id: str
    test_name: str
    test_file: Path
    status: Status = Status.BROKEN
    notes: str = ""
    steps: int | None = None
    is_setup: bool = False
    duration: timedelta | None = None


def test_id_and_name_from_path(path: Path) -> tuple[str, str]:
    """Derive (test_id, test_name) from a test file path.

    Convention: filename stem starts with "{id}_{name}". If there is no
    underscore, the whole stem is treated as the name and the id is empty.
    """
    stem = path.stem
    if "_" in stem:
        test_id, _, test_name = stem.partition("_")
        return test_id.strip(), test_name.strip()
    return "", stem.strip()
