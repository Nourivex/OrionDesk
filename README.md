<div align="center">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="docs/assets/brand/oriondesk-mark-dark.svg" />
<source media="(prefers-color-scheme: light)" srcset="docs/assets/brand/oriondesk-mark-light.svg" />
<img alt="OrionDesk Logo" src="docs/assets/brand/oriondesk-mark-light.svg" width="420" />
</picture>

<h1>OrionDesk</h1>

<p><strong>Local-First OS Intelligence for Windows</strong></p>

<p>
Intent-driven execution, policy-guarded automation, and developer-centric system orchestration.
</p>

<p>
<img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" />
<img alt="PySide6" src="https://img.shields.io/badge/PySide6-Qt%20for%20Python-41CD52?logo=qt&logoColor=white" />
<img alt="Architecture" src="https://img.shields.io/badge/Architecture-Local--First-0A0A0A" />
<img alt="Security" src="https://img.shields.io/badge/Safety-Guardrails-success" />
<img alt="License" src="https://img.shields.io/badge/License-MIT-blue" />
<img alt="Roadmap" src="https://img.shields.io/badge/Roadmap-v6-6F42C1" />
</p>
</div>

---

## Overview

OrionDesk is a modular, local-first desktop agent that transforms high-level intent into structured, policy-aware system execution.

Built for power users and developers, it provides a safe orchestration layer on top of Windows — combining command execution, risk metadata, and workflow automation into a unified interface.

---

## Feature Highlights

- 🧠 **Unified Command Engine**  
  Structured execution with context awareness and risk metadata.

- 🛠 **Capability Layer**  
  File, process, network, and utility actions with guardrails.

- ✍ **Smart Command Assist**  
  Typo correction, intent clarification, and explain mode.

- ⚖ **Execution Profiles**  
  Strict, Balanced, Power, and Explain-only modes for controlled automation.

- 🖥 **Modern Desktop UI**  
  Tabbed interface, consistent icon language, and snapshot regression coverage.


## Navigation

### 🏗 Architecture
System design, module boundaries, and ADR records.  
→ [Technical Architecture](docs/ARCHITECTURE.md)

---

### 🗺 Roadmap
Product planning and phase-by-phase milestones.  
→ [Roadmap v6](docs/ROADMAP.md)

---

### 🧩 Developer API
Command and plugin authoring guidelines.  
→ [Plugin Developer Guide](docs/api/PLUGIN_DEVELOPER_GUIDE.md)

---

### 📘 User Manual
Practical command usage for end users.  
→ [User Guide](docs/manual/USER_GUIDE.md)

---

### 🎨 Wireframe
Current UI snapshots and visual references.  
→ [Wireframe Documentation](docs/WIREFRAME.md)

---

### 📝 Changelog
Release notes and notable project changes.  
→ [Changelog](CHANGELOG.md)


## 🚀 Quick Start

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
````

### 2. Run OrionDesk

```powershell
python main.py
```

OrionDesk will start with the default execution profile and local capability layer enabled.

---

## 🧪 Testing

Run the full test suite:

```powershell
pytest -q
```

Snapshot regression and command execution coverage are included in the test pipeline.

---

## 🗺 Roadmap Status

**Current Development Cycle: v1.6 (Roadmap v6)**

* PHASE 0–26 → ✅ Completed
* ROADMAP v4 (v1.4) → ✅ Released
* ROADMAP v5 (v1.5) → ✅ Released
* ROADMAP v6 (v1.6) → 🔄 Active Planning (PHASE 27–31)

See full details in the [Roadmap Documentation](docs/ROADMAP.md).

---

## 📄 License

Distributed under the MIT License.
See [`LICENSE`](LICENSE) for more information.

````