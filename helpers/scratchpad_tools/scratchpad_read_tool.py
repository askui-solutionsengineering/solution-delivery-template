from pathlib import Path

from askui.models.shared.tools import Tool

SCRATCHPAD_FILENAME = "scratchpad.txt"


class ScratchpadReadTool(Tool):
    """Reads the full contents of the scratchpad."""

    def __init__(self, base_dir: str | Path):
        super().__init__(
            name="scratchpad_read_tool",
            description=(
                "Read the full contents of the scratchpad. "
                "Use this to retrieve information that was previously persisted."
            ),
        )
        self._file_path = Path(base_dir) / SCRATCHPAD_FILENAME
        self.is_cacheable = True

    def __call__(self) -> str:
        if not self._file_path.exists():
            return "Scratchpad is empty."
        content = self._file_path.read_text(encoding="utf-8").strip()
        if not content:
            return "Scratchpad is empty."
        return content
