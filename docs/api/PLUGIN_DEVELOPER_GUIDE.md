<div align="center">
  <h1>Plugin Developer Guide</h1>
  <p>How to implement, register, and validate OrionDesk plugin commands.</p>
</div>

## Audience

Developers who want to add new commands to OrionDesk through the plugin registry.

## Prerequisites

- Python 3.11+
- Familiarity with OrionDesk command contracts
- Local test environment with `pytest`

## Plugin Contract

Each plugin exports `COMMAND_DEFINITIONS` as a list of command metadata records.

Required fields:

- `keyword`
- `usage`
- `min_args`
- `handler_name`
- `dangerous`

Optional fields:

- `max_args`
- `first_arg_equals`

## Recommended Workflow

1. Add a plugin file in `plugins/`.
2. Define command records in `COMMAND_DEFINITIONS`.
3. Implement the target handler on the router.
4. Add unit tests under `tests/`.
5. Run full regression before merge.

## Minimal Example

Create a new file under `plugins/` and define a command record in `COMMAND_DEFINITIONS`.

Then implement the referenced handler method on the router class.

## Safety Requirements

- Mark destructive actions as `dangerous=True`.
- Route high-risk actions through policy and guardrails.
- Do not bypass whitelist or profile checks.

## Testing Requirements

- Add unit tests in `tests/` for:
  - contract validation
  - happy path execution
  - policy/guardrail behavior

## Validation Checklist

- Command appears in suggestion list
- Usage hint renders correctly
- Session and logs capture execution metadata
- Full test suite passes
