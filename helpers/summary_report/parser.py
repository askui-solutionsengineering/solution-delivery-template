import re
from pathlib import Path

from .models import Status

# Matches the "**Status:** PASSED" line. Allows multiple pipe-separated
# placeholder values in the template itself to be ignored.
_STATUS_LINE_RE = re.compile(
    r"^\s*\*\*Status:\*\*\s*([A-Z][A-Z_]*)\s*$",
    re.MULTILINE,
)

# Sections we pull into `notes` when present, in priority order.
_NOTE_SECTIONS = ("Issues", "Conclusion")


def parse_report(report_path: Path) -> tuple[Status, str]:
    """Parse a per-test report file into (status, notes).

    - If the file does not exist -> (BROKEN, "No report written").
    - If the file has no recognizable status line -> (BROKEN, "Unrecognized status ...").
    - Otherwise returns the status found in the report plus a best-effort
      notes string derived from the Issues / Conclusion sections.
    """
    if not report_path.exists():
        return Status.BROKEN, "No report written"

    try:
        content = report_path.read_text(encoding="utf-8")
    except OSError as e:
        return Status.BROKEN, f"Could not read report: {e}"

    status = _extract_status(content)
    if status is None:
        return Status.BROKEN, "Unrecognized or missing status in report"

    notes = _extract_notes(content)
    return status, notes


def _extract_status(content: str) -> Status | None:
    for match in _STATUS_LINE_RE.finditer(content):
        raw = match.group(1).strip().upper()
        # Skip the template placeholder row like
        # "**Status:** PASSED | FAILED | SKIPPED | WARN | BROKEN"
        # (our regex already requires a single token, so this is usually safe,
        # but we also ignore empty matches).
        try:
            return Status(raw)
        except ValueError:
            continue
    return None


def _extract_notes(content: str) -> str:
    """Return the text of the first non-empty Issues/Conclusion section."""
    for section in _NOTE_SECTIONS:
        text = _extract_section(content, section)
        if text:
            return text
    return ""


def _extract_section(content: str, heading: str) -> str:
    """Extract the body under a `## {heading}` section, stopping at the next
    top-level or same-level heading. Returns a stripped, single-line-joined
    string suitable for inclusion in a summary row."""
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^#{{1,2}}\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(content)
    if not match:
        return ""
    body = match.group(1).strip()
    # Drop boilerplate "No issues encountered." values.
    if body.lower().startswith("no issues encountered"):
        return ""
    return body
