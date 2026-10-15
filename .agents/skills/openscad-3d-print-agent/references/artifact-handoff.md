# Artifact verification and Bambu handoff

Run `verify_mesh.py --manifest` and `inspect_project_status.py --project-version-dir`.
Hashes/source identity, computational checks and immutable human fit evidence have
different meanings. Never fabricate coupon/physical results or modify records to
make them pass. A changed source, profile or printed setup needs a new version/test.

Use `prepare_bambu_handoff.py --manifest` for source/STL copies and the concrete
manual-import checklist. This is NOT a 3MF or verified Bambu project. The doctor
probes Bambu `--help` only when installed. Automated 3MF packaging remains blocked
until that installed CLI and real compatible full P2S profiles are available and
an exported project has been reopened/imported and checked.

Use copies of real printer/process/filament presets; preserve the originals and
record provenance/hashes. Never substitute P1S, invent installed nozzle/material/
plate/AMS identities, assign guessed colors or purge estimates. Keep millimeter
scale and relative component alignment. A generic geometry 3MF is not a Bambu
Studio project. Future multicolor components need explicit IDs and confirmed
filament mappings. Do not connect/send jobs/update firmware or print without a
separate user task authorizing it. Run `check_output_policy.py` before committing.
