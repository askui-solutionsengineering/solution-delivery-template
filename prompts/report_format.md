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
Example: `task_test_login/click_login_button.png`, `task_test_login/login_analysis.md`.
