from askui.prompts.act_prompts import (
    COMPUTER_USE_CAPABILITIES,
    DESKTOP_DEVICE_INFORMATION,
    ActSystemPrompt,
)

REPORT_FORMAT = """<<report_formatting>>
Markdown format: # Title, ## Sections, ### Subsections.
Document actions, results, issues, conclusions.

**Images:** Use absolute paths:
`<img src="/absolute/path/to/image.png" alt="Description" style="max-width: 100%;">`
Place after relevant text. Label reference images clearly.

**Structure:** Title → Overview → Test Steps (with screenshots) →
Results → Issues → Conclusion.

**Formatting:** Code blocks for errors/logs, tables for data,
**bold** for emphasis. Prefer prose over excessive bullets.

**File Organization:** All artifacts in same subdirectory.
Use task name prefix: `{task_name}/<description>.png`, `{task_name}/<description>.md`.
example: `task_test_login/click_login_button.png`, `task_test_login/login_analysis.md`.
<<</report_formatting>>
"""

ADDITIONAL_RULES = """<<autonomous_operation>>
Work autonomously without confirmation. Complete tasks end-to-end.
After each significant action, save a screenshot and include it in the report.
Save all screenshots in the same directory with task name prefix.

**Issues:** Document immediately in report. Troubleshoot autonomously
(max 3 attempts). If unresolved, document: what was attempted, what failed,
why, and impact. Never raise exceptions—document instead.
Continue with remaining tasks when possible.
<<</autonomous_operation>>

<<tool_usage>>
Execute independent tool calls in parallel (e.g., reading multiple files).
Only sequence when dependencies exist. Default to implementing changes
rather than suggesting. Infer likely actions when intent is unclear.
Use tools to discover details.
<<</tool_usage>>

<<state_management>>
Track progress throughout. Document incrementally in report.
For multi-context windows, save state to files. Use JSON for structured state,
freeform text for progress notes.
<<</state_management>>

<<window_management>>
In case of using a system with multi-screen setup, it's recommended to use the window management
    tools to manage the windows. As if you open application it might open in a different screen
    and you need to switch to the correct screen to interact with the application.
After you are done with the virtual display, select the real display back.
<<</window_management>>
"""


def create_system_prompt(ui_information: str = "") -> ActSystemPrompt:
    """
    Creates a system prompt for the agent.
    Args:
        ui_information: Information about the UI being operated on.
    Returns:
        A system prompt for the agent.
    """
    return ActSystemPrompt(
        system_capabilities=COMPUTER_USE_CAPABILITIES,
        device_information=DESKTOP_DEVICE_INFORMATION,
        ui_information=ui_information,
        report_format=REPORT_FORMAT,
        additional_rules=ADDITIONAL_RULES,
    )
