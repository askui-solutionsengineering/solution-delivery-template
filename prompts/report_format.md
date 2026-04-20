Write the test case report in Markdown format.

## Status Definitions

- **PASSED** — Step executed successfully, actual result matches expected result.
- **FAILED** — Step executed but actual result does not match expected result.
- **SKIPPED** — Step was intentionally not executed (e.g., precondition not met, not applicable).
- **WARN** — Step passed but with warnings (e.g., slow response, minor visual deviation).
- **BROKEN** — Step could not execute due to an error (crash, infrastructure failure, exception).

## Report Structure

```markdown
# Test Case Report: {test_case_name}

**Test Case ID:** {test_case_id}
**Date:** {execution_date}
**Status:** PASSED | FAILED | SKIPPED | WARN | BROKEN

## Summary

Brief description of the test case objective and outcome.

## Preconditions

1. {precondition_1}
2. {precondition_2}

## Test Steps

1. **{action}** — Status: **{status}**
   - **Agent Interpretation:** {agent_interpretation}
   - **Expected:** {expected_result}
   - **Actual:** {actual_result}
   - ![Step 1](step_1.png)

2. **{action}** — Status: **{status}**
   - **Agent Interpretation:** {agent_interpretation}
   - **Expected:** {expected_result}
   - **Actual:** {actual_result}
   - ![Step 2](step_2.png)


## Postconditions

1. {postcondition_1}
2. {postcondition_2}

## Issues

Describe any issues encountered during execution. If none, write "No issues encountered."

## Conclusion

Final assessment of the test case execution.
```

## Rules

- Include a screenshot for each step and embed it in the list.
- Mark each step as PASSED, FAILED, SKIPPED, WARN, or BROKEN.
- Overall status: BROKEN if any step broke, FAILED if any step failed, WARN if any step warned, SKIPPED if all steps skipped, otherwise PASSED.
- Use code blocks for error messages or logs.
- All report artifacts (screenshots, report file) must be in the same subdirectory.
- File organization: `{test_name}/{test_name}_report.md`, `{test_name}/step_{n}.png`.
