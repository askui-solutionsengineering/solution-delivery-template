from datetime import datetime, timezone
from pathlib import Path

from askui import VisionAgent
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

from system_prompt import create_system_prompt

# Define the agent workspace directory.
# This is the only place where the agent can write files to.
AGENT_WORKSPACE = (
    Path(__file__).parent
    / "agent_workspace"
    / datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
)

# Define the Task Folder for the agent.
# Folder, where text based files are stored, that contains the tasks for the agent.
# Agent will read the tasks from this folder and execute them.
TASK_FOLDER = Path(__file__).parent / "tasks"

# Defines the System Prompt for the agent.
ui_information = """
<Information about the UI being operated on>
<Helps the agent to understand the UI being operated on.>
"""
system_prompt = create_system_prompt(ui_information)


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
]

with VisionAgent(
    act_tools=act_tools, reporters=[SimpleHtmlReporter(report_dir=AGENT_WORKSPACE)]
) as agent:
    task_files = (
        list(TASK_FOLDER.glob("*.txt"))
        + list(TASK_FOLDER.glob("*.md"))
        + list(TASK_FOLDER.glob("*.csv"))
        + list(TASK_FOLDER.glob("*.json"))
    )
    for task_file in task_files:
        task_name = task_file.stem
        agent.act(
            f"""
        Read the task from the Task file {task_file} and execute it.
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
        """
        )
