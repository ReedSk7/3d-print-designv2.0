# Peg hook 6.8 mm PETG fit edit

This project preserves the peg-hook mesh edit that was migrated from the legacy
`3d-print-design-studio` repository during the workspace consolidation.

## Source and outputs

- Editable transformation: `source/peg_hook_6p8mm_fit_petg_edit.py`
- Preserved exports: `exports/peg_hook_6p8mm_fit_petg.stl` and `.3mf`
- Original validation record: `notes/peg_hook_6p8mm_fit_petg_report.json`
- Comparison images: `previews/`

The original `MP25.stl` reference mesh is not committed. Place an authorized
copy at `references/MP25.stl`, or set `PEG_HOOK_SOURCE_STL` to its local path,
before rerunning the edit:

```powershell
python source\peg_hook_6p8mm_fit_petg_edit.py
```

The preserved report records mesh checks and measured geometry from the prior
run. It does not establish physical fit; the part remains physically unverified.
