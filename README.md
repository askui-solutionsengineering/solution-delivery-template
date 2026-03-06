# AskUI Vision Agent - Solution Delivery Template

A task-driven automation framework built on AskUI Vision Agent that reads tasks from the `tasks/` folder, performs UI interactions, and generates per-task reports with screenshots in a timestamped workspace. Tasks are organized in a hierarchical folder structure with support for rules, setup, and teardown.

## Overview

This project automates UI tasks defined in text-based files under the `tasks/` directory. The AskUI Vision Agent:

- Reads tasks from the **Task Folder** (`tasks/`) — supports `.txt`, `.md`, `.csv`, `.json`, and `.pdf`
- Supports **hierarchical task organization** with rules, setup, and teardown per folder
- Executes each task step-by-step via UI automation
- Writes a summary report per task (what was done, result, issues, conclusion)
- Saves screenshots of system interactions and includes them in reports
- Writes all outputs into a timestamped **Agent Workspace** directory
- Supports **custom tools** via the `helpers/` module
- Supports **caching** for repeated task runs

## Project Structure

```
solution-delivery-template/
├── main.py                        # Entry point - hierarchical folder runner
├── system_prompt.py               # System prompt builder (reads from prompts/)
├── requirements.txt               # Python dependencies
├── ruff.toml                      # Linting/formatting configuration
├── .vscode/settings.json          # Editor & AskUI Shell terminal profile
├── helpers/                       # Custom tools and utilities
│   ├── __init__.py
│   ├── get_tools.py               # Tool factory function
│   └── tools/
│       ├── __init__.py
│       └── greeting_tool.py       # Example custom tool
├── prompts/                       # Prompt parts for the system prompt (MD files)
│   ├── system_capabilities.md     # Agent capabilities description
│   ├── device_information.md      # Desktop device context
│   └── report_format.md           # Report formatting guidelines
├── tasks/                         # Task definitions (hierarchical)
│   └── demo/
│       ├── rules.md               # Rules for this task group
│       ├── calculator.csv         # CSV test case
│       ├── clock_demo.txt         # Text task
│       ├── notepad_hello.md       # Markdown task
│       └── webbrowser.json        # JSON task
├── agent_workspace/               # Generated per run (timestamped)
├── .gitignore
└── README.md                      # This file
```

## Task Hierarchy

Tasks are organized in folders under `tasks/`. Each folder can contain:

| File | Purpose |
|------|---------|
| `rules.(md\|txt\|csv\|json\|pdf)` | Context/rules injected as system prompt for all tasks in folder |
| `setup.(md\|txt\|csv\|json\|pdf)` | Executed before tasks in folder |
| `teardown.(md\|txt\|csv\|json\|pdf)` | Executed after all tasks in folder |
| `*.csv`, `*.md`, `*.txt`, `*.json`, `*.pdf` | Task files (executed in sorted order) |
| Subdirectories | Subgroups that inherit parent rules |

Rules cascade from parent to child folders, so subgroups inherit their parent's context.

### Example: setup.md

A setup file runs before any tasks in the folder. Use it to prepare the environment:

```markdown
## Setup Steps

1. Open the Settings application.
2. Navigate to the "Network" section.
3. Ensure WiFi is enabled before proceeding with tests.
```

### Example: teardown.md

A teardown file runs after all tasks in the folder complete. Use it to clean up:

```markdown
## Teardown Steps

1. Close the Settings application.
2. Return to the home screen.
3. Clear any temporary files created during testing.
```

## Prerequisites

Before you begin, ensure you have:

- **AskUI Shell** installed on your system
- Python 3.12 or higher
- Access to the AskUI platform with valid credentials

### Installing AskUI Shell

If you haven't already, install AskUI Shell following the [official installation guide](https://docs.askui.com/).

## Installation

### Step 1: Open AskUI Shell

Launch the AskUI Shell environment:

```bash
askui-shell
```

### Step 2: Configure AskUI Credentials (First Time Only)

