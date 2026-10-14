"""Contain local workshop paths without granting links a new authority."""
from pathlib import Path


def safe_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError('Use a relative project path.')
    if root.absolute() != root.resolve():
        raise ValueError('Allowed root is redirected by a link or junction.')
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        raise ValueError('Path leaves the allowed project directory.') from None
    return candidate


def unredirected_path(root: Path, path: Path) -> Path:
    """Catalog/storage identities are their original locations, never aliases."""
    resolved = safe_path(root, path.relative_to(root).as_posix())
    if resolved != path.absolute():
        raise ValueError(f'Path is redirected by a link or junction: {path.relative_to(root)}')
    return resolved
