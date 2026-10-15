"""Prepare a manual Bambu Studio import bundle without slicing or printing."""
from __future__ import annotations

import tempfile
from pathlib import Path

from core.workflow.review import (
    file_record, publish_bundle, revision_directory, snapshot_generation, write_json,
)


def prepare_bambu_handoff(manifest: Path, *, revision="r01", printer_model="Bambu Lab P2S") -> Path:
    # The user's known machine is P2S. No substitutions or inferred hardware setup.
    if printer_model != "Bambu Lab P2S":
        raise ValueError("This handoff targets Bambu Lab P2S; printer substitution is not allowed.")
    generation, scad, stl, spec, mesh = snapshot_generation(manifest)
    if generation.spec.printer_profile not in {"generic_fdm", "bambu_lab_p2s_owner_local"}:
        raise ValueError("Unrecognized or mismatched printer-profile identity for P2S handoff; review the source spec, never substitute profiles.")
    target = revision_directory(generation, "bambu-handoff", revision)
    with tempfile.TemporaryDirectory(prefix=".ppw3-handoff-", dir=generation.workspace_root) as directory:
        staging = Path(directory)
        for name, data in (("geometry.stl", stl), ("source.scad", scad), ("spec.snapshot.json", spec)):
            (staging / name).write_bytes(data)
        declared = {"printer_profile": generation.spec.printer_profile, "material": generation.spec.material,
                    "nozzle_diameter_mm": str(generation.spec.nozzle_diameter_mm),
                    "calibration_profile": generation.calibration_profile_id}
        instructions = f"""# Manual Bambu Studio import — {generation.spec.project.id} / {generation.spec.project.version}

This is an STL/source handoff, NOT a 3MF or a verified Bambu Studio project.
No slicing, printer connection, machine changes, firmware update, or print occurs.

1. In Bambu Studio, create a new local project and choose the real **Bambu Lab P2S**.
   Confirm the physically installed nozzle, filament, build plate, and any AMS model.
   Never substitute P1S. The spec's declared identities below are not installation evidence.
2. Duplicate your compatible printer/process/filament presets. Work only on those copies.
   Record original preset names, Bambu Studio version, exported copy hashes, and changes
   beside this handoff. Do not alter master presets or guess filament/AMS assignments.
3. Import geometry.stl at **100% scale in millimeters**. Its disconnected bodies keep
   their relative alignment in this single mesh. Do not split, orient, arrange, center
   components individually, or accept an automatic unit conversion.
4. Compare overall dimensions to {" × ".join(str(v) for v in mesh.extents_mm)} mm.
   Check component placement and all critical interfaces against source.scad and the spec.
   If Studio moves the object as a whole to the bed, inspect and record that transform.
5. Review actual top/front/side/isometric previews. Record reviewer, date, images/hashes,
   observations and remaining concerns in a NEW local review note. PNG existence is not review.
6. Save a new .3mf project beside this bundle using a new filename, then close and reopen it.
   Recheck millimeter scale, object count/placement, P2S/nozzle/plate/process/filament settings.
   Record this as manual reopen evidence; until then packaging remains unverified.
7. Physical printing and fit testing are a separate owner decision. This task authorizes neither.

Declared spec identities (not confirmed printer settings): {declared}
Unresolved: installed nozzle, actual filament/preset, build plate, process preset,
AMS model/mapping, compatible exported profile copies, Bambu Studio import/reopen validation.
Future component labels and multicolor mappings require explicit component IDs and real
filament assignments. No mappings or purge estimates are supplied here.
"""
        (staging / "IMPORT_IN_BAMBU.md").write_text(instructions, encoding="utf-8")
        write_json(staging / "handoff-manifest.json", {
            "schema_version": "1.0", "kind": "manual_stl_import", "target_printer": printer_model,
            "source_manifest": generation.manifest_binding.to_dict(),
            "artifacts": [file_record(path) for path in sorted(staging.iterdir())],
            "source_declared_identity": declared, "expected_extents_mm": [str(v) for v in mesh.extents_mm],
            "component_transform": "identity; one STL preserves relative placement", "units": "mm",
            "profiles": [], "settings_provenance": "No real slicer profiles supplied; owner must select compatible copies.",
            "automated_3mf_packaging": "not_implemented_without_tested_tool_and_profiles",
            "bambu_project_verified": False, "reopen_validation": "pending", "physical_fit_confirmed": False,
        })
        publish_bundle(staging, target, manifest_name="handoff-manifest.json")
    return target / "handoff-manifest.json"
