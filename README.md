<div align="center">
	<picture>
		<source media="(prefers-color-scheme: dark)" srcset="docs/assets/brand/oriondesk-mark-dark.svg" />
		<source media="(prefers-color-scheme: light)" srcset="docs/assets/brand/oriondesk-mark-light.svg" />
		<img alt="OrionDesk" src="docs/assets/brand/oriondesk-mark-light.svg" width="420" />
	</picture>

	<h1>OrionDesk</h1>
	<p><strong>Windows Personal OS Agent</strong> with local-first execution, safety guardrails, and developer-grade automation utilities.</p>

	<p>
		<img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" />
		<img alt="UI" src="https://img.shields.io/badge/UI-PySide6-41CD52?logo=qt&logoColor=white" />
		<img alt="License" src="https://img.shields.io/badge/License-MIT-blue" />
		<img alt="Roadmap" src="https://img.shields.io/badge/Roadmap-v6%20Planning-6F42C1" />
	</p>
</div>

## Overview

OrionDesk is a modular desktop agent focused on three outcomes: fast command execution, policy-driven safety, and practical automation for daily developer workflows.

## Feature Highlights

- Unified command engine with execution context and risk metadata
- Capability layer for file, process, network, and utility actions
- Smart command assist with typo correction and explain mode
- Execution profiles: strict, balanced, power, and explain-only
- Modern tabbed UI with icon language and snapshot regression coverage

## Navigation

<table>
	<tr>
		<td>
			<strong>Architecture</strong><br/>
			System design, boundaries, and ADR records.<br/>
			<a href="docs/ARCHITECTURE.md">Technical Architecture</a>
		</td>
		<td>
			<strong>Roadmap</strong><br/>
			Product planning and phase-by-phase milestones.<br/>
			<a href="docs/ROADMAP.md">Roadmap v6</a>
		</td>
		<td>
			<strong>Developer API</strong><br/>
			Command and plugin authoring guidelines.<br/>
			<a href="docs/api/PLUGIN_DEVELOPER_GUIDE.md">Plugin Guide</a>
		</td>
	</tr>
	<tr>
		<td>
			<strong>User Manual</strong><br/>
			Practical command usage for end users.<br/>
			<a href="docs/manual/USER_GUIDE.md">User Guide</a>
		</td>
		<td>
			<strong>Wireframe</strong><br/>
			Current UI snapshots and visual references.<br/>
			<a href="docs/WIREFRAME.md">Wireframe Docs</a>
		</td>
		<td>
			<strong>Changelog</strong><br/>
			Release notes and notable project changes.<br/>
			<a href="CHANGELOG.md">Changelog</a>
		</td>
	</tr>
</table>

## Quick Start

```powershell
pip install -r requirements.txt
python main.py
```

## Test

```powershell
pytest -q
```

## Roadmap Status

- PHASE 0–26: Done
- ROADMAP v4 / v1.4: Completed
- ROADMAP v5 / v1.5: Completed
- ROADMAP v6 / v1.6: Active Planning (PHASE 27–31)

## License

This project is licensed under the MIT License. See LICENSE.
