from pathlib import Path

from askui.models.shared.tools import Tool

SCRATCHPAD_FILENAME = "scratchpad.txt"


class ScratchpadWriteTool(Tool):
    """Appends a line to the scratchpad."""

    def __init__(self, base_dir: str | Path):
        super().__init__(
            name="scratchpad_write_tool",
            description=(
                "Append information to the scratchpad. "
                "Use this to persist information for later retrieval."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The text to append to the scratchpad.",
                    },
                },
                "required": ["content"],
            },
        )
        self._file_path = Path(base_dir) / SCRATCHPAD_FILENAME
        self.is_cacheable = True

    def __call__(self, content: str) -> str:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._file_path, "a", encoding="utf-8") as f:
            f.write(content + "\n")
        return f"Written to scratchpad: {content}"
