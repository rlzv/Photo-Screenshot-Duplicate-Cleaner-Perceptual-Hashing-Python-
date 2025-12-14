from pathlib import Path
from typing import List, Dict, Any
import json

from .similarity import HashedImage


def print_groups(groups: List[List[HashedImage]]) -> None:
    """
    Print duplicate / near-duplicate groups to the console.
    """
    if not groups:
        print("No duplicate or near-duplicate images found.")
        return

    print(f"Found {len(groups)} duplicate/near-duplicate group(s):\n")

    for idx, group in enumerate(groups, start=1):
        print(f"Group {idx} ({len(group)} images):")
        # Simple heuristic: first image as "reference"
        reference = group[0]
        print(f"  Reference: {reference.path}")
        for img in group[1:]:
            print(f"    Similar: {img.path}")
        print("")


def groups_to_json_serializable(groups: List[List[HashedImage]]) -> List[Dict[str, Any]]:
    """
    Turn groups into a JSON-serializable list of dicts.
    """
    data: List[Dict[str, Any]] = []
    for idx, group in enumerate(groups, start=1):
        data.append(
            {
                "group_id": idx,
                "images": [str(img.path) for img in group],
                "reference": str(group[0].path),
            }
        )
    return data


def save_groups_to_json(groups: List[List[HashedImage]], output_path: Path) -> None:
    """
    Save groups to a JSON file.
    """
    payload = groups_to_json_serializable(groups)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"Saved groups to {output_path}")