1. **Create an Access Token**
   Follow the [Access Token Guide](https://docs.askui.com/02-how-to-guides/01-account-management/04-tokens#create-access-token).

2. **Set Up Your Credentials**
   Follow the [Credentials Setup Guide](https://docs.askui.com/04-reference/02-askui-suite/02-askui-suite/ADE/Public/AskUI-SetSettings#askui-setsettings).

### Step 3: Set Up Python Environment

Activate the virtual environment (run this each time you start a new terminal):

```powershell
AskUI-EnablePythonEnvironment -name 'AskUI-POC' -CreateIfNotExists
```

### Step 4: Install Dependencies

Install required packages (only needed the first time or when `requirements.txt` is updated):

```powershell
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

```bash
cp .env.template .env
# Edit .env file with your API keys
```

## Configuration

Key paths are defined in `main.py`:

- **`TASK_FOLDER`** (`tasks/`): Folder containing task files the agent reads and executes.
- **`AGENT_WORKSPACE`** (`agent_workspace/YYYY-MM-DD_HH-MM-SS/`): Where the agent can write reports and screenshots (timestamped per run).

You can customize the system prompt by editing the markdown files in `prompts/`:
- `system_capabilities.md` — Agent capabilities and behavior rules
- `device_information.md` — Information about the device being controlled
- `report_format.md` — Report formatting guidelines

## Usage

### Running Tasks

```bash
# Run all tasks from the default tasks/ folder
python main.py

# Run tasks from a specific subfolder
python main.py tasks/demo

# Run a single task file (with setup/teardown from its folder hierarchy)
python main.py tasks/demo/calculator.csv

# Custom caching options
python main.py tasks/demo --cache-strategy auto --cache-dir .askui_cache
```

### Output Structure

Each run creates a new workspace directory:

```
agent_workspace/YYYY-MM-DD_HH-MM-SS/
├── <task_name>/
│   ├── <task_name>_report.md
│   └── <task_name>_screenshot.png
└── ... (HTML report artifacts from SimpleHtmlReporter)
```

### Adding New Tasks

1. Create a new folder under `tasks/` for your task group
2. Add a `rules.md` with context and rules for the group
3. Optionally add `setup` and `teardown` files
4. Add task files (CSV, Markdown, etc.) — they execute in sorted order

### Adding Custom Tools

1. Create new tool classes in `helpers/tools/`
2. Inherit from `askui.models.shared.tools.Tool`
3. Register tools in `helpers/get_tools.py`

See `helpers/tools/greeting_tool.py` for an example.

## Task Formats

Tasks can be provided in several formats. The agent reads files from `tasks/` and interprets them as tasks to execute.

### Plain text (`.txt`)

Short step-by-step instructions, e.g. open an app, read and report information, include a screenshot.

### Markdown (`.md`)

Structured task with objective, steps, and deliverables.

### CSV

Table format with test case ID, name, preconditions, step number, step description, and expected result — suitable for test-case style automation.

**Example columns:** `Test case ID`, `Test case name`, `Precondition`, `Step number`, `Step description`, `Expected result`

### JSON

Structured task with `id`, `name`, `description`, `precondition`, `steps` (array of `number`, `action`, `expectedResult`), and optional `deliverables`.

### PDF

PDF files are supported as task references. The agent will note the PDF path for processing.

## Agent Tools

The **VisionAgent** comes with built-in computer tools for UI automation, including:

- Mouse control (move, click, press, drag)
- Keyboard input (typing, key presses)
- Taking screenshots
- Other desktop interaction capabilities

**In addition**, this project adds the following tools:

- **ReadFromFileTool** (base: Task Folder): Read task file contents
- **ListFilesTool** (Task Folder & Agent Workspace): List files in those directories
- **WriteToFileTool** (base: Agent Workspace): Write reports and other files
- **ComputerSaveScreenshotTool** (base: Agent Workspace): Capture and save screenshots to disk
- **PrintToConsoleTool**: Print messages to the console
- **Window management tools**: Virtual display, process/window listing, focus control
- **Custom tools**: Registered via `helpers/get_tools.py` (e.g., GreetingTool)

Reporting is enhanced by **SimpleHtmlReporter**, which writes HTML reports into the agent workspace.

## License

This project is provided as an AskUI solution delivery template.
