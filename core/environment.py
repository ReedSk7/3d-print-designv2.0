"""Read-only, dependency-free diagnostics for the local development workspace.

This module deliberately imports no third-party packages and never opens owner
specifications, credentials, global Codex configuration, or printer connections.
"""

from __future__ import annotations

import importlib.metadata
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

from core.workflow.openscad import find_openscad, openscad_version

ROOT = Path(__file__).resolve().parents[1]
CONFIG_VALUES = {
    "sandbox_mode": "workspace-write",
    "approval_policy": "on-request",
}
# Optional user choices are validated by the client, not constrained by this doctor.
SESSION_CONFIG_KEYS = {"model", "model_reasoning_effort"}
PROBE_TIMEOUT_SECONDS = 15
PIN = re.compile(r"([A-Za-z0-9_.-]+)==([A-Za-z0-9_.+!-]+)(?:\s*;\s*sys_platform\s*==\s*['\"]win32['\"])?")


def check(name: str, required: bool, status: str, detail: str, **extra: Any) -> dict[str, Any]:
    return {"name": name, "required": required, "status": status, "detail": detail, **extra}


def probe(executable: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    """Use argument lists, never shell quoting; bound broken native tools."""
    return subprocess.run(
        [str(executable), *arguments], capture_output=True, text=True,
        errors="replace", shell=False, check=False, timeout=PROBE_TIMEOUT_SECONDS,
        cwd=ROOT,
    )


def find_tool(names: tuple[str, ...], *, environment: str | None = None,
              candidates: tuple[Path, ...] = ()) -> Path | None:
    if environment and os.environ.get(environment):
        explicit = Path(os.environ[environment]).expanduser()
        if not explicit.is_file():
            raise FileNotFoundError(f"{environment} does not point to an executable file; correct or unset it.")
        return explicit.resolve()
    for name in names:
        located = shutil.which(name)
        if located:
            return Path(located).resolve()
    return next((path.resolve() for path in candidates if path.is_file()), None)


def executable_check(name: str, required: bool, executable: Path | None,
                     corrective_action: str) -> dict[str, Any]:
    if executable is None:
        return check(name, required, "fail" if required else "warning", "Not found.",
                     corrective_action=corrective_action)
    try:
        result = probe(executable, "--version")
        lines = (result.stdout + "\n" + result.stderr).strip().splitlines()
        if result.returncode != 0 or not lines:
            raise RuntimeError(f"version probe exited {result.returncode} or returned no version")
        return check(name, required, "pass", "Version probe succeeded.",
                     path=str(executable), version=lines[0][:300])
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        return check(name, required, "fail" if required else "warning", str(exc),
                     path=str(executable), corrective_action=corrective_action)


def dependency_checks(root: Path) -> list[dict[str, Any]]:
    lock = root / "requirements-lock.txt"
    try:
        lines = lock.read_text(encoding="utf-8").splitlines()
    except OSError:
        return [check("dependency lock", True, "fail", "Cannot read requirements-lock.txt.",
                      corrective_action="Restore requirements-lock.txt from this upgrade branch.")]
    checks = []
    seen = set()
    for number, line in enumerate(lines, start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = PIN.fullmatch(line)
        if not match:
            checks.append(check("dependency lock", True, "fail", f"Unsupported requirement at line {number}; use an exact package==version pin."))
            continue
        name, expected = match.groups()
        normalized = re.sub(r"[-_.]+", "-", name).lower()
        if normalized in seen:
            checks.append(check("dependency lock", True, "fail", f"Duplicate dependency pin at line {number}."))
            continue
        seen.add(normalized)
        if ";" in line and sys.platform != "win32":
            continue
        try:
            distribution = importlib.metadata.distribution(name)
            version = distribution.version
            checks.append(check(
                name, True, "pass" if version == expected else "fail",
                f"Locked version: {expected}.", version=version,
                path=str(distribution.locate_file("")),
                **({"corrective_action": "Run scripts/setup.ps1, or install requirements-lock.txt into the project .venv."}
                   if version != expected else {}),
            ))
        except importlib.metadata.PackageNotFoundError:
            checks.append(check(name, True, "fail", f"Missing dependency; locked version: {expected}.",
                                corrective_action="Run scripts/setup.ps1, or install requirements-lock.txt into the project .venv."))
    if not seen:
        checks.append(check("dependency lock", True, "fail", "No exact dependency pins found.",
                            corrective_action="Restore requirements-lock.txt from this upgrade branch."))
    try:
        result = probe(Path(sys.executable), "-m", "pip", "check")
        checks.append(check("dependency compatibility", True, "pass" if result.returncode == 0 else "fail",
                            (result.stdout.strip() or "pip check failed; pip may be missing.")[:2000],
                            command=[sys.executable, "-m", "pip", "check"],
                            **({"corrective_action": "Run scripts/setup.ps1 to restore the locked project environment."}
                               if result.returncode else {})))
    except (OSError, subprocess.TimeoutExpired) as exc:
        checks.append(check("dependency compatibility", True, "fail", str(exc),
                            corrective_action="Check this interpreter's pip installation, then run scripts/setup.ps1."))
    return checks


def codex_config_check(root: Path) -> dict[str, Any]:
    path = root / ".codex" / "config.toml"
    common = {"path": str(path), "accepted_by_client": "unknown", "active_in_session": "unknown"}
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return check("project Codex configuration", True, "fail", "Missing, unreadable, or invalid TOML; no private contents displayed.",
                     corrective_action="Restore the project .codex/config.toml; do not change global configuration.", **common)
    problems = [f"{key} differs from the reviewed project setting" for key, value in CONFIG_VALUES.items()
                if data.get(key) != value]
    extra_keys = set(data) - set(CONFIG_VALUES) - SESSION_CONFIG_KEYS
    if extra_keys:
        problems.append("Additional project configuration keys need review; values are not displayed")
    return check("project Codex configuration", True, "fail" if problems else "pass",
                 "; ".join(problems) if problems else "TOML and execution safeguards are valid on disk only; model and reasoning are client choices.",
                 written_values={key: data[key] for key, value in CONFIG_VALUES.items() if data.get(key) == value},
                 corrective_action="Choose model and reasoning in the Codex client; confirm active settings and execution permissions there. This check does not select a model, verify account availability, or switch a running session.",
                 **common)


def vscode_extension_check(home: Path | None = None) -> dict[str, Any]:
    home = home or Path.home()
    found = []
    for folder in (home / ".vscode" / "extensions", home / ".vscode-insiders" / "extensions", home / ".vscode-server" / "extensions"):
        try:
            candidates = list(folder.glob("openai.chatgpt-*/package.json"))
        except OSError:
            continue
        for path in candidates:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if data.get("publisher") == "openai" and data.get("name") == "chatgpt":
                    found.append({"path": str(path.parent), "version": str(data.get("version", "unknown"))})
            except (OSError, ValueError):
                continue
    return check("Codex VS Code extension", False, "pass" if found else "warning",
                 "Local extension metadata found; activation is unknown." if found else "No readable Codex extension metadata found in conventional local extension folders.",
                 extensions=found, corrective_action="If using the IDE, inspect its Extensions view and reload it after updating. Remote and portable installations may live elsewhere.")


def bambu_check() -> dict[str, Any]:
    action = "Install/open Bambu Studio separately if needed, or set BAMBUSTUDIO_PATH to its CLI-capable executable. Use the manual-import handoff until real P2S profiles and project re-import are verified."
    candidates = tuple(Path(base) / "Bambu Studio" / name
                       for base in (os.environ.get("ProgramFiles", r"C:\Program Files"), os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
                       for name in ("bambu-studio.com", "bambu-studio.exe"))
    try:
        executable = find_tool(("bambu-studio", "BambuStudio", "bambu-studio.com", "bambu-studio.exe"),
                               environment="BAMBUSTUDIO_PATH", candidates=candidates)
        if executable is None:
            return check("Bambu Studio", False, "warning", "Not found; core CAD functionality remains available.", corrective_action=action)
        result = probe(executable, "--help")
        help_text = result.stdout + "\n" + result.stderr
        options = sorted(set(re.findall(r"(?<![\w-])--[a-z][a-z0-9-]*", help_text)))
        version = re.search(r"(?:Bambu\s*Studio|bambu-studio)[^\r\n]*", help_text, re.IGNORECASE)
        usable = result.returncode == 0 and bool(options)
        return check("Bambu Studio", False, "pass" if usable else "warning",
                     "Help-only CLI capability probe; packaging and compatible P2S profiles are unverified.",
                     path=str(executable), version=version.group(0)[:300] if version else "not exposed by --help",
                     help_exit_code=result.returncode, cli_options=options, packaging_verified=False,
                     corrective_action=action)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return check("Bambu Studio", False, "warning", str(exc), corrective_action=action)


def collect_environment(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    python_supported = (3, 12) <= sys.version_info[:2] <= (3, 13)
    checks = [check("Python", True, "pass" if python_supported else "fail", "Supported validation window: Python 3.12 or 3.13.",
                    path=sys.executable, version=sys.version.split()[0],
                    **({"corrective_action": "Select an installed Python 3.12 or 3.13 for scripts/setup.ps1; install Python separately if missing."} if not python_supported else {}))]
    venv = root / ".venv"
    isolated = sys.prefix != sys.base_prefix and Path(sys.prefix).resolve() == venv.resolve()
    checks.append(check("project virtual environment", True, "pass" if isolated else "fail",
                        "The running interpreter is the project .venv." if isolated else "The running interpreter is not this project's .venv.",
                        path=str(venv), running_prefix=sys.prefix,
                        corrective_action="Run .venv\\Scripts\\python.exe scripts\\check_environment.py on Windows (.venv/bin/python on Linux); create it with scripts/setup.ps1 if missing."))
    checks.extend(dependency_checks(root))
    checks.append(executable_check("Git", True, find_tool(("git",)), "Install Git separately and restart the terminal, then verify git --version."))
    try:
        openscad = find_openscad()
        checks.append(check("OpenSCAD", True, "pass", "Required compiler is available.",
                            path=str(openscad), version=openscad_version(openscad)))
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        checks.append(check("OpenSCAD", True, "fail", str(exc),
                            corrective_action="Install OpenSCAD separately, or set OPENSCAD_PATH to its actual executable (Windows: prefer openscad.com). Compilation/integration is blocked until this passes."))
    checks.append(executable_check("Codex CLI", False, find_tool(("codex", "codex.cmd"), candidates=(Path("/opt/codex/bin/codex"),)),
                                   "Use an existing Codex IDE installation or install/update the CLI separately; restart the client afterward."))
    checks.extend((vscode_extension_check(), codex_config_check(root), bambu_check()))
    checks.append(check("preview display", False, "pass" if sys.platform in ("win32", "darwin") or bool(os.environ.get("DISPLAY")) or shutil.which("xvfb-run") else "warning",
                        "OpenSCAD PNG rendering needs a working graphics context; availability is not a successful render.",
                        corrective_action="Run the preview task; on headless Linux provide a display or use xvfb-run separately."))
    failures = [item["name"] for item in checks if item["required"] and item["status"] == "fail"]
    return {"repository_root": str(root), "read_only": True, "required_checks_passed": not failures,
            "required_failures": failures, "checks": checks,
            "physical_fit": "not assessed", "printer_connection": "not attempted"}


def format_environment(report: dict[str, Any]) -> str:
    lines = ["ENVIRONMENT CHECK PASSED" if report["required_checks_passed"] else "ENVIRONMENT CHECK FAILED",
             f"Repository: {report['repository_root']}"]
    for item in report["checks"]:
        requirement = "required" if item["required"] else "optional"
        lines.append(f"[{item['status'].upper()}] {item['name']} ({requirement}): {item['detail']}")
        for field in ("path", "version", "accepted_by_client", "active_in_session", "corrective_action"):
            if field in item:
                lines.append(f"  {field}: {item[field]}")
        if item.get("extensions"):
            lines.append(f"  extensions: {json.dumps(item['extensions'])}")
        if item.get("written_values"):
            lines.append(f"  written_values: {json.dumps(item['written_values'])}")
        if "cli_options" in item:
            lines.append(f"  cli_options: {', '.join(item['cli_options'])}")
    lines.append("Read-only check. No printer connection or physical-fit validation was performed.")
    return "\n".join(lines)
