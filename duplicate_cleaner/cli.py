import argparse
from pathlib import Path
from typing import List

from .image_loader import list_image_files
from .hashing import compute_hash, HashType
from .similarity import HashedImage, group_similar_images
from .report import print_groups, save_groups_to_json
from .actions import move_duplicates


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Photo & Screenshot Duplicate Cleaner using perceptual hashing"
    )
    parser.add_argument(
        "folder",
        type=str,
        help="Path to the folder containing images.",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Scan folders recursively.",
    )
    parser.add_argument(
        "--hash-type",
        choices=["ahash", "phash", "dhash", "whash"],
        default="phash",
        help="Type of perceptual hash to use (default: phash).",
    )
    parser.add_argument(
        "--hash-size",
        type=int,
        default=8,
        help="Hash size for perceptual hashing (default: 8). Higher = more precise but slower.",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        type=int,
        default=5,
        help="Max Hamming distance between hashes to consider images as near-duplicates (default: 5).",
    )
    parser.add_argument(
        "-o",
        "--output-json",
        type=str,
        default=None,
        help="Optional path to save duplicate groups as JSON.",
    )
    parser.add_argument(
        "--move-duplicates-to",
        type=str,
        default=None,
        help=(
            "Optional folder where non-reference duplicates will be moved. "
            "One image per group is kept in place."
        ),
    )
    parser.add_argument(
        "--keep-strategy",
        choices=["first", "largest"],
        default="first",
        help=(
            "Strategy for which image to keep in each group: "
            "'first' (default) or 'largest' (keep largest file size)."
        ),
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    root = Path(args.folder).expanduser().resolve()
    if not root.exists():
        print(f"Error: folder not found: {root}")
        return

    print(f"Scanning images in: {root}")
    images: List[Path] = list_image_files(root, recursive=args.recursive)

    if not images:
        print("No supported image files found.")
        return

    print(f"Found {len(images)} image(s). Computing perceptual hashes...")

    hashed_images: List[HashedImage] = []
    for img_path in images:
        try:
            h = compute_hash(
                img_path,
                hash_type=args.hash_type,  # type: ignore[arg-type]
                hash_size=args.hash_size,
            )
            hashed_images.append(HashedImage(path=img_path, hash=h))
        except Exception as e:
            # If any image can't be processed, just report and skip.
            print(f"Warning: failed to process {img_path}: {e}")

    if not hashed_images:
        print("No images could be hashed. Exiting.")
        return

    print("Finding near-duplicate images...")
    groups = group_similar_images(hashed_images, threshold=args.threshold)

    print_groups(groups)

    # Save JSON if requested
    if args.output_json and groups:
        output_path = Path(args.output_json).expanduser().resolve()
        save_groups_to_json(groups, output_path)

    # Move duplicates if requested
    if args.move_duplicates_to and groups:
        dest_root = Path(args.move_duplicates_to)
        print("\nMoving duplicates (non-reference images) ...")
        move_duplicates(
            groups,
            dest_root=dest_root,
            keep_strategy=args.keep_strategy,
        )
