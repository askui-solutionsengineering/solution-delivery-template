from __future__ import annotations

from collections import Counter
from datetime import date as date_type, datetime, timedelta, timezone
from pathlib import Path

from .models import STATUS_DISPLAY, Status, TestResult

SUMMARY_FILENAME = "summary_report.md"


def _format_duration(duration: timedelta) -> str:
    """Format a timedelta as HH:MM:SS."""
    total_secs = max(0, int(duration.total_seconds()))
    hours, remainder = divmod(total_secs, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def render_summary(
    results: list[TestResult],
    report_date: date_type | None = None,
    duration: timedelta | None = None,
    setup_issues: list[tuple[str, str]] | None = None,
) -> str:
    """Render the summary report markdown from a list of TestResult."""
    if report_date is None:
        report_date = datetime.now(timezone.utc).date()

    counts = Counter(r.status for r in results)

    lines: list[str] = []
    lines.append("# Summary Report")
    lines.append("")
    lines.append(f"**Datum:** {report_date.isoformat()}")
    lines.append("")
    lines.append(f"**Total:** {len(results)} Test Cases")
    for status in Status:
        c = counts.get(status, 0)
        if c == 0:
            continue
        icon, label = STATUS_DISPLAY[status]
        lines.append(f"- **{icon} {label}:** {c}")
    if duration is not None:
        lines.append(f"- **\u23f1\ufe0f Duration:** {_format_duration(duration)}")
    lines.append("")

    # Table ---------------------------------------------------------------
    lines.append("| Test Case ID | Test Case Name | Status | Duration |")
    lines.append("|---|---|---|---|")
    for r in results:
        icon, label = STATUS_DISPLAY[r.status]
        duration_cell = _format_duration(r.duration) if r.duration is not None else "\u2014"
        lines.append(
            f"| {r.test_id} | {_escape_cell(r.test_name)} | {icon} {label} | {duration_cell} |"
        )
    lines.append("")

    # Setup Issues section ------------------------------------------------
    if setup_issues:
        lines.append("# \u2699\ufe0f Setup Issues")
        lines.append("")
        for label, text in setup_issues:
            lines.append(f"## {label}")
            lines.append(text)
            lines.append("")

    # Warnings section ----------------------------------------------------
    warnings = [r for r in results if r.status is Status.WARN]
    if warnings:
        lines.append("# \u26a0\ufe0f Warnings")
        lines.append("")
        for r in warnings:
            lines.append(f"## {_header_id(r)}")
            lines.append(r.notes or "_No further details provided._")
            lines.append("")

    # Failures section ----------------------------------------------------
    fails = [r for r in results if r.status is Status.FAILED]
    if fails:
        lines.append("# \u274c Fails")
        lines.append("")
        for r in fails:
            lines.append(f"## {_header_id(r)}")
            lines.append(r.notes or "_No further details provided._")
            lines.append("")

    # Broken / not-executed section --------------------------------------
    broken = [r for r in results if r.status is Status.BROKEN]
    if broken:
        lines.append("# \U0001f4a5 Broken / Not Executed")
        lines.append("")
        for r in broken:
            lines.append(f"## {_header_id(r)}")
            lines.append(r.notes or "_No further details provided._")
            lines.append("")

    # Skipped section -----------------------------------------------------
    skipped = [r for r in results if r.status is Status.SKIPPED]
    if skipped:
        lines.append("# \u23ed\ufe0f Skipped")
        lines.append("")
        for r in skipped:
            lines.append(f"## {_header_id(r)}")
            lines.append(r.notes or "_No further details provided._")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_summary_report(
    workspace: Path,
    results: list[TestResult],
    report_date: date_type | None = None,
    duration: timedelta | None = None,
    setup_issues: list[tuple[str, str]] | None = None,
) -> Path:
    """Render and write the summary report to `<workspace>/summary_report.md`."""
    workspace.mkdir(parents=True, exist_ok=True)
    path = workspace / SUMMARY_FILENAME
    path.write_text(
        render_summary(
            results,
            report_date=report_date,
            duration=duration,
            setup_issues=setup_issues,
        ),
        encoding="utf-8",
    )
    return path


def _header_id(r: TestResult) -> str:
    if r.test_id:
        return f"{r.test_id} - {r.test_name}"
    return r.test_name


def _escape_cell(text: str) -> str:
    """Escape characters that would break a markdown table cell."""
    return text.replace("|", "\\|").replace("\n", " ").strip()
