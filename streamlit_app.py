import os
from pathlib import Path
from typing import List

import streamlit as st

from duplicate_cleaner.image_loader import list_image_files
from duplicate_cleaner.hashing import compute_hash
from duplicate_cleaner.similarity import HashedImage, group_similar_images
from duplicate_cleaner.actions import move_duplicates


st.set_page_config(
    page_title="Photo & Screenshot Duplicate Cleaner",
    layout="wide",
)


def scan_for_duplicates(
    folder: Path,
    recursive: bool,
    hash_type: str,
    hash_size: int,
    threshold: int,
) -> List[List[HashedImage]]:
    """Scan the folder, compute hashes, and group near-duplicates."""
    images = list_image_files(folder, recursive=recursive)
    if not images:
        st.warning("No supported image files found in this folder.")
        return []

    st.info(f"Found {len(images)} image(s). Computing perceptual hashes...")

    hashed_images: List[HashedImage] = []
    progress_bar = st.progress(0.0)
    total = len(images)

    for idx, img_path in enumerate(images, start=1):
        try:
            h = compute_hash(
                img_path,
                hash_type=hash_type,  # type: ignore[arg-type]
                hash_size=hash_size,
            )
            hashed_images.append(HashedImage(path=img_path, hash=h))
        except Exception as e:
            st.warning(f"Failed to process {img_path}: {e}")

        progress_bar.progress(idx / total)

    if not hashed_images:
        st.error("No images could be hashed.")
        return []

    st.info("Finding near-duplicate images...")
    groups = group_similar_images(hashed_images, threshold=threshold)
    return groups


def delete_duplicates_in_place(
    groups: List[List[HashedImage]],
    keep_strategy: str = "first",
) -> int:
    """
    Delete duplicates directly from disk, keeping one image per group.

    :param groups: List of HashedImage groups.
    :param keep_strategy: "first" or "largest".
    :return: Number of files deleted.
    """
    deleted_count = 0

    for group in groups:
        if len(group) < 2:
            continue

        if keep_strategy == "first":
            keep = group[0]
        elif keep_strategy == "largest":
            keep = max(group, key=lambda hi: hi.path.stat().st_size)
        else:
            raise ValueError(f"Unsupported keep_strategy: {keep_strategy}")

        for img in group:
            if img.path == keep.path:
                continue

            if img.path.exists():
                try:
                    os.remove(img.path)
                    deleted_count += 1
                except Exception as e:
                    st.warning(f"Failed to delete {img.path}: {e}")

    return deleted_count


def main():
    st.title("🧹 Photo & Screenshot Duplicate Cleaner")
    st.write(
        "Visually inspect duplicate / near-duplicate images, then move or delete them."
    )

    # --- Sidebar controls ---
    st.sidebar.header("Settings")

    folder_str = st.sidebar.text_input(
        "Folder path",
        value=".",
        help="Folder containing your photos/screenshots.",
    )
    recursive = st.sidebar.checkbox(
        "Scan recursively", value=True, help="Include subfolders"
    )
    hash_type = st.sidebar.selectbox(
        "Hash type",
        options=["phash", "ahash", "dhash", "whash"],
        index=0,
        help="Type of perceptual hash to use",
    )
    hash_size = st.sidebar.slider(
        "Hash size",
        min_value=4,
        max_value=16,
        value=8,
        help="Higher = more precise but slower",
    )
    threshold = st.sidebar.slider(
        "Similarity threshold (Hamming distance)",
        min_value=1,
        max_value=10,
        value=5,
        help="Lower = stricter duplicates, higher = more tolerant",
    )
    keep_strategy = st.sidebar.selectbox(
        "Keep strategy for each group",
        options=["first", "largest"],
        index=0,
        help=(
            "When moving or deleting, which image to keep in each group:\n"
            "- 'first': first discovered image\n"
            "- 'largest': largest file size"
        ),
    )

    st.sidebar.markdown("---")
    dest_folder_str = st.sidebar.text_input(
        "Destination folder for moved duplicates",
        value="./duplicates_moved",
        help="Where to move non-reference duplicates",
    )

    if "groups" not in st.session_state:
        st.session_state["groups"] = []

    # --- Scan button ---
    if st.sidebar.button("🔍 Scan for duplicates"):
        folder = Path(folder_str).expanduser().resolve()
        if not folder.exists():
            st.error(f"Folder not found: {folder}")
        else:
            groups = scan_for_duplicates(
                folder=folder,
                recursive=recursive,
                hash_type=hash_type,
                hash_size=hash_size,
                threshold=threshold,
            )
            st.session_state["groups"] = groups

    groups: List[List[HashedImage]] = st.session_state.get("groups", [])

    # --- Display groups ---
    if groups:
        st.success(f"Found {len(groups)} duplicate / near-duplicate group(s).")

        for group_idx, group in enumerate(groups, start=1):
            with st.expander(f"Group {group_idx}  ({len(group)} images)", expanded=False):
                # Display images in rows of up to 4 columns
                cols_per_row = 4
                total = len(group)
                for start in range(0, total, cols_per_row):
                    cols = st.columns(min(cols_per_row, total - start))
                    for col, img in zip(cols, group[start : start + cols_per_row]):
                        with col:
                            st.image(
                                str(img.path),
                                caption=str(img.path.name),
                                use_column_width=True,
                            )
                            st.caption(str(img.path))

        st.markdown("---")
        st.subheader("Actions on duplicates")

        col_move, col_delete = st.columns(2)

        with col_move:
            if st.button("📁 Move duplicates (keep 1 per group)"):
                dest_root = Path(dest_folder_str).expanduser().resolve()
                if not dest_root.exists():
                    dest_root.mkdir(parents=True, exist_ok=True)
                move_duplicates(
                    groups,
                    dest_root=dest_root,
                    keep_strategy=keep_strategy,
                )
                st.success(
                    f"Move operation completed. Check folder: {dest_root}"
                )

        with col_delete:
            if st.button("🗑️ Delete duplicates in place (keep 1 per group)"):
                deleted = delete_duplicates_in_place(
                    groups,
                    keep_strategy=keep_strategy,
                )
                st.warning(
                    f"Deleted {deleted} file(s). "
                    "This operation cannot be undone. "
                    "You may want to rescan to update the view."
                )

    else:
        st.info(
            "No groups loaded yet. Use the sidebar to choose a folder and click "
            "'Scan for duplicates'."
        )


if __name__ == "__main__":
    main()
