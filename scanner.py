#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║                         S O L O S W E E P   v 1 . 0 . 0         ║
║           AI-Powered Security Scanner for Your Codebase         ║
╚══════════════════════════════════════════════════════════════════╝

What this script does (plain English):
  1. Runs two security scanners (TruffleHog + Semgrep) on your folder.
  2. Filters results to keep only the dangerous stuff:
       - Hardcoded secrets, API keys, passwords, tokens.
       - Insecure local storage (JS localStorage, Android SharedPreferences).
  3. (Optional) Sends each problem to Google Gemini and asks for a code fix.
  4. Saves everything to scan_report.md and prints a summary.

New in v1.0.0:
  • --no-ai flag    – skip AI fix generation entirely, fast scan.
  • --version flag  – print version and exit.
  • Privacy warning after report if secrets were found.
  • Actionable "What to do next" section at the end of the report.
  • Automatic network retry for Gemini (one retry on connection error).

Security policy (KEY RULES):
  • The Gemini API key is read EXCLUSIVELY from the GEMINI_API_KEY
    environment variable. There is no fallback, no default, no hardcoded value.
  • If the variable is missing the script prints a clear error and exits
    immediately — it will never attempt AI fixes without a verified key.
  • On startup the script inspects its own source code and warns you if it
    detects what looks like an accidentally hardcoded key.

Usage:
  python scanner.py /path/to/your/project [--no-ai] [--version]
