From the project root (photo_duplicate_cleaner/):

Install deps:

pip install -r requirements.txt


python -m streamlit run streamlit_app.py

# 🧹 Photo & Screenshot Duplicate Cleaner (Perceptual Hashing, Python)

A small Python project that scans a folder of images (photos, screenshots, etc.), detects **duplicate / near-duplicate images** using **perceptual hashing**, and helps you:

- Inspect duplicate groups in a **Streamlit UI**
- **Move** duplicate files into a separate folder (keeping one reference image)
- Or **delete** duplicates in place (again, keeping one image per group)

No camera needed – the tool only works on existing image files.

---

## ✨ Features

- 🔍 **Duplicate detection** via perceptual hashes:
  - Supports `phash`, `ahash`, `dhash`, `whash` via `imagehash` library
  - Configurable hash size and Hamming distance threshold
- 🖼️ **Visual inspection**:
  - Streamlit UI to view each duplicate group with thumbnails
- 📁 **File management**:
  - Move duplicates to a chosen folder (keeps 1 image per group)
  - Optionally delete duplicates directly from disk
- 🧪 Two ways to use:
  - CLI (command line)
  - Streamlit web UI

---

## 🧠 Core Idea (Perceptual Hashing)

Instead of comparing raw files (which would only detect exact binary duplicates), we use **perceptual hashing**, which tries to capture *how an image looks*.

High level:

1. Load image → resize → grayscale.
2. Compute a small hash (e.g. 8×8 = 64 bits).
3. Similar-looking images have similar hashes.
4. Compare hashes using **Hamming distance**:
   - Distance = number of differing bits.
   - Distance ≤ threshold → images are considered near-duplicates.

This makes the method robust to:
- Small resizes
- Slight crops
- Minor brightness/contrast changes
- Re-encoding artifacts

---

## 🏗️ Project Structure

```text
photo_duplicate_cleaner/
├─ duplicate_cleaner/
│  ├─ __init__.py           # exports CLI main() if needed
│  ├─ cli.py                # CLI entrypoint (argparse)
│  ├─ image_loader.py       # file discovery (iterating image files)
│  ├─ hashing.py            # perceptual hashing (imagehash + Pillow)
│  ├─ similarity.py         # HashedImage model, grouping via Union-Find
│  ├─ report.py             # console + JSON reports
│  ├─ actions.py            # move/delete duplicate files
├─ main.py                  # simple entrypoint for CLI
├─ streamlit_app.py         # Streamlit UI for visual inspection & actions
├─ requirements.txt         # Python dependencies
└─ README.md                # (this documentation)
=======
# Photo-Screenshot-Duplicate-Cleaner-Perceptual-Hashing-Python-
>>>>>>> 196fe2a3ac09bec2cb6752de433fb68d3935754e
