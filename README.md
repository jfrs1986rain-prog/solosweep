<div align="center">
  <h1>🛡️ SoloSweep</h1>
  <p><em>Find & fix security leaks before they leak you.</em></p>

  [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
  [![GitHub release (latest by date)](https://img.shields.io/github/v/release/jfrs1986rain-prog/solosweep)](https://github.com/jfrs1986rain-prog/solosweep/releases)
  [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
</div>

---

## 🔍 What is SoloSweep?

SoloSweep is a **zero‑configuration CLI security scanner** built for indie hackers and micro‑SaaS founders.  
It runs on your machine, never uploads your code, and uses AI (Google Gemini) to give you copy‑paste code fixes for every finding.

**Why?** Because enterprise tools are too expensive, too complex, and too noisy for a one‑person team.

---

## ⚡ Quick Start (2 minutes)

### 1. Download the binary
👉 [**Download SoloSweep.exe (Windows)**](https://github.com/jfrs1986rain-prog/solosweep/releases/latest)

macOS / Linux users: run from source (see below).

### 2. Get a free Gemini API key
Go to [Google AI Studio](https://aistudio.google.com/), click **Get API key**, and copy it.

### 3. Set the key as an environment variable

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your-key-here"
