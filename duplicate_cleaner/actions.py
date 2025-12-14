from pathlib import Path
from typing import List
import shutil

from .similarity import HashedImage


def move_duplicates(
    groups: List[List[HashedImage]],
    dest_root: Path,
    keep_strategy: str = "first",
) -> None:
    """
    Move duplicate / near-duplicate images into `dest_root`,
    keeping one image per group in the original location.

    :param groups: List of groups of HashedImage.
    :param dest_root: Folder where duplicates will be moved.
    :param keep_strategy: Strategy to choose which image to keep.
                          Currently supported: "first" (default), "largest".
    """
    if not groups:
        print("No groups to process for moving duplicates.")
        return

    dest_root = dest_root.expanduser().resolve()
    dest_root.mkdir(parents=True, exist_ok=True)

    moved_count = 0

    for group in groups:
        if len(group) < 2:
            continue  # nothing to move

        # Choose which image to keep
        if keep_strategy == "first":
            keep = group[0]
        elif keep_strategy == "largest":
            # Keep the largest file (by bytes)
            keep = max(group, key=lambda hi: hi.path.stat().st_size)
        else:
            raise ValueError(f"Unsupported keep_strategy: {keep_strategy}")

        print(f"\n[GROUP] Keeping: {keep.path}")
        print(f"        Moving others to: {dest_root}")

        for img in group:
            if img.path == keep.path:
                continue  # skip the kept one

            src = img.path
            if not src.exists():
                print(f"  Skipping (file missing): {src}")
                continue

            # Build destination path (avoid overwriting with suffixes)
            dest = dest_root / src.name
            if dest.exists():
                stem = dest.stem
                suffix = dest.suffix
                index = 1
                while dest.exists():
                    dest = dest_root / f"{stem}_dup{index}{suffix}"
                    index += 1

            try:
                shutil.move(str(src), str(dest))
                moved_count += 1
                print(f"  Moved: {src} -> {dest}")
            except Exception as e:
                print(f"  Failed to move {src}: {e}")

    print(f"\nDone. Moved {moved_count} file(s) to {dest_root}")
