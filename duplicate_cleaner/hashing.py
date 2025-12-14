from pathlib import Path
from typing import Literal

from PIL import Image
import imagehash

HashType = Literal["ahash", "phash", "dhash", "whash"]


def compute_hash(
    image_path: Path,
    hash_type: HashType = "phash",
    hash_size: int = 8,
) -> imagehash.ImageHash:
    """
    Compute a perceptual hash for an image.

    :param image_path: Path to the image file.
    :param hash_type: Type of hash: 'ahash', 'phash', 'dhash', or 'whash'.
    :param hash_size: Hash size (larger = more detail, but slightly slower).
    """
    with Image.open(image_path) as img:
        img = img.convert("RGB")

        if hash_type == "ahash":
            return imagehash.average_hash(img, hash_size=hash_size)
        elif hash_type == "phash":
            return imagehash.phash(img, hash_size=hash_size)
        elif hash_type == "dhash":
            return imagehash.dhash(img, hash_size=hash_size)
        elif hash_type == "whash":
            return imagehash.whash(img, hash_size=hash_size)
        else:
            raise ValueError(f"Unsupported hash type: {hash_type}")
