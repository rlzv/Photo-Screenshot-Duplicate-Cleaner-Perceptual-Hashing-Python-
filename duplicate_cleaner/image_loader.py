from pathlib import Path
from typing import Iterable, List

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}


def iter_image_files(root: Path, recursive: bool = True) -> Iterable[Path]:
    """
    Yield paths to image files under `root`.

    :param root: Folder to scan.
    :param recursive: If True, walk all subfolders.
    """
    if not root.exists():
        raise FileNotFoundError(f"Path not found: {root}")

    if recursive:
        paths = root.rglob("*")
    else:
        paths = root.glob("*")

    for p in paths:
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield p


def list_image_files(root: Path, recursive: bool = True) -> List[Path]:
    """
    Convenience wrapper to return a list.
    """
    return list(iter_image_files(root, recursive=recursive))
