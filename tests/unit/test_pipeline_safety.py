from pathlib import Path

import pytest

from core.workflow.openscad import OpenSCADExecutionError
from core.workflow.pipeline import generate_project


def test_failed_compile_does_not_consume_project_version(
    examples_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail_compile(*args: object, **kwargs: object) -> None:
        raise OpenSCADExecutionError("synthetic compile failure")

    monkeypatch.setattr("core.workflow.pipeline.compile_binary_stl", fail_compile)
    with pytest.raises(OpenSCADExecutionError, match="synthetic compile failure"):
        generate_project(
            examples_dir / "bushing_example.json", workspace_root=tmp_path
        )

    assert not (tmp_path / "bushing_example" / "v01").exists()
    assert not any(path.name.startswith(".ppw3-build-") for path in tmp_path.iterdir())