"""

# ─────────────────────────────────────────────────────────────────
# IMPORTS — We only use Python's built-in standard library.
# No need to "pip install" anything for these imports.
# ─────────────────────────────────────────────────────────────────
import sys
import os
import subprocess
import json
import urllib.request
import urllib.error
import datetime
import shutil
import re
import time  # Only added for the network retry sleep

# ─────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────
REPORT_FILENAME = "scan_report.md"
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)

INSECURE_STORAGE_PATTERNS = [
    "localstorage",
    "sharedpreferences",
    "shared-preferences",
    "insecure-storage",
    "unencrypted-storage",
    "android.insecure",
    "javascript.browser.security.insecure-localstorage",
]

HIGH_RISK_SEVERITIES = {"ERROR", "CRITICAL"}

# ─────────────────────────────────────────────────────────────────
# STEP 0a: SELF-AUDIT — Warn if someone hardcoded the API key.
# (unchanged, same as before)
# ─────────────────────────────────────────────────────────────────
def check_for_hardcoded_key() -> None:
    script_path = os.path.abspath(__file__)
    HARDCODED_KEY_PATTERN = re.compile(
        r'gemini_api_key\s*=\s*["\'][A-Za-z0-9_\-]{8,}',
        re.IGNORECASE,
    )
    SAFE_PLACEHOLDERS = (
        "your_key",
        "paste_your",
        "aizasyb_paste",
        "...",
    )
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return

    warnings_found = []
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if HARDCODED_KEY_PATTERN.search(line):
            lower_line = line.lower()
            if any(placeholder in lower_line for placeholder in SAFE_PLACEHOLDERS):
                continue
            warnings_found.append((line_number, stripped))

    if warnings_found:
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  🚨  SECURITY WARNING: POSSIBLE HARDCODED API KEY DETECTED  ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        for line_number, content in warnings_found:
            redacted = re.sub(r'=\s*["\'].*', '= "***REDACTED***"', content)
            print(f"║  Line {line_number:<5}: {redacted[:52]:<52} ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print("║  ACTION REQUIRED:                                            ║")
        print("║  1. Delete the hardcoded key from this file immediately.     ║")
        print("║  2. Use:  export GEMINI_API_KEY=\"your-key\"  instead.         ║")
        print("║  3. If this file was ever committed to Git, rotate your key  ║")
        print("║     at https://aistudio.google.com/ right now — it may       ║")
        print("║     already be compromised.                                  ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()

# ─────────────────────────────────────────────────────────────────
# STEP 0b: KEY VALIDATION — Strictly require the env variable.
# (unchanged, same as before)
# ─────────────────────────────────────────────────────────────────
def get_gemini_api_key() -> str:
    raw_value = os.environ.get("GEMINI_API_KEY")
    if raw_value is None:
        print(
            "\n❌  GEMINI_API_KEY environment variable is NOT set.\n"
            "\n"
            "   SoloSweep requires this variable to request AI-powered fix\n"
            "   suggestions from Google Gemini. The script cannot continue\n"
            "   without it.\n"
            "\n"
            "   How to fix this:\n"
            "\n"
            "   macOS / Linux (Terminal):\n"
            "     export GEMINI_API_KEY=\"AIzaSyB_your_real_key_here\"\n"
            "\n"
            "   Windows (Command Prompt):\n"
            "     set GEMINI_API_KEY=AIzaSyB_your_real_key_here\n"
            "\n"
            "   Windows (PowerShell):\n"
            "     $env:GEMINI_API_KEY=\"AIzaSyB_your_real_key_here\"\n"
            "\n"
            "   Don't have a key yet? Get one free at:\n"
            "     https://aistudio.google.com/\n"
        )
        sys.exit(1)

    key = raw_value.strip()
    if not key:
        print(
            "\n❌  GEMINI_API_KEY is set but its value is empty.\n"
            "\n"
            "   The variable exists but contains only whitespace.\n"
            "   Please set it to your actual Gemini API key.\n"
        )
        sys.exit(1)

    PLACEHOLDER_PATTERNS = (
        "your_key", "your-key", "paste_your", "paste-your",
        "api_key_here", "api-key-here", "<api_key>", "<gemini",
        "changeme", "replace_me", "replace-me", "insert_key",
        "insert-key", "xxxxxxxxxxx",
    )
    key_lower = key.lower()
    for placeholder in PLACEHOLDER_PATTERNS:
        if placeholder in key_lower:
            print(
                f"\n❌  GEMINI_API_KEY looks like an unfilled placeholder: \"{key}\"\n"
                "\n"
                "   This value resembles an example from documentation rather than\n"
                "   a real API key. Please replace it with your actual Gemini key.\n"
                "\n"
                "   Get a real key (free) at: https://aistudio.google.com/\n"
            )
            sys.exit(1)
    return key

# ─────────────────────────────────────────────────────────────────
# STEP 0c: HELPER — Check that required tools are installed.
# (unchanged)
# ─────────────────────────────────────────────────────────────────
def check_tool_installed(tool_name: str) -> bool:
    if shutil.which(tool_name) is not None:
        return True
    print(f"\n❌  '{tool_name}' is NOT installed or not found on your PATH.")
    if tool_name == "trufflehog":
        print(
            "   ➜  To install TruffleHog, run ONE of these commands:\n"
            "      • macOS/Linux (Homebrew): brew install trufflesecurity/trufflehog/trufflehog\n"
            "      • Any OS (pip):           pip install trufflehog\n"
            "      • Direct download:        https://github.com/trufflesecurity/trufflehog/releases\n"
        )
    elif tool_name == "semgrep":
        print(
            "   ➜  To install Semgrep, run ONE of these commands:\n"
            "      • pip (recommended):   pip install semgrep\n"
            "      • macOS (Homebrew):    brew install semgrep\n"
            "      • Docker:              docker pull returntocorp/semgrep\n"
        )
    return False

# ─────────────────────────────────────────────────────────────────
# STEP 1: RUN TRUFFLEHOG
# (unchanged)
# ─────────────────────────────────────────────────────────────────
def run_trufflehog(folder_path: str) -> list:
    print("🔍  Running TruffleHog to detect leaked secrets...")
    command = ["trufflehog", "filesystem", folder_path, "--json", "--no-update"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        findings = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                finding = json.loads(line)
                findings.append(finding)
            except json.JSONDecodeError:
                pass
        print(f"   ✅  TruffleHog found {len(findings)} raw result(s).")
        return findings
    except subprocess.TimeoutExpired:
        print("   ⚠️  TruffleHog timed out after 5 minutes. Skipping.")
        return []
    except FileNotFoundError:
        print("   ⚠️  TruffleHog could not be launched. Skipping.")
        return []
    except Exception as e:
        print(f"   ⚠️  Unexpected error running TruffleHog: {e}")
        return []

# ─────────────────────────────────────────────────────────────────
# STEP 2: RUN SEMGREP
# (unchanged)
# ─────────────────────────────────────────────────────────────────
def run_semgrep(folder_path: str) -> list:
    print("🔍  Running Semgrep to detect insecure coding patterns...")
    command = ["semgrep", "--config=auto", folder_path, "--json", "--quiet"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=600)
        if not result.stdout.strip():
            print("   ✅  Semgrep returned no output.")
            return []
        data = json.loads(result.stdout)
        findings = data.get("results", [])
        print(f"   ✅  Semgrep found {len(findings)} raw result(s).")
        return findings
    except json.JSONDecodeError:
        print("   ⚠️  Could not parse Semgrep's JSON output. Skipping.")
        return []
    except subprocess.TimeoutExpired:
        print("   ⚠️  Semgrep timed out after 10 minutes. Skipping.")
        return []
    except FileNotFoundError:
        print("   ⚠️  Semgrep could not be launched. Skipping.")
        return []
    except Exception as e:
        print(f"   ⚠️  Unexpected error running Semgrep: {e}")
        return []

# ─────────────────────────────────────────────────────────────────
# STEP 3: FILTER RESULTS
# (unchanged)
# ─────────────────────────────────────────────────────────────────
def filter_trufflehog(raw_findings: list) -> list:
    normalised = []
    for finding in raw_findings:
        detector   = finding.get("DetectorName", "Unknown Detector")
        verified   = finding.get("Verified", False)
        source_meta = finding.get("SourceMetadata", {})
        data_block  = source_meta.get("Data", {})
        file_path = (
            data_block.get("Filesystem", {}).get("file", "")
            or data_block.get("Git", {}).get("file", "")
            or "unknown file"
        )
        line = (
            data_block.get("Filesystem", {}).get("line", 0)
            or data_block.get("Git", {}).get("line", 0)
        )
        snippet = f"Detected by: {detector} | File: {file_path} | Line: {line}"
        normalised.append({
            "source":      "TruffleHog",
            "title":       f"Leaked secret: {detector}",
            "severity":    "CRITICAL" if verified else "HIGH",
            "file":        file_path,
            "line":        line,
            "rule_id":     detector,
            "snippet":     snippet,
            "description": (
                f"TruffleHog detected a **{'verified' if verified else 'likely'}** "
                f"secret for detector `{detector}` in `{file_path}` at line {line}. "
                "Hardcoded secrets in source code are a critical security risk — "
                "they can be stolen by anyone who reads the file."
            ),
        })
    return normalised

def filter_semgrep(raw_findings: list) -> list:
    normalised = []
    for finding in raw_findings:
        rule_id   = finding.get("check_id", "").lower()
        severity  = finding.get("extra", {}).get("severity", "").upper()
        message   = finding.get("extra", {}).get("message", "No description available.")
        file_path = finding.get("path", "unknown file")
        start     = finding.get("start", {})
        line      = start.get("line", 0)
        snippet   = finding.get("extra", {}).get("lines", "").strip()
        is_high_severity    = severity in HIGH_RISK_SEVERITIES
        is_insecure_storage = any(pattern in rule_id for pattern in INSECURE_STORAGE_PATTERNS)
        if not (is_high_severity or is_insecure_storage):
            continue
        category = "Insecure Local Storage" if is_insecure_storage else "Dangerous Code Pattern"
        normalised.append({
            "source":      "Semgrep",
            "title":       f"{category}: {rule_id}",
            "severity":    severity,
            "file":        file_path,
            "line":        line,
            "rule_id":     rule_id,
            "snippet":     snippet or f"(see file {file_path}, line {line})",
            "description": message,
        })
    return normalised

# ─────────────────────────────────────────────────────────────────
# STEP 4: CALL GEMINI API — with network retry (POLISHED)
# ─────────────────────────────────────────────────────────────────
def ask_gemini_for_fix(finding: dict, api_key: str) -> str:
    prompt = (
        "You are a senior security engineer. A security scanner found the following "
        "vulnerability in a codebase. Please provide:\n"
        "1. A brief explanation of WHY this is dangerous (2-3 sentences).\n"
        "2. The EXACT fixed code snippet, with comments explaining each change.\n"
        "3. Any additional best-practice advice (1-2 sentences).\n\n"
        f"**Vulnerability Type:** {finding['title']}\n"
        f"**Severity:** {finding['severity']}\n"
        f"**File:** {finding['file']}, Line {finding['line']}\n\n"
        f"**Scanner Description:**\n{finding['description']}\n\n"
        f"**Vulnerable Code Snippet:**\n```\n{finding['snippet']}\n```\n\n"
        "Respond in Markdown format."
    )
    request_body = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    body_bytes = json.dumps(request_body).encode("utf-8")
    url = f"{GEMINI_ENDPOINT}?key={api_key}"
    req = urllib.request.Request(
        url, data=body_bytes, headers={"Content-Type": "application/json"}, method="POST"
    )

    # ── First attempt ───────────────────────────────────────────
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            response_bytes = response.read()
        response_data = json.loads(response_bytes.decode("utf-8"))
        candidates = response_data.get("candidates", [])
        if not candidates:
            return "_Gemini returned no candidates. The prompt may have been blocked._"
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return "_Gemini returned an empty response._"
        return parts[0].get("text", "_No text in Gemini's response._")
    except urllib.error.URLError as e:
        # Network error — wait and retry once.
        print(f"      ⚠️  Network error, retrying once in 2s ({e.reason})...")
        time.sleep(2)
        try:
            with urllib.request.urlopen(req, timeout=60) as response2:
                response_bytes2 = response2.read()
            response_data2 = json.loads(response_bytes2.decode("utf-8"))
            candidates2 = response_data2.get("candidates", [])
            if not candidates2:
                return "_Gemini returned no candidates after retry._"
            parts2 = candidates2[0].get("content", {}).get("parts", [])
            if not parts2:
                return "_Gemini returned an empty response after retry._"
            return parts2[0].get("text", "_No text in Gemini's response after retry._")
        except Exception as retry_error:
            return f"_Network error after retry: {retry_error}_"
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        return f"_Gemini API error {e.code}: {e.reason}._\n_Details: {error_body[:300]}_"
    except Exception as e:
        return f"_Unexpected error: {e}_"

# ─────────────────────────────────────────────────────────────────
# STEP 5: BUILD THE REPORT — now with "What to do next" (POLISHED)
# ─────────────────────────────────────────────────────────────────
def build_report(findings_with_fixes: list, folder_path: str, ai_used: bool = True) -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    lines.append("# 🔐 SoloSweep Security Report")
    lines.append("")
    lines.append(f"**Scanned folder:** `{folder_path}`  ")
    lines.append(f"**Generated at:** {now}  ")
    lines.append(f"**Total high-risk findings:** {len(findings_with_fixes)}  ")
    if not ai_used:
        lines.append("**AI fixes:** Skipped (`--no-ai` flag used)  ")
    lines.append("")
    lines.append("---")
    lines.append("")

    if not findings_with_fixes:
        lines.append("## ✅ No high-risk findings detected!")
        lines.append("")
        lines.append("Great news — your code looks clean. Keep practising secure coding! 🎉")
        return "\n".join(lines)

    # Table of contents
    lines.append("## Table of Contents")
    for i, finding in enumerate(findings_with_fixes, start=1):
        anchor = f"finding-{i}"
        lines.append(f"{i}. [{finding['title']}](#{anchor})")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Individual findings
    for i, finding in enumerate(findings_with_fixes, start=1):
        anchor = f"finding-{i}"
        severity_emoji = {
            "CRITICAL": "🔴", "HIGH": "🟠", "ERROR": "🟠",
            "MEDIUM": "🟡", "WARNING": "🟡", "LOW": "🟢", "INFO": "🔵",
        }.get(finding["severity"].upper(), "⚪")

        lines.append(f'<a name="{anchor}"></a>')
        lines.append(f"## {i}. {severity_emoji} {finding['title']}")
        lines.append("")
        lines.append(f"| Field     | Value |")
        lines.append(f"|-----------|-------|")
        lines.append(f"| **Source**   | {finding['source']} |")
        lines.append(f"| **Severity** | {finding['severity']} |")
        lines.append(f"| **File**     | `{finding['file']}` |")
        lines.append(f"| **Line**     | {finding['line']} |")
        lines.append(f"| **Rule**     | `{finding['rule_id']}` |")
        lines.append("")
        lines.append("### 📋 Description")
        lines.append("")
        lines.append(finding["description"])
        lines.append("")
        lines.append("### 💥 Vulnerable Code")
        lines.append("")
        lines.append("```")
        lines.append(finding["snippet"])
        lines.append("```")
        lines.append("")
        lines.append("### 🤖 AI-Suggested Fix (Gemini)")
        lines.append("")
        fix_text = finding.get("ai_fix", "_No fix was generated._")
        lines.append(fix_text)
        lines.append("")
        lines.append("---")
        lines.append("")

    # ── NEW "What to do next" section (POLISHED) ───────────────
    lines.append("## 🧭 What to do next")
    lines.append("")
    has_secrets = any(f["source"] == "TruffleHog" for f in findings_with_fixes)
    has_insecure_storage = any(
        "insecure storage" in f["title"].lower() or "localstorage" in f["rule_id"].lower()
        for f in findings_with_fixes
    )
    if has_secrets:
        lines.append("### 🔑 For leaked secrets / API keys")
        lines.append("")
        lines.append("1. **Rotate the key immediately.** Go to the provider's console and generate a new key. The exposed one must be revoked.")
        lines.append("2. **Remove the secret from the code.** Replace the hardcoded value with an environment variable (e.g., `export SECRET_KEY=…`) or use a `.env` file that is listed in `.gitignore`.")
        lines.append("3. **Check your Git history.** If the secret was ever committed, it's still in the repository. Use `git filter-branch` or [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/) to purge it, and force-push.")
        lines.append("4. **Assume compromise.** If the secret was ever pushed to a public repository, assume it has been scraped by bots and rotate it everywhere it was used.")
        lines.append("")
    if has_insecure_storage:
        lines.append("### 📱 For insecure local storage")
        lines.append("")
        lines.append("1. **Never store sensitive data in plain localStorage or unencrypted SharedPreferences.** These are readable by anyone with access to the device or the browser's developer tools.")
        lines.append("2. **On Android**, use [EncryptedSharedPreferences](https://developer.android.com/reference/androidx/security/crypto/EncryptedSharedPreferences) or the DataStore with encryption.")
        lines.append("3. **For web apps**, sensitive data (tokens, keys) should be stored in HTTP‑only, Secure cookies, not in `localStorage`. Consider using backend‑issued session tokens.")
        lines.append("4. **Move critical logic server‑side.** If the data absolutely must be protected, let the backend handle it and only expose what's strictly needed.")
        lines.append("")
    if not has_secrets and not has_insecure_storage:
        lines.append("Your findings are general code patterns. Review the AI suggestions carefully and adapt them to your project's context.")
        lines.append("")

    lines.append("*Report generated by **SoloSweep v1.0.0** — AI-powered security scanning.*")
    return "\n".join(lines)

# ─────────────────────────────────────────────────────────────────
# STEP 6: PRINT SUMMARY
# (unchanged)
# ─────────────────────────────────────────────────────────────────
def print_summary(findings_with_fixes: list, report_path: str):
    print("\n" + "═" * 60)
    print("  S O L O S W E E P   —   S C A N   S U M M A R Y")
    print("═" * 60)
    if not findings_with_fixes:
        print("  ✅  No high-risk findings. Your code looks clean!")
    else:
        print(f"  ⚠️   {len(findings_with_fixes)} high-risk finding(s) detected:\n")
        for i, f in enumerate(findings_with_fixes, start=1):
            severity_tag = f"[{f['severity']}]".ljust(12)
            title = f["title"][:50] + ("…" if len(f["title"]) > 50 else "")
            print(f"  {i:>2}. {severity_tag} {title}")
            print(f"       📄 {f['file']}  (line {f['line']})")
    print("")
    print(f"  📝  Full report saved to: {report_path}")
    print("═" * 60 + "\n")

# ─────────────────────────────────────────────────────────────────
# MAIN — polished with --version, --no-ai, and post-report warning
# ─────────────────────────────────────────────────────────────────
def main():
    # ── Parse command-line arguments ────────────────────────────
    # Separate flags from the folder path.
    args = sys.argv[1:]
    folder_path = None
    ai_enabled = True

    # We'll collect non‑flag arguments; the last one should be the folder.
    positional = []
    for arg in args:
        if arg == "--version":
            print("SoloSweep v1.0.0")
            sys.exit(0)
        elif arg == "--no-ai":
            ai_enabled = False
        else:
            positional.append(arg)

    if len(positional) < 1:
        print(
            "\n❌  Please provide a folder path to scan.\n"
            "   Usage: python scanner.py /path/to/your/project [--no-ai] [--version]\n"
        )
        sys.exit(1)

    folder_path = positional[-1]  # Use the last non‑flag argument as the folder.

    if not os.path.isdir(folder_path):
        print(f"\n❌  The path '{folder_path}' is not a valid directory.\n")
        sys.exit(1)

    print(f"\n🚀  SoloSweep v1.0.0 starting scan of: {folder_path}\n")
    if not ai_enabled:
        print("   ℹ️  AI fix generation is OFF (--no-ai flag detected).\n")

    # ── Check tools are installed ──────────────────────────────
    trufflehog_ok = check_tool_installed("trufflehog")
    semgrep_ok    = check_tool_installed("semgrep")
    if not trufflehog_ok and not semgrep_ok:
        print("\n❌  Neither TruffleHog nor Semgrep is installed. Install at least one.\n")
        sys.exit(1)

    # ── Self-audit for hardcoded key ───────────────────────────
    check_for_hardcoded_key()

    # ── Gemini API key (only needed if AI is enabled) ──────────
    if ai_enabled:
        gemini_api_key = get_gemini_api_key()
        print(f"✅  Gemini API key loaded from environment (ending in …{gemini_api_key[-4:]}).\n")
    else:
        gemini_api_key = None  # Not used

    # ── Run scanners ───────────────────────────────────────────
    raw_trufflehog = run_trufflehog(folder_path) if trufflehog_ok else []
    raw_semgrep    = run_semgrep(folder_path)    if semgrep_ok    else []

    # ── Filter results ────────────────────────────────────────
    print("\n🧹  Filtering results to high-risk findings only...")
    filtered_trufflehog = filter_trufflehog(raw_trufflehog)
    filtered_semgrep    = filter_semgrep(raw_semgrep)
    all_findings = filtered_trufflehog + filtered_semgrep
    severity_order = {"CRITICAL": 0, "HIGH": 1, "ERROR": 1, "MEDIUM": 2,
                      "WARNING": 2, "LOW": 3, "INFO": 4}
    all_findings.sort(key=lambda f: severity_order.get(f["severity"].upper(), 99))
    print(f"   📌  {len(filtered_trufflehog)} TruffleHog finding(s) kept.")
    print(f"   📌  {len(filtered_semgrep)} Semgrep finding(s) kept.")
    print(f"   📌  {len(all_findings)} total high-risk finding(s).\n")

    # ── Ask Gemini for fixes (only if AI enabled) ──────────────
    if ai_enabled and all_findings:
        print(f"🤖  Asking Gemini for fix suggestions ({len(all_findings)} finding(s))...\n")
        for i, finding in enumerate(all_findings, start=1):
            print(f"   [{i}/{len(all_findings)}] Requesting fix for: {finding['title'][:60]}")
            fix = ask_gemini_for_fix(finding, gemini_api_key)
            finding["ai_fix"] = fix
    else:
        # Placeholder message if AI is off or no findings
        for finding in all_findings:
            if not ai_enabled:
                finding["ai_fix"] = "_AI fix skipped (--no-ai flag used)._"
            else:
                finding["ai_fix"] = "_No fix generated._"

    # ── Build and save report ─────────────────────────────────
    print("\n📝  Building report...")
    report_markdown = build_report(all_findings, folder_path, ai_used=ai_enabled)
    report_path = os.path.join(os.getcwd(), REPORT_FILENAME)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_markdown)

    # ── Post-report privacy warning if secrets were found ─────
    if any(f["source"] == "TruffleHog" for f in all_findings):
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  ⚠️  WARNING: The report contains the FILE LOCATIONS of     ║")
        print("║     secrets. Keep it private and never commit it to a       ║")
        print("║     public repository.                                      ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()

    # ── Summary ────────────────────────────────────────────────
    print_summary(all_findings, report_path)

if __name__ == "__main__":
    main()

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║           BEGINNER SETUP GUIDE — READ THIS BEFORE RUNNING               ║
# ╚══════════════════════════════════════════════════════════════════════════╝
# (Same comprehensive guide as before, slightly updated for v1.0.0)
#
#   [The guide text remains the same as previously, not repeated here for brevity.
#    You can leave the existing guide at the end of your file if you prefer.]