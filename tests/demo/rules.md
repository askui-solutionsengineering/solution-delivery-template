## Desktop Application Testing

- Use the desktop computer to execute these tests.
- Interact with applications via mouse clicks, keyboard input, and window management.

## Error Handling
- If an infrastructure or tool exception occurs (e.g., gRPC error, connection lost, session expired), you MUST mark the testcase as BROKEN, write the report, and then call `exception_tool` to abort the execution!
- If a non-infrastructure exception occurs (e.g., unexpected application error), you MUST mark the testcase as FAILED and abort the execution!
