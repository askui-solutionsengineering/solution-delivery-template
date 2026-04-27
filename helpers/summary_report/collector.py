import logging
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

from .models import Status, TestResult, test_id_and_name_from_path
from .parser import parse_report
from .writer import write_summary_report

logger = logging.getLogger(__name__)


def _sanitize_filename(name: str) -> str:
    """Mirror the filename sanitization used by main.py to resolve report paths."""
    return re.sub(r'[<>:"/\\|?*\x00-\x1f\s]', "_", name)


class SummaryCollector:
    """Tracks the scheduled tests and renders the summary report at the end
    of a run by reading each test's per-test report file from the workspace.
    """

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self._scheduled: list[Path] = []
        self._seen: set[Path] = set()
        self._scheduled_setups: list[Path] = []
        self._setups_seen: set[Path] = set()
        self._test_durations: dict[Path, timedelta] = {}
        self._start_time: datetime = datetime.now(timezone.utc)

    def schedule(self, test_files: Iterable[Path]) -> None:
        """Register tests that were scheduled to run (preserves insertion order)."""
        for test_file in test_files:
            key = test_file.resolve()
            if key in self._seen:
                continue
            self._seen.add(key)
            self._scheduled.append(test_file)

    def record_test_duration(self, test_file: Path, duration: timedelta) -> None:
        """Record how long a single test took to execute."""
        self._test_durations[test_file.resolve()] = duration

    def schedule_setup(self, setup_file: Path) -> None:
        """Register a setup file that was executed.

        The agent may optionally write a `issues.md` file to the setup's
        workspace directory; any such content is surfaced in the summary.
        """
        key = setup_file.resolve()
        if key in self._setups_seen:
            return
        self._setups_seen.add(key)
        self._scheduled_setups.append(setup_file)

    def build_results(self) -> list[TestResult]:
        """Resolve the outcome of every scheduled test by reading its report file."""
        results: list[TestResult] = []
        for test_file in self._scheduled:
            test_id, test_name = test_id_and_name_from_path(test_file)
            status, notes = self._read_test_report(test_file)
            results.append(
                TestResult(
                    test_id=test_id,
                    test_name=test_name,
                    test_file=test_file,
                    status=status,
                    notes=notes,
                    duration=self._test_durations.get(test_file.resolve()),
                )
            )
        return results

    def build_setup_issues(self) -> list[tuple[str, str]]:
        """Collect (label, issues) for every scheduled setup that wrote an issues file."""
        issues: list[tuple[str, str]] = []
        for setup_file in self._scheduled_setups:
            text = self._read_setup_issues(setup_file)
            if not text:
                continue
            issues.append((self._setup_label(setup_file), text))
        return issues

    def write(self) -> Path | None:
        if not self._scheduled:
            logger.info("SummaryCollector.write(): no scheduled tests, skipping.")
            return None
        duration = datetime.now(timezone.utc) - self._start_time
        return write_summary_report(
            self.workspace,
            self.build_results(),
            duration=duration,
            setup_issues=self.build_setup_issues(),
        )

    def _read_test_report(self, test_file: Path) -> tuple[Status, str]:
        report_path = self.workspace / test_file.stem / f"{test_file.stem}_report.md"
        if not report_path.exists():
            report_path = self.workspace / test_file.stem / "report.md"
        return parse_report(report_path)

    def _read_setup_issues(self, setup_file: Path) -> str:
        setup_name = _sanitize_filename(f"{setup_file.parent.name}_setup")
        issues_path = self.workspace / setup_name / "issues.md"
        if not issues_path.exists():
            return ""
        try:
            return issues_path.read_text(encoding="utf-8").strip()
        except OSError as e:
            logger.warning(f"Could not read setup issues at {issues_path}: {e}")
            return ""

    def _setup_label(self, setup_file: Path) -> str:
        """Best-effort short label for a setup file (e.g. 'tests_frontend/setup.md')."""
        try:
            return str(setup_file.resolve().relative_to(Path.cwd()))
        except ValueError:
            return f"{setup_file.parent.name}/{setup_file.name}"
