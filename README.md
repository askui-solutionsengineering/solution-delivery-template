# AskUI - Solution Delivery Template

A task-driven automation framework built on AskUI Agent that reads tests from the `tests/` folder, performs UI interactions, and generates per-test reports with screenshots in a timestamped workspace. Tests are organized in a hierarchical folder structure with support for rules, setup, teardown, reusable procedures, and test plans.

## Overview

This project automates UI tasks defined in text-based files under the `tests/` directory. The AskUI Agent:

- Reads tests from the **Test Folder** (`tests/`) — supports `.txt`, `.md`, `.csv`, `.json`, and `.pdf`
- Supports **hierarchical test organization** with rules, setup, and teardown per folder
- Supports **reusable procedures** (`procedures/`) — named step sequences injected into the system prompt and referenced by name in tests
- Supports **test plans** (`plans/`) — filter which tests to run based on a plan file
- Executes each test step-by-step via UI automation
- Writes a summary report per test (what was done, result, issues, conclusion)
- Saves screenshots of system interactions and includes them in reports
- Writes all outputs into a timestamped **Agent Workspace** directory
- Supports **custom tools** via the `helpers/` module
- Supports **caching** for repeated test runs

## Project Structure

```
solution-delivery-template/
├── main.py                        # Entry point - hierarchical folder runner
├── requirements.txt               # Python dependencies
├── ruff.toml                      # Linting/formatting configuration
├── helpers/                       # Custom tools and utilities
│   ├── __init__.py
│   ├── get_tools.py               # Tool factory function
│   └── tools/
│       ├── __init__.py
│       └── greeting_tool.py       # Example custom tool
├── prompts/                       # Prompt parts for the system prompt (MD files)
│   ├── system_capabilities.md     # Agent capabilities description
│   ├── device_information.md      # Desktop device context
│   ├── ui_information.md          # UI environment context
│   └── report_format.md           # Report formatting guidelines
├── procedures/                    # Reusable procedure definitions
│   ├── OpenNotepad.md             # Example: open notepad procedure
│   ├── OpenCalculator.md          # Example: open calculator procedure
│   └── SaveAndCloseFile.md        # Example: save and close procedure
├── plans/                         # Test plan files (filter test execution)
├── tests/                         # Test definitions (hierarchical)
│   └── demo/
│       ├── rules.md               # Rules for this test group
│       ├── setup.md               # Setup steps before tests
│       ├── teardown.md            # Cleanup steps after tests
│       ├── calculator.csv         # CSV test case
│       ├── clock_demo.txt         # Text test
│       ├── notepad_hello.md       # Markdown test
│       └── webbrowser.json        # JSON test
├── agent_workspace/               # Generated per run (timestamped)
├── .gitignore
└── README.md                      # This file
```

## Test Hierarchy

Tests are organized in folders under `tests/`. Each folder can contain:

| File | Purpose |
|------|---------|
| `rules.(md\|txt\|csv\|json\|pdf)` | Context/rules injected as system prompt for all tests in folder |
| `setup.(md\|txt\|csv\|json\|pdf)` | Executed before tests in folder |
| `teardown.(md\|txt\|csv\|json\|pdf)` | Executed after all tests in folder |
| `*.csv`, `*.md`, `*.txt`, `*.json`, `*.pdf` | Test files (executed in sorted order) |
| Subdirectories | Subgroups that inherit parent rules |

Rules cascade from parent to child folders, so subgroups inherit their parent's context.

### Example: setup.md

A setup file runs before any tests in the folder. Use it to prepare the environment:

```markdown
## Setup Steps

1. Open the Settings application.
2. Navigate to the "Network" section.
3. Ensure WiFi is enabled before proceeding with tests.
```

### Example: teardown.md

A teardown file runs after all tests in the folder complete. Use it to clean up:

```markdown
## Teardown Steps

1. Close the Settings application.
2. Return to the home screen.
3. Clear any temporary files created during testing.
```

## Procedures

Procedures are **reusable, named step sequences** stored in the `procedures/` directory. They are automatically loaded and injected into the agent's system prompt as "Known Procedures". When a test step references a procedure by name, the agent executes the corresponding steps.

### How Procedures Work

1. Place procedure files (`.md`, `.txt`, `.csv`, `.json`, or `.pdf`) in the `procedures/` directory.
2. Each file defines a named procedure with step-by-step instructions.
3. All procedures are loaded at startup and included in the system prompt.
4. Tests can reference procedures by name — e.g., "Execute the procedure OpenCalculator".

### Creating a Procedure

Create a file in `procedures/` with a descriptive name. The filename (without extension) becomes the procedure name.

**Example: `procedures/OpenCalculator.md`**

```markdown
# Open Calculator

1. Open the Calculator application.
2. Wait until the calculator window is fully loaded and visible.
3. Confirm the calculator is ready by verifying the display shows "0".
```

**Example: `procedures/SaveAndCloseFile.md`**

```markdown
# Save and Close File

1. Press Ctrl+S (or Cmd+S on macOS) to save the current file.
2. If a "Save As" dialog appears, choose the appropriate location and confirm.
3. Wait until the file is saved (title bar no longer shows unsaved indicator).
4. Close the application window by pressing Alt+F4 (or Cmd+Q on macOS).
```

### Referencing Procedures in Tests

In your test files, reference procedures by name:

```markdown
## Steps

1. Execute the procedure OpenCalculator.
2. Enter the calculation 256 * 128.
3. Take a screenshot of the result.
4. Execute the procedure SaveAndCloseFile.
```

The agent will look up the procedure by name from its known procedures and execute the defined steps.

