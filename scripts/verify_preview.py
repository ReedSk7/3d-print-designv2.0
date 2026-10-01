"""Verify rendered image hashes and their exact version bindings; no human review claim."""
import argparse
from pathlib import Path
from _repo_bootstrap import add_repo_root
add_repo_root()
from core.workflow.preview import verify_preview_bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview-manifest', required=True, type=Path)
    args = parser.parse_args()
    try:
        verify_preview_bundle(args.preview_manifest)
    except Exception as exc:
        print(f'PREVIEW CHECK FAILED: {exc}')
        return 1
    print('Preview hashes/version/PNG structure passed. Human visual review and physical fit are not established.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
