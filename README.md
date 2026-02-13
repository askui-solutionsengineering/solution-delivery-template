# AskUI Vision Agent - Solution Delivery Template

A task-driven automation framework built on AskUI Vision Agent that reads tasks from the `tasks/` folder, performs UI interactions, and generates per-task reports with screenshots in a timestamped workspace.

## 📋 Table of Contents

- [Overview](#-overview)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Task Formats](#-task-formats)
- [Agent Tools](#-agent-tools)

## 🎯 Overview

This project automates UI tasks defined in text-based files under the `tasks/` directory. The AskUI Vision Agent:

- Reads tasks from the **Task Folder** (`tasks/`) — supports `.txt`, `.md`, `.csv`, and `.json`
- Executes each task step-by-step via UI automation
- Writes a summary report per task (what was done, result, issues, conclusion)
- Saves screenshots of system interactions and includes them in reports
- Writes all outputs into a timestamped **Agent Workspace** directory

## 📋 Prerequisites

Before you begin, ensure you have:

- **AskUI Shell** installed on your system
- Python 3.12 or higher
- Access to the AskUI platform with valid credentials

### Installing AskUI Shell

If you haven't already, install AskUI Shell following the [official installation guide](https://docs.askui.com/).

## 🚀 Installation

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

## ⚙️ Configuration

Key paths are defined in `main.py`:

- **`TASK_FOLDER`** (`tasks/`): Folder containing task files the agent reads and executes.
- **`AGENT_WORKSPACE`** (`agent_workspace/YYYY-MM-DD_HH-MM-SS/`): Where the agent can write reports and screenshots (timestamped per run).

You can customize the system prompt and UI context by editing the `ui_information` string in `main.py` and the templates in `system_prompt.py`.

## 🎮 Usage

### Running the Agent

Execute the agent to process all tasks in the Task Folder:

```powershell
python ./main.py
```

The agent will:

1. Read all tasks from the `tasks/` directory
2. Execute each task one by one
3. For each task, write a summary report including:
   - What was the task?
   - What you did to complete the task
   - What was the result of the task
   - What was the issue (if any)
   - What was the conclusion of the task
   - Screenshots of each system interaction included in the report

### Output Structure

Each run creates a new workspace directory:

```
agent_workspace/YYYY-MM-DD_HH-MM-SS/
├── <task_name>/
│   ├── <task_name>_report.md
│   └── <task_name>_screenshot.png
└── ... (HTML report artifacts from SimpleHtmlReporter)
```

## 📁 Project Structure

```
solution-delivery-template/
├── tasks/                         # Task definitions (agent reads from here)
│   ├── calculator.csv             # CSV test case (e.g. calculator 256*128)
│   ├── clock_demo.txt             # Text task (clock app, date/time)
│   ├── notepad_hello.md           # Markdown task (Notepad, save file)
│   └── webbrowser.json            # JSON task (browser, gold price search)
├── agent_workspace/               # Generated per run (timestamped)
├── main.py                        # Entry point, VisionAgent setup
├── system_prompt.py               # System prompt and report/behavior rules
├── requirements.txt               # Python dependencies
├── ruff.toml                      # Linting/formatting configuration
├── .vscode/settings.json          # Editor & AskUI Shell terminal profile
├── .gitignore
└── README.md                      # This file
```

## 📝 Task Formats

Tasks can be provided in several formats. The agent reads files from `tasks/` and interprets them as tasks to execute.

### Plain text (`.txt`)

Short step-by-step instructions, e.g. open an app, read and report information, include a screenshot.

**Example** (`clock_demo.txt`):

```
Open the Clock app (or your system's date and time display).
Read and report the current date and time shown in your task summary.
Include a screenshot of the Clock app or time display.
```

### Markdown (`.md`)

Structured task with objective, steps, and deliverables.

**Example** (`notepad_hello.md`): Objective, numbered steps, and deliverables (saved file path, summary, screenshot).

### CSV

Table format with test case ID, name, preconditions, step number, step description, and expected result — suitable for test-case style automation.

**Example columns:** `Test case ID`, `Test case name`, `Precondition`, `Step number`, `Step description`, `Expected result`

### JSON

Structured task with `id`, `name`, `description`, `precondition`, `steps` (array of `number`, `action`, `expectedResult`), and optional `deliverables` (e.g. `summaryRequired`, `screenshotRequired`).

**Example** (`webbrowser.json`): Web Browser Gold Price — open browser, search for gold price in Germany (EUR), report result and source, include screenshot.

## 🛠️ Agent Tools

The **VisionAgent** comes with built-in computer tools for UI automation, including:

- Mouse control (move, click, press, drag)
- Keyboard input (typing, key presses)
- Taking screenshots
- Other desktop interaction capabilities

**In addition**, this project adds the following tools in `main.py` (they extend the default VisionAgent toolset):

- **ReadFromFileTool** (base: Task Folder): Read task file contents
- **ListFilesTool** (Task Folder & Agent Workspace): List files in those directories
- **WriteToFileTool** (base: Agent Workspace): Write reports and other files
- **ComputerSaveScreenshotTool** (base: Agent Workspace): Capture and save screenshots to disk
- **PrintToConsoleTool**: Print messages to the console

Reporting is enhanced by **SimpleHtmlReporter**, which writes HTML reports into the agent workspace.

To add more custom tools, see the [official guide on creating custom tools](https://askui-library.help.usepylon.com/articles/4871023453-creating-custom-tools-for-askui-agents).

## 📄 License

This project is provided as an AskUI solution delivery template.
