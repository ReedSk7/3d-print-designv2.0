from __future__ import annotations

import importlib.metadata
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from core import environment
from core.workflow.openscad import OpenSCADNotFound


def test_missing_lock_is_reported_without_dependency_imports(tmp_path: Path) -> None:
    result = environment.dependency_checks(tmp_path)
    assert result[0]["status"] == "fail"
    assert "requirements-lock.txt" in result[0]["detail"]


def test_missing_and_mismatched_dependencies_fail_with_corrective_action(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "requirements-lock.txt").write_text("numpy==2.4.4\ntrimesh==4.11.5\n")

    def distribution(name: str):
        if name == "numpy":
            raise importlib.metadata.PackageNotFoundError(name)
        return SimpleNamespace(version="0.0.1", locate_file=lambda _: tmp_path)

    monkeypatch.setattr(importlib.metadata, "distribution", distribution)
    monkeypatch.setattr(environment, "probe", lambda *_: subprocess.CompletedProcess([], 1, "incompatible dependency\n", ""))
    result = environment.dependency_checks(tmp_path)
    assert len(result) == 3
    assert all(item["status"] == "fail" for item in result)
    assert all(item["corrective_action"] for item in result)
    assert result[1]["version"] == "0.0.1"
    assert "incompatible" in result[2]["detail"]


def test_windows_only_dependency_is_skipped_elsewhere(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "requirements-lock.txt").write_text("colorama==0.4.6 ; sys_platform == 'win32'\n")
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(importlib.metadata, "distribution", lambda _: pytest.fail("Windows-only package inspected on Linux"))
    monkeypatch.setattr(environment, "probe", lambda *_: subprocess.CompletedProcess([], 0, "No broken requirements found.\n", ""))
    result = environment.dependency_checks(tmp_path)
    assert len(result) == 1
    assert result[0]["status"] == "pass"


def test_invalid_lock_marker_is_a_required_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "requirements-lock.txt").write_text("numpy>=2.4\n")
    monkeypatch.setattr(environment, "probe", lambda *_: subprocess.CompletedProcess([], 0, "OK", ""))
    assert environment.dependency_checks(tmp_path)[0]["status"] == "fail"


def test_empty_lock_cannot_report_dependency_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "requirements-lock.txt").write_text("# empty by mistake\n")
    monkeypatch.setattr(environment, "probe", lambda *_: subprocess.CompletedProcess([], 0, "OK", ""))
    result = environment.dependency_checks(tmp_path)
    assert result[0]["status"] == "fail"
    assert result[0]["required"]


@pytest.mark.parametrize("content", ["model = [\n", 'model = "secret-private-model"\nsandbox_mode = "danger-full-access"\n'])
def test_bad_config_fails_without_displaying_private_values(tmp_path: Path, content: str) -> None:
    config = tmp_path / ".codex" / "config.toml"
    config.parent.mkdir()
    config.write_text(content)
    result = environment.codex_config_check(tmp_path)
    assert result["status"] == "fail"
    assert "secret-private-model" not in json.dumps(result)
    assert result["accepted_by_client"] == "unknown"
    assert result["active_in_session"] == "unknown"


def test_valid_config_reports_only_written_not_active(tmp_path: Path) -> None:
    config = tmp_path / ".codex" / "config.toml"
    config.parent.mkdir()
    config.write_text("\n".join(f'{key} = "{value}"' for key, value in environment.CONFIG_VALUES.items()))
    result = environment.codex_config_check(tmp_path)
    assert result["status"] == "pass"
    assert result["written_values"] == environment.CONFIG_VALUES
    assert result["accepted_by_client"] == result["active_in_session"] == "unknown"


