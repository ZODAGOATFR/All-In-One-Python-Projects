import cv2
import numpy as np
import time
from pathlib import Path
from matplotlib import pyplot as plt

# ---- Settings ----
SHOW_FIGS = True   # Set False if you don’t want matplotlib popups
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# 🔑 Your folder
IMAGE_DIR = Path("/Users/lonzohamiltonjr/Documents/Images")

# Allowed image extensions
EXTS = [".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"]

def wait(t: float):
    time.sleep(t)

def get_images(folder: Path):
    """Return all image files in the given folder (non-recursive)."""
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")
    images = [p for p in folder.iterdir() if p.suffix.lower() in EXTS]
    if not images:
        raise FileNotFoundError(f"No images found in {folder}")
    return images

def scenario(image_path: Path, show: bool = SHOW_FIGS):
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Failed to read image: {image_path}")

    # --- Processing ---
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (15, 15), 0)
    _, thresh = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY)

    found = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(found) == 3:
        _img, contours, hierarchy = found
    else:
        contours, hierarchy = found

    vis = image.copy()
    cv2.drawContours(vis, contours, -1, (0, 255, 0), 2)

    centroids = []
    for cnt in contours:
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            centroids.append((cx, cy))
            cv2.circle(vis, (cx, cy), 3, (0, 0, 255), -1)

    # --- Save outputs ---
    stem = image_path.stem
    out_gray   = OUTPUT_DIR / f"{stem}_gray.png"
    out_blur   = OUTPUT_DIR / f"{stem}_blur.png"
    out_thresh = OUTPUT_DIR / f"{stem}_thresh.png"
    out_vis    = OUTPUT_DIR / f"{stem}_contours.png"

    cv2.imwrite(str(out_gray), gray)
    cv2.imwrite(str(out_blur), blur)
    cv2.imwrite(str(out_thresh), thresh)
    cv2.imwrite(str(out_vis), vis)

    # --- Show results ---
    if show:
        try:
            vis_rgb = cv2.cvtColor(vis, cv2.COLOR_BGR2RGB)
            plt.figure(figsize=(7, 5))
            plt.title(f"{stem}: Contours + Centroids")
            plt.imshow(vis_rgb)
            plt.axis("off")
            plt.show()

            plt.figure(figsize=(7, 5))
            plt.title(f"{stem}: Threshold")
            plt.imshow(thresh, cmap="gray")
            plt.axis("off")
            plt.show()
        except Exception as e:
            print(f"(Display skipped) {e}")

    return {
        "image": str(image_path),
        "num_contours": len(contours),
        "centroids": centroids[:50],
        "saved": {
            "gray": str(out_gray.resolve()),
            "blur": str(out_blur.resolve()),
            "thresh": str(out_thresh.resolve()),
            "contours": str(out_vis.resolve())
        }
    }

if __name__ == "__main__":
    print("Starting macOS-safe image processing…")
    try:
        images = get_images(IMAGE_DIR)
        for p in images:
            print(f"\nProcessing {p} …")
            stats = scenario(p, show=SHOW_FIGS)
            print(f"Contours: {stats['num_contours']}")
            print("Saved files:")
            for k, v in stats["saved"].items():
                print(" ", k, "->", v)
            wait(0.15)
    except Exception as e:
        print(f"Setup error: {e}")