## Plans

Plans let you **selectively run a subset of tests** based on a plan file. Plan files are stored in the `plans/` directory and describe which tests should be executed.

### How Plans Work

1. Place a plan file (`.md`, `.txt`, `.csv`, `.json`, or `.pdf`) in the `plans/` directory.
2. Run with the `--plan` flag: `python main.py --plan my_plan`
3. The agent interprets the plan and selects matching test files from the available tests.
4. Only the selected tests are executed (each with their full setup/teardown lifecycle).

### Example: `plans/smoke_test.md`

```markdown
# Smoke Test Plan

Run only the basic calculator and notepad tests to verify the environment is working.

Include:
- calculator.csv
- notepad_hello.md
```

## Prerequisites

Before you begin, ensure you have:

- **Python** installed on your system
- version >=3.11, <3.14

- **AskUI Credentials** setup in the askui hub

## Installation

### Step 1: Install Python (First Time Only)

Install python on your system, e.g. [here](https://www.python.org/downloads/):

### Step 2: Configure AskUI Credentials (First Time Only)

**Create an Access Token**
   Follow the [Access Token Guide](https://docs.askui.com/02-how-to-guides/01-account-management/04-tokens#create-access-token).


### Step 3: Set Up Python Environment (First Time Only)

Create the virtual environment and activate it:

```powershell
python -m venv .venv
.venv\Scripts\Activate (Windows)
source .venv\bin\activate (Mac/Linux)
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

- **`TEST_FOLDER`** (`tests/`): Folder containing test files the agent reads and executes.
- **`PROCEDURES_DIR`** (`procedures/`): Folder containing reusable procedure definitions.
- **`PLANS_DIR`** (`plans/`): Folder containing test plan files.
- **`AGENT_WORKSPACE`** (`agent_workspace/YYYY-MM-DD_HH-MM-SS/`): Where the agent can write reports and screenshots (timestamped per run).

You can customize the system prompt by editing the markdown files in `prompts/`:
- `system_capabilities.md` — Agent capabilities and behavior rules
- `device_information.md` — Information about the device being controlled
- `ui_information.md` — UI environment context
- `report_format.md` — Report formatting guidelines

## Usage

### Running Tests

```bash
# Run all tests from the default tests/ folder
python main.py

# Run tests from a specific subfolder
python main.py tests/demo

# Run a single test file (with setup/teardown from its folder hierarchy)
python main.py tests/demo/calculator.csv

# Run tests matching a plan
python main.py --plan smoke_test

# Custom caching options
python main.py tests/demo --cache-strategy auto --cache-dir .askui_cache
```

### Output Structure

Each run creates a new workspace directory:

```
agent_workspace/YYYY-MM-DD_HH-MM-SS/
├── <test_name>/
│   ├── <test_name>_report.md
│   └── step_1.png, step_2.png, ...
├── summary_report.md
└── ... (HTML report artifacts from SimpleHtmlReporter)
```

### Adding New Tests

1. Create a new folder under `tests/` for your test group
2. Add a `rules.md` with context and rules for the group
3. Optionally add `setup` and `teardown` files
4. Add test files (CSV, Markdown, etc.) — they execute in sorted order

### Adding Procedures

1. Create a new file in `procedures/` (e.g., `procedures/MyProcedure.md`)
2. Write step-by-step instructions the agent should follow
3. Reference the procedure by name in your test files

### Adding Custom Tools

1. Create new tool classes in `helpers/tools/`
2. Inherit from `askui.models.shared.tools.Tool`
3. Register tools in `helpers/get_tools.py`

See `helpers/tools/greeting_tool.py` for an example.

## Test Formats

Tests can be provided in several formats. The agent reads files from `tests/` and interprets them as tests to execute.

### Plain text (`.txt`)

Short step-by-step instructions, e.g. open an app, read and report information, include a screenshot.

### Markdown (`.md`)

Structured test with objective, steps, and deliverables.

### CSV

Table format with test case ID, name, preconditions, step number, step description, and expected result — suitable for test-case style automation.

**Example columns:** `Test case ID`, `Test case name`, `Precondition`, `Step number`, `Step description`, `Expected result`

### JSON

Structured test with `id`, `name`, `description`, `precondition`, `steps` (array of `number`, `action`, `expectedResult`), and optional `deliverables`.

### PDF

PDF files are supported as test references. The agent will note the PDF path for processing.

## Agent Tools

The **AskUI Agent** comes with built-in computer tools for UI automation, including:

- Mouse control (move, click, press, drag)
- Keyboard input (typing, key presses)
- Taking screenshots
- Other desktop interaction capabilities

**In addition**, this project adds the following tools:

- **ReadFromFileTool** (base: Test Folder): Read test file contents
- **ListFilesTool** (Test Folder & Agent Workspace): List files in those directories
- **WriteToFileTool** (base: Agent Workspace): Write reports and other files
- **ComputerSaveScreenshotTool** (base: Agent Workspace): Capture and save screenshots to disk
- **Window management tools**: Virtual display, process/window listing, focus control
- **ScratchpadReadTool / ScratchpadWriteTool**: Persist information between test executions (e.g., virtual display IDs)
- **Custom tools**: Registered via `helpers/get_tools.py` (e.g., GreetingTool)

Reporting is enhanced by **SimpleHtmlReporter**, which writes HTML reports into the agent workspace.

## Available VLMs
The project supports multiple Claude models:

claude-opus-4-6
claude-sonnet-4-6 (default)
claude-haiku-4-5-20251001
claude-sonnet-4-5-20250929

## License

This project is provided as an AskUI solution delivery template.
