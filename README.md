<div align="center">

<img src="https://via.placeholder.com/120x120/0d1117/58a6ff?text=🛡️" alt="SoloSweep Logo" width="100" />

# SoloSweep

### Zero‑configuration AI‑powered security scanner for solo developers and micro‑SaaS founders.

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e.svg?style=for-the-badge)](https://github.com/jfrs1986rain-prog/solosweep/blob/main/LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3b82f6.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![GitHub Release](https://img.shields.io/github/v/release/jfrs1986rain-prog/solosweep?style=for-the-badge&color=f59e0b&label=Latest%20Release)](https://github.com/jfrs1986rain-prog/solosweep/releases)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-a855f7.svg?style=for-the-badge)](https://github.com/jfrs1986rain-prog/solosweep/pulls)

<br/>

**[⬇️ Download for Windows](#-installation)** · **[🌐 Try the Online Demo](https://solosweep.vercel.app)** · **[📖 Read the Docs](#-table-of-contents)** · **[🐛 Report a Bug](https://github.com/jfrs1986rain-prog/solosweep/issues)**

<br/>

<img src="https://via.placeholder.com/900x480/0d1117/58a6ff?text=SoloSweep+Terminal+Demo" alt="SoloSweep demo screenshot" width="860" style="border-radius:10px;" />

</div>

---

## 📋 Table of Contents

- [What is SoloSweep?](#-what-is-solosweep)
- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Run from Source](#-run-from-source)
- [Online Demo](#-online-demo)
- [Screenshots](#-screenshots)
- [How It Works](#-how-it-works)
- [Privacy & Security](#-privacy--security)
- [Roadmap](#️-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔍 What is SoloSweep?

SoloSweep is a **dead-simple, one-command security scanner** built specifically for indie hackers, solo developers, and micro-SaaS founders who ship fast and don't have a dedicated security team watching their back.

You write the code. SoloSweep makes sure you haven't accidentally shipped your AWS secret key, left a hardcoded password in your repo, or stored sensitive data in plaintext localStorage — before an attacker finds it for you.

**No config files. No dashboards. No subscriptions.** Just run it on your project folder and get a clean, actionable Markdown report in seconds.

```bash
solosweep /path/to/your/project
```

> **Powered by:** [TruffleHog](https://github.com/trufflesecurity/trufflehog) · [Semgrep](https://semgrep.dev/) · [Google Gemini](https://aistudio.google.com/)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **Secret Scanning** | Detects hardcoded API keys, tokens, passwords, and credentials using TruffleHog's comprehensive ruleset |
| 🧠 **Insecure Pattern Detection** | Finds dangerous code patterns — unencrypted `localStorage`, insecure `SharedPreferences`, eval abuse, and more via Semgrep |
| 🤖 **AI-Powered Fixes** | Google Gemini reads your vulnerable snippet and generates an exact, ready-to-paste code fix with an explanation |
| 📋 **Clean Markdown Report** | Every scan produces a beautifully formatted `.md` report with a "What to Do Next" action checklist |
| ⚡ **`--no-ai` Offline Mode** | Runs fully offline with no external calls — perfect for air-gapped environments or privacy-sensitive codebases |
| 🛡️ **Self-Audit Protection** | SoloSweep scans itself — it will warn you if you accidentally hardcode a key inside the script |
| 🏠 **Privacy-First Architecture** | All scanning is local. Only isolated, anonymized code snippets (never whole files) are sent to Gemini for fix generation |

---

## 💾 Installation

### Option A — Windows Executable (Recommended, No Python Required)

Download the pre-built `.exe` — no installation, no dependencies. Just download and run.

<div align="center">

**[⬇️ Download SoloSweep.exe (Windows)](https://github.com/jfrs1986rain-prog/solosweep/releases/download/v1.0.0/SoloSweep.exe)**

</div>

1. Download `SoloSweep.exe` from the link above.
2. Place it anywhere on your system (e.g., `C:\Tools\SoloSweep.exe`).
3. Optionally, add that folder to your `PATH` so you can call `solosweep` from any terminal.

### Option B — Run from Source (macOS / Linux / Windows)

See the [Run from Source](#-run-from-source) section below.

---

## 🚀 Quick Start

### Step 1 — Get a Free Gemini API Key

SoloSweep uses Google Gemini's **free tier** for AI-powered fix generation. No credit card required.

1. Visit [https://aistudio.google.com/](https://aistudio.google.com/)
2. Sign in with your Google account.
3. Click **Get API Key → Create API Key**.
4. Copy the key.

### Step 2 — Set the Environment Variable

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY = "your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

**macOS / Linux:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

> 💡 **Pro tip:** Add the export line to your `~/.bashrc` or `~/.zshrc` so you only have to do this once.

### Step 3 — Run Your First Scan

```bash
# Scan a project directory
solosweep /path/to/your/project

# Windows .exe users
SoloSweep.exe C:\Users\you\my-saas-project
```

That's it. SoloSweep will:
- 🔍 Scan for hardcoded secrets
- 🧠 Detect insecure code patterns
- 🤖 Generate AI-powered fixes for each finding
- 📋 Save a `solosweep-report.md` in your current directory

### Offline / Privacy Mode

To run without any network calls (no Gemini, fully local):

```bash
solosweep /path/to/project --no-ai
```

Findings will still be reported — you just won't get the AI-generated fix suggestions.

---

## 🛠 Run from Source

Prefer to run from source? SoloSweep requires Python 3.8+ and two external tools.

### Prerequisites

Install the required tools:

```bash
# Install TruffleHog
pip install trufflehog

# Install Semgrep
pip install semgrep

# Install Python dependencies
pip install google-generativeai
```

> **macOS (Homebrew):**
> ```bash
> brew install trufflehog semgrep
> ```

### Clone & Run

```bash
# 1. Clone the repository
git clone https://github.com/jfrs1986rain-prog/solosweep.git
cd solosweep

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Set your API key
export GEMINI_API_KEY="your-api-key-here"

# 4. Run SoloSweep
python solosweep.py /path/to/your/project

# 5. Offline mode
python solosweep.py /path/to/your/project --no-ai
```

### Requirements at a Glance

| Requirement | Version | Purpose |
|---|---|---|
| Python | 3.8+ | Runtime |
| TruffleHog | Latest | Secret scanning |
| Semgrep | Latest | Pattern detection |
| `google-generativeai` | Latest | Gemini API client |
| Gemini API Key | — | AI fix generation (optional) |

---

## 🌐 Online Demo

Don't want to install anything? Try the **web-based quick scan** at:

### 👉 [solosweep.vercel.app](https://solosweep.vercel.app)

Paste a code snippet and get instant secret detection and AI-generated fixes in your browser. *(Note: the online demo has a file size limit and is intended for quick evaluation only. For full project scans, use the CLI.)*

---

## 📸 Screenshots

### Scan Output — Terminal

<div align="center">
<img src="https://via.placeholder.com/860x440/0d1117/22c55e?text=Terminal+Scan+Output" alt="Terminal scan output" width="860" />
</div>

*SoloSweep running on a sample Node.js project — secrets and insecure patterns detected in seconds.*

---

### Generated Markdown Report

<div align="center">
<img src="https://via.placeholder.com/860x520/0d1117/f59e0b?text=solosweep-report.md+Preview" alt="Markdown report preview" width="860" />
</div>

*The `solosweep-report.md` report — severity-ranked findings, exact file/line references, and AI-generated fixes.*

---

### AI-Generated Fix Example

<div align="center">
<img src="https://via.placeholder.com/860x440/0d1117/a855f7?text=Gemini+AI+Fix+Example" alt="AI fix generation" width="860" />
</div>

*Gemini explains the vulnerability and provides an exact, ready-to-paste replacement.*

---

## ⚙️ How It Works

SoloSweep chains three best-in-class tools into a single, seamless pipeline:

```
Your Project Folder
       │
       ▼
┌─────────────────────────────┐
│  1. TruffleHog              │  ← Scans git history & files for
│     Secret Scanning         │    API keys, tokens, passwords
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  2. Semgrep                 │  ← Detects insecure code patterns:
│     Pattern Detection       │    localStorage, eval(), hardcoded
└──────────────┬──────────────┘    credentials, weak crypto, etc.
               │
               ▼
┌─────────────────────────────┐
│  3. Google Gemini           │  ← Receives isolated vulnerable
│     AI Fix Generation       │    snippet → returns exact fix
│     (--no-ai to skip)       │    + explanation
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  solosweep-report.md        │  ← Severity-ranked, actionable
│  Clean Markdown Report      │    "What to Do Next" checklist
└─────────────────────────────┘
```

### What SoloSweep Detects

**Secrets (TruffleHog)**
- AWS Access Keys & Secret Keys
- GitHub / GitLab Personal Access Tokens
- Stripe, Twilio, SendGrid API Keys
- Google Cloud / Firebase credentials
- Generic high-entropy strings matching secret patterns
- Passwords and connection strings in source code

**Insecure Patterns (Semgrep)**
- Sensitive data written to `localStorage` or `sessionStorage`
- Android `SharedPreferences` without encryption
- Use of `eval()` with dynamic input
- Hardcoded IPs or internal endpoints
- Weak or deprecated cryptographic algorithms
- SQL queries concatenated with user input

---

## 🏠 Privacy & Security

SoloSweep was designed from the ground up with your privacy in mind.

- ✅ **All scanning is local.** TruffleHog and Semgrep run entirely on your machine.
- ✅ **Only snippets are sent to Gemini.** When AI fix generation is enabled, SoloSweep extracts just the vulnerable code snippet (typically 5–15 lines) — never whole files, never your full codebase.
- ✅ **No telemetry.** SoloSweep does not phone home, collect usage data, or store anything.
- ✅ **Use `--no-ai` for zero external calls.** In offline mode, SoloSweep makes no network requests whatsoever.
- ✅ **Self-auditing.** Before scanning your code, SoloSweep checks its own script for accidentally hardcoded keys. Practice what you preach.

---

## 🗺️ Roadmap

The following improvements are planned for future releases. Contributions are welcome!

- [ ] **v1.1** — GitHub Actions integration (scan on every push)
- [ ] **v1.1** — `.solosweepignore` file support (exclude paths/patterns)
- [ ] **v1.2** — SARIF output format for IDE integration (VS Code, JetBrains)
- [ ] **v1.2** — HTML report output option
- [ ] **v1.3** — Support for additional AI backends (OpenAI, Ollama for fully local AI)
- [ ] **v1.4** — Docker image for CI/CD pipelines
- [ ] **v2.0** — Diff-aware scanning (scan only changed files in a PR)
- [ ] **v2.0** — macOS & Linux pre-built binaries

Have a feature request? [Open an issue](https://github.com/jfrs1986rain-prog/solosweep/issues/new?labels=enhancement&template=feature_request.md) and let's discuss it.

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are warmly welcomed! SoloSweep is a solo-dev-friendly project and aims to stay that way.

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/my-awesome-feature`
3. **Commit** your changes: `git commit -m 'feat: add awesome feature'`
4. **Push** to your branch: `git push origin feature/my-awesome-feature`
5. **Open a Pull Request** — describe what you changed and why

### Development Setup

```bash
git clone https://github.com/jfrs1986rain-prog/solosweep.git
cd solosweep
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Linting, testing tools

# Run tests
pytest tests/

# Lint
ruff check .
```

### Contribution Guidelines

- Please keep PRs focused and small — one feature or fix per PR.
- Add or update tests for any new functionality.
- Follow the existing code style (enforced via `ruff`).
- Update the README if you add user-facing changes.

### Reporting Bugs

Found a bug? Please [open an issue](https://github.com/jfrs1986rain-prog/solosweep/issues/new?labels=bug&template=bug_report.md) with:
- Your OS and Python version
- The command you ran
- The full error output

---

## 📄 License

SoloSweep is released under the **MIT License** — free to use, modify, and distribute for personal and commercial projects.

```
MIT License

Copyright (c) 2024 SoloSweep Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

See the full [LICENSE](https://github.com/jfrs1986rain-prog/solosweep/blob/main/LICENSE) file for details.

---

<div align="center">

Made with ❤️ for the solo dev community.

**[⭐ Star this repo](https://github.com/jfrs1986rain-prog/solosweep)** if SoloSweep saved your codebase — it helps others find the project!

<br/>

[Report Bug](https://github.com/jfrs1986rain-prog/solosweep/issues) · [Request Feature](https://github.com/jfrs1986rain-prog/solosweep/issues) · [Online Demo](https://solosweep.vercel.app) · [Download for Windows](https://github.com/jfrs1986rain-prog/solosweep/releases/download/v1.0.0/SoloSweep.exe)

</div>