def test_missing_openscad_is_a_required_failure_and_bambu_is_optional(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing():
        raise OpenSCADNotFound(("synthetic missing tool",))

    monkeypatch.setattr(environment, "find_openscad", missing)
    monkeypatch.setattr(environment, "find_tool", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(environment, "dependency_checks", lambda _: [])
    monkeypatch.setattr(environment, "vscode_extension_check", lambda: environment.check("Codex VS Code extension", False, "warning", "missing"))
    result = environment.collect_environment()
    assert not result["required_checks_passed"]
    assert "OpenSCAD" in result["required_failures"]
    assert "Bambu Studio" not in result["required_failures"]
    assert result["printer_connection"] == "not attempted"


def test_paths_with_spaces_are_probed_as_one_argument(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    executable = tmp_path / "Program Files" / "Tool App" / "tool.exe"
    seen = {}

    def run(command, **kwargs):
        seen.update(command=command, kwargs=kwargs)
        return subprocess.CompletedProcess(command, 0, "tool 1.0\n", "")

    monkeypatch.setattr(subprocess, "run", run)
    result = environment.executable_check("test tool", True, executable, "fix it")
    assert result["status"] == "pass"
    assert seen["command"] == [str(executable), "--version"]
    assert seen["kwargs"]["shell"] is False
    assert seen["kwargs"]["timeout"] == environment.PROBE_TIMEOUT_SECONDS
    assert seen["kwargs"]["cwd"] == environment.ROOT


def test_probe_timeout_is_actionable(monkeypatch: pytest.MonkeyPatch) -> None:
    def timeout(*_):
        raise subprocess.TimeoutExpired(["tool", "--version"], 15)

    monkeypatch.setattr(environment, "probe", timeout)
    result = environment.executable_check("test tool", True, Path("tool"), "repair tool")
    assert result["status"] == "fail"
    assert result["corrective_action"] == "repair tool"


def test_invalid_explicit_bambu_path_does_not_fall_back(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BAMBUSTUDIO_PATH", str(tmp_path / "missing.exe"))
    monkeypatch.setattr(environment.shutil, "which", lambda _: pytest.fail("Invalid explicit path must not fall back"))
    result = environment.bambu_check()
    assert result["status"] == "warning"
    assert "BAMBUSTUDIO_PATH" in result["detail"]
    assert not result["required"]


def test_bambu_probe_only_runs_help_and_never_claims_packaging(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    executable = tmp_path / "Bambu Studio" / "bambu-studio.com"
    monkeypatch.setattr(environment, "find_tool", lambda *_args, **_kwargs: executable)
    calls = []

    def probe(*arguments):
        calls.append(arguments)
        return subprocess.CompletedProcess([], 0, "Bambu Studio 2.0\n--help --export-3mf --load-settings\n", "")

    monkeypatch.setattr(environment, "probe", probe)
    result = environment.bambu_check()
    assert calls == [(executable, "--help")]
    assert result["status"] == "pass"
    assert result["packaging_verified"] is False
    assert result["cli_options"] == ["--export-3mf", "--help", "--load-settings"]


def test_extension_report_is_metadata_only(tmp_path: Path) -> None:
    extension = tmp_path / ".vscode" / "extensions" / "openai.chatgpt-0.5.0"
    extension.mkdir(parents=True)
    (extension / "package.json").write_text(json.dumps({"publisher": "openai", "name": "chatgpt", "version": "0.5.0", "private": "do-not-show"}))
    result = environment.vscode_extension_check(tmp_path)
    assert result["status"] == "pass"
    assert result["extensions"][0]["version"] == "0.5.0"
    assert "do-not-show" not in json.dumps(result)


def test_old_python_cli_reports_action_before_importing_tomllib(repo_root, monkeypatch, capsys):
    import importlib.util
    monkeypatch.syspath_prepend(str(repo_root/'scripts'))
    spec = importlib.util.spec_from_file_location('doctor_cli_fixture', repo_root/'scripts/check_environment.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    monkeypatch.setattr(sys, 'version_info', (3,10,0))
    monkeypatch.setattr(sys, 'argv', ['check_environment.py', '--json'])
    assert module.main() == 1
    result = json.loads(capsys.readouterr().out)
    assert result['required_failures'] == ['Python']
    assert '3.12' in result['corrective_action']
