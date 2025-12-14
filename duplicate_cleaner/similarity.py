from dataclasses import dataclass
from pathlib import Path
from typing import List

import imagehash


@dataclass
class HashedImage:
    path: Path
    hash: imagehash.ImageHash


class UnionFind:
    """
    Simple Union-Find (Disjoint Set Union) to group similar images.
    """

    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, a: int, b: int) -> None:
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a == root_b:
            return
        # Union by rank
        if self.rank[root_a] < self.rank[root_b]:
            self.parent[root_a] = root_b
        elif self.rank[root_a] > self.rank[root_b]:
            self.parent[root_b] = root_a
        else:
            self.parent[root_b] = root_a
            self.rank[root_a] += 1

    def groups(self) -> List[List[int]]:
        """
        Return groups of indices (each group is a list of indices).
        """
        root_to_members = {}
        for i in range(len(self.parent)):
            root = self.find(i)
            root_to_members.setdefault(root, []).append(i)
        return list(root_to_members.values())


def group_similar_images(
    hashed_images: List[HashedImage],
    threshold: int = 5,
) -> List[List[HashedImage]]:
    """
    Group images whose perceptual hash distance is <= threshold.

    :param hashed_images: List of HashedImage.
    :param threshold: Max Hamming distance to consider as near-duplicate.
    :return: List of groups; each group is a list of HashedImage.
    """
    n = len(hashed_images)
    if n == 0:
        return []

    uf = UnionFind(n)

    # Naive O(n^2) comparison - fine for an MVP / normal-sized folders.
    for i in range(n):
        for j in range(i + 1, n):
            dist = hashed_images[i].hash - hashed_images[j].hash
            if dist <= threshold:
                uf.union(i, j)

    index_groups = uf.groups()
    result: List[List[HashedImage]] = []

    for group in index_groups:
        if len(group) > 1:  # Only keep groups with actual duplicates
            result.append([hashed_images[i] for i in group])

    return result
