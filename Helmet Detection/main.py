import cv2
import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt

# ---- Settings ----
SHOW_FIGS = True   # Set False if you don’t want matplotlib popups
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# 🔑 Your single image path (given)
IMAGE_PATH = Path("/Users/lonzohamiltonjr/Documents/CPSC_2735/Shoei-NXR2-Motorcycle-Helmet-Lifestyle-6.jpg")

def save_fig(title, img_bgr):
    """Helper to save + (optionally) show BGR images with a title-based filename."""
    out_path = OUTPUT_DIR / (title.replace(" ", "_").lower() + ".png")
    cv2.imwrite(str(out_path), img_bgr)
    if SHOW_FIGS:
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        plt.figure(figsize=(7,5))
        plt.title(title)
        plt.imshow(img_rgb if img_rgb.ndim == 3 else img_bgr, cmap=None if img_rgb.ndim == 3 else "gray")
        plt.axis("off")
        plt.show()
    return out_path

def crop_safe(img, x1, y1, x2, y2, pad=10):
    h, w = img.shape[:2]
    x1 = max(0, x1 - pad); y1 = max(0, y1 - pad)
    x2 = min(w, x2 + pad); y2 = min(h, y2 + pad)
    return img[y1:y2, x1:x2].copy()

def detect_helmet_region(image):
    """
    Heuristic helmet region finder:
      1) Try Hough circles on blurred gray (look for large circle near top half).
      2) If none, threshold + contours, pick largest contour in top half.
    Returns (x1,y1,x2,y2) bbox if found, else None.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 2)

    # --- Try HoughCircles (tune params as needed for your photo) ---
    circles = cv2.HoughCircles(
        blur,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=50,
        param1=120,
        param2=30,
        minRadius=40,
        maxRadius=0  # 0 -> no explicit max
    )

    h, w = gray.shape[:2]
    top_half_limit = int(h * 0.6)  # consider helmets likely in top ~60%

    if circles is not None:
        circles = np.round(circles[0]).astype(int)
        # Filter circles roughly in the top half
        circles_top = [c for c in circles if c[1] < top_half_limit]
        chosen = None
        if circles_top:
            # choose largest radius in top region
            chosen = max(circles_top, key=lambda c: c[2])
        else:
            # fallback: choose largest overall
            chosen = max(circles, key=lambda c: c[2])

        x, y, r = chosen
        x1, y1 = x - r, y - r
        x2, y2 = x + r, y + r
        # Clip to image bounds
        x1 = max(0, x1); y1 = max(0, y1)
        x2 = min(w, x2); y2 = min(h, y2)
        return (x1, y1, x2, y2)

    # --- Fallback: threshold + largest contour in top half ---
    # Use adaptive or fixed threshold depending on lighting
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    # Emphasize edges/shapes
    th = cv2.medianBlur(th, 5)

    found = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = found[0] if len(found) == 2 else found[1]

    # Filter contours whose centroid lies in the top half
    cand = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 500:  # ignore tiny bits
            continue
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue
        cy = int(M["m01"] / M["m00"])
        if cy < top_half_limit:
            x, y, bw, bh = cv2.boundingRect(cnt)
            cand.append((area, (x, y, x+bw, y+bh)))

    if cand:
        cand.sort(reverse=True, key=lambda x: x[0])  # largest area first
        return cand[0][1]

    return None

def main():
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(f"Image not found: {IMAGE_PATH}")

    image = cv2.imread(str(IMAGE_PATH))
    if image is None:
        raise ValueError(f"Failed to read image: {IMAGE_PATH}")

    save_fig("original", image)

    bbox = detect_helmet_region(image)
    vis = image.copy()
    cropped_out = None

    if bbox is not None:
        x1, y1, x2, y2 = bbox
        # Draw bbox on visualization
        cv2.rectangle(vis, (x1, y1), (x2, y2), (0,255,0), 3)
        cv2.putText(vis, "HELMET (heuristic)", (x1, max(0, y1-10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2, cv2.LINE_AA)
        save_fig("helmet_bbox", vis)

        # Save the cropped helmet region
        cropped = crop_safe(image, x1, y1, x2, y2, pad=12)
        # Normalize to a nice square thumbnail similar to your headlight output
        target = 512
        ch, cw = cropped.shape[:2]
        scale = target / max(ch, cw)
        resized = cv2.resize(cropped, (int(cw*scale), int(ch*scale)), interpolation=cv2.INTER_LANCZOS4)
        # letterbox to square
        canvas = np.zeros((target, target, 3), dtype=np.uint8)
        oy = (target - resized.shape[0]) // 2
        ox = (target - resized.shape[1]) // 2
        canvas[oy:oy+resized.shape[0], ox:ox+resized.shape[1]] = resized
        out_path = OUTPUT_DIR / "motorcycle_helmet.jpg"
        cv2.imwrite(str(out_path), canvas)
        print(f"Saved cropped helmet: {out_path.resolve()}")
        cropped_out = out_path
    else:
        print("No helmet-like region found with current heuristic.")
        # Still save a labeled version of the original for reference
        cv2.putText(vis, "NO HELMET REGION FOUND", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 2, cv2.LINE_AA)
        save_fig("helmet_not_found", vis)

    # Also save a simple grayscale/threshold debug stack like your headlight flow
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9,9), 2)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    save_fig("gray", cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR))
    save_fig("blur", cv2.cvtColor(blur, cv2.COLOR_GRAY2BGR))
    save_fig("thresh", cv2.cvtColor(th, cv2.COLOR_GRAY2BGR))

if __name__ == "__main__":
    print("Starting single-image helmet extraction…")
    main()




