<div align="center">
	<h1>OrionDesk User Guide</h1>
	<p>Daily usage guide for command execution, safety profiles, and diagnostics.</p>
</div>

## What OrionDesk Does

OrionDesk helps you run local commands, utility actions, and automation workflows from a single desktop shell.

## Quick Start

1. Install dependencies.
2. Run `python main.py`.
3. Open the `Command` tab and enter a command.

## Core Commands

- `open <app>`
- `search <query>` or `search file <query>`
- `sys info`
- `capability <domain> <action> [args]`
- `smart <request>`
- `profile <strict|balanced|power|explain-only>`
- `explain <command>`

## Safety Behavior

- High-risk commands require confirmation in safe modes.
- Execution profiles change risk behavior and action permissions.
- Guardrails block protected targets and restricted paths.

## Tabs Overview

- Command: run commands and view outputs
- Memory: view usage summary
- Settings: theme, channel, tray behavior
- Diagnostics: generate reports and snapshots
- About: version and runtime information

## Troubleshooting

- If command fails, review output badge and diagnostics tab.
- If app is slow, run diagnostics and inspect recent logs.
- If behavior differs by profile, check active execution profile.
