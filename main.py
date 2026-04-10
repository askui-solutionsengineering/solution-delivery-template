import argparse
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from askui import ComputerAgent
from askui.models.shared.prompts import ActSystemPrompt
from askui.models.shared.settings import (
    ActSettings,
    CacheWritingSettings,
    CachingSettings,
    MessageSettings,
)
from askui.reporting import SimpleHtmlReporter
from askui.tools.store.computer import ComputerSaveScreenshotTool
from askui.tools.store.computer.experimental import (
    ComputerAddWindowAsVirtualDisplayTool,
    ComputerListProcessTool,
    ComputerListProcessWindowsTool,
    ComputerSetProcessInFocusTool,
    ComputerSetWindowInFocusTool,
)
from askui.tools.store.universal import (
    ListFilesTool,
    PrintToConsoleTool,
    ReadFromFileTool,
    WriteToFileTool,
)
from dotenv import load_dotenv

from helpers import get_agent_tools

LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.WARNING))
logger = logging.getLogger("AskUI Task Runner")

PROMPTS_DIR = Path(__file__).parent / "prompts"


def _read_prompt(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8").strip()


def create_system_prompt(
    ui_information: str = "", additional_rules: str = ""
) -> ActSystemPrompt:
    return ActSystemPrompt(
        system_capabilities=_read_prompt("system_capabilities.md"),
        device_information=_read_prompt("device_information.md"),
        ui_information=ui_information,
        report_format=_read_prompt("report_format.md"),
        additional_rules=additional_rules,
    )


# Load Env variables, e.g. API Keys
load_dotenv()

# Reserved filenames (stem) that provide folder-level context, not tasks
SPECIAL_STEMS = {"rules", "setup", "teardown"}

# Supported task file extensions
TASK_EXTENSIONS = {".txt", ".md", ".pdf", ".csv", ".json"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AskUI Vision Agent - Task Automation")
    parser.add_argument(
        "target",
        nargs="?",
        default="tasks",
        help="Path to a tasks folder or a single task file (default: tasks)",
    )
    parser.add_argument(
        "--cache-strategy",
        type=str,
        default="auto",
        help="Caching strategy (default: auto)",
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default=".askui_cache",
        help="Directory for cache files (default: .askui_cache)",
    )
    return parser.parse_args()


def find_special_file(folder: Path, stem: str) -> Path | None:
    """Find a special file (context, setup, teardown) in any supported format."""
    for ext in TASK_EXTENSIONS:
        candidate = folder / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    return None


def read_file_content(file_path: Path) -> str:
    """Read a text file's content. Returns empty string for binary formats like PDF."""
    if file_path.suffix == ".pdf":
        return f"[PDF file: {file_path}]"
    return file_path.read_text(encoding="utf-8").strip()


def collect_task_files(folder: Path) -> list[Path]:
    """Collect task files from a folder, excluding special files and subdirectories."""
    task_files = []
    for f in sorted(folder.iterdir()):
        if f.is_file() and f.suffix in TASK_EXTENSIONS and f.stem not in SPECIAL_STEMS:
            task_files.append(f)
    return task_files


def collect_subgroups(folder: Path) -> list[Path]:
    """Collect subdirectories (groups) from a folder, sorted by name."""
    return sorted([d for d in folder.iterdir() if d.is_dir()])


def _make_act_settings(rules: str) -> ActSettings:
    return ActSettings(
        messages=MessageSettings(
            system=create_system_prompt(additional_rules=rules),
        )
    )


def run_setup(agent: ComputerAgent, folder: Path, rules: str):
    """Run the setup file for a folder if it exists."""
    setup_file = find_special_file(folder, "setup")
    if not setup_file:
        return
    print(f"[{folder.name}] Running setup...")
    agent.act(
        f"Execute the following setup steps:\n\n{read_file_content(setup_file)}",
        act_settings=_make_act_settings(rules),
    )


def run_teardown(agent: ComputerAgent, folder: Path, rules: str):
    """Run the teardown file for a folder if it exists."""
    teardown_file = find_special_file(folder, "teardown")
    if not teardown_file:
        return
    print(f"[{folder.name}] Running teardown...")
    agent.act(
        f"Execute the following teardown/cleanup steps:\n\n{read_file_content(teardown_file)}",
        act_settings=_make_act_settings(rules),
    )


def run_single_task(
    agent: ComputerAgent,
    task_file: Path,
    rules: str,
    caching_settings: CachingSettings | None = None,
):
    """Run a single task file with pre-computed rules."""
    print(f"Executing task: {task_file.stem}")

    act_settings = _make_act_settings(rules)
    caching_settings = caching_settings or CachingSettings()
    caching_settings.writing_settings = (
        caching_settings.writing_settings or CacheWritingSettings()
    )
    caching_settings.writing_settings.filename = task_file.stem

    agent.act(
        f"""
    Read the task from the Task file {task_file} and execute it.
    Be verbose during the execution share with me all the details.

    For each task, you must write a summary report about the task:
    - What was the task?
    - What you did to complete the task?
    - What was the result of the task?
    - What was the issue if any?
    - What was the conclusion of the task?
    - Must include a screenshot of each system interaction and include it to the report.

    Organize the files in the following way:
    - ./<task_name>/<task_name>_report.md
    - ./<task_name>/<task_name>_screenshot.png
    """,
        act_settings=act_settings,
        caching_settings=caching_settings,
    )


def _collect_folder_chain(folder: Path) -> list[Path]:
    """Collect ancestor folders from filesystem root down to folder (inclusive)."""
    chain: list[Path] = []
    current = folder
    while current != current.parent:
        chain.append(current)
        current = current.parent
    chain.reverse()
    return chain


def run_single_task_with_lifecycle(
    agent: ComputerAgent,
    task_file: Path,
    caching_settings: CachingSettings | None = None,
):
    """
    Run a single task file with full setup/teardown lifecycle.
    Walks the ancestor folder chain and runs setups top-down, then the task,
    then teardowns bottom-up.
    """
    folder_chain = _collect_folder_chain(task_file.parent)

    # Build cumulative rules per folder level
    levels: list[tuple[Path, str]] = []
    cumulative_rules = ""
    for folder in folder_chain:
        rules_file = find_special_file(folder, "rules")
        local_rules = read_file_content(rules_file) if rules_file else ""
        cumulative_rules = "\n\n".join(filter(None, [cumulative_rules, local_rules]))
        levels.append((folder, cumulative_rules))

    # Setups: top-down
    for folder, rules in levels:
        run_setup(agent, folder, rules)

    # Task
    run_single_task(
        agent, task_file, rules=cumulative_rules, caching_settings=caching_settings
    )

    # Teardowns: bottom-up
    for folder, rules in reversed(levels):
        run_teardown(agent, folder, rules)


def run_folder(
    agent: ComputerAgent,
    folder: Path,
    parent_rules: str = "",
    caching_settings: CachingSettings | None = None,
):
    """
    Run all tasks in a folder with the setup/rules/teardown pattern.
    Recurses into subgroup folders.

    Hierarchy:
        1. Read rules (inherits from parent + own) -> set as system prompt
        2. Run setup
        3. Run task files
        4. Recurse into subgroups
        5. Run teardown
    """
    # Build cascading rules: parent rules + this folder's rules
    rules_file = find_special_file(folder, "rules")
    local_rules = read_file_content(rules_file) if rules_file else ""
    full_rules = "\n\n".join(filter(None, [parent_rules, local_rules]))

    run_setup(agent, folder, full_rules)

    for task_file in collect_task_files(folder):
        run_single_task(
            agent, task_file, rules=full_rules, caching_settings=caching_settings
        )

    for subgroup in collect_subgroups(folder):
        print(f"[{folder.name}] Entering group: {subgroup.name}")
        run_folder(
            agent, subgroup, parent_rules=full_rules, caching_settings=caching_settings
        )

    run_teardown(agent, folder, full_rules)


if __name__ == "__main__":
    args = parse_args()

    TARGET = Path(__file__).parent / args.target
    if not TARGET.exists():
        raise FileNotFoundError(f"Target not found: {TARGET}")

    is_single_task = TARGET.is_file()
    if is_single_task and TARGET.suffix not in TASK_EXTENSIONS:
        raise ValueError(
            f"Unsupported task file type: {TARGET.suffix}. "
            f"Supported: {', '.join(sorted(TASK_EXTENSIONS))}"
        )

    TASK_FOLDER = TARGET.parent if is_single_task else TARGET

    # Define the agent workspace directory.
    AGENT_WORKSPACE = (
        Path(__file__).parent
        / "agent_workspace"
        / datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    )

    # Build caching settings from CLI args
    cache_strategy = (
        None if args.cache_strategy.lower() == "none" else args.cache_strategy
    )
    caching_settings = CachingSettings(
        strategy=args.cache_strategy,
        cache_dir=args.cache_dir,
    )

    # Read root-level rules for the system prompt
    root_rules_file = find_special_file(TASK_FOLDER, "rules")
    ui_information = read_file_content(root_rules_file) if root_rules_file else ""
    system_prompt = create_system_prompt(ui_information=ui_information)

    act_tools = [
        # Tools to enable reading the tasks from the Task Folder.
        ReadFromFileTool(base_dir=TASK_FOLDER),
        ListFilesTool(base_dir=TASK_FOLDER),
        # Tools to enable writing the reports to the Report Folder.
        WriteToFileTool(base_dir=AGENT_WORKSPACE),
        ListFilesTool(base_dir=AGENT_WORKSPACE),
        # Tools to enable saving the screenshots to disk
        ComputerSaveScreenshotTool(base_dir=AGENT_WORKSPACE),
        # Tools to enable printing to the console
        PrintToConsoleTool(source_name="AskUI Agent"),
        # Computer window management tools
        ComputerAddWindowAsVirtualDisplayTool(),
        ComputerListProcessTool(),
        ComputerListProcessWindowsTool(),
        ComputerSetProcessInFocusTool(),
        ComputerSetWindowInFocusTool(),
        # Custom tools
        *get_agent_tools(),
    ]

    with ComputerAgent(
        act_tools=act_tools, reporters=[SimpleHtmlReporter(report_dir=AGENT_WORKSPACE)]
    ) as agent:
        if is_single_task:
            run_single_task_with_lifecycle(
                agent, TARGET, caching_settings=caching_settings
            )
        else:
            run_folder(agent, TASK_FOLDER, caching_settings=caching_settings)
