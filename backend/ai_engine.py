import cv2
import numpy as np
import os

def analyze_construction_image(image_path, claimed_progress, stage_id):
    """
    Analyzes an uploaded image to verify construction progress.
    Returns 'Verified' if the image structural density matches expectations, 
    otherwise returns 'Flagged'.
    """
    if not os.path.exists(image_path):
        return "Flagged"

    try:
        # 1. Load the image using OpenCV
        image = cv2.imread(image_path)
        if image is None:
            return "Flagged"

        # 2. Resize for faster processing (standardizing the input)
        image = cv2.resize(image, (640, 480))

        # 3. Convert to Grayscale (Color doesn't matter for structural shapes)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 4. Apply Gaussian Blur to reduce background noise (leaves only distinct structures)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # 5. Canny Edge Detection (Finds lines, scaffolding, brick edges, pillars)
        edges = cv2.Canny(blurred, 50, 150)

        # 6. Calculate Structural Density
        # Count the number of white pixels (edges) vs total pixels
        total_pixels = edges.shape[0] * edges.shape[1]
        edge_pixels = np.count_nonzero(edges)
        structural_density = (edge_pixels / total_pixels) * 100

        print(f"[AI ENGINE] Analyzed {image_path} | Structural Density: {structural_density:.2f}%")

        # 7. Verification Logic
        # A very basic B.Tech heuristic: If the contractor claims high progress, 
        # there should be a decent amount of structural edges in the photo.
        
        if claimed_progress > 20 and structural_density < 2.0:
            # They claim lots of work, but the photo looks like an empty flat field
            return "Flagged"
        elif structural_density >= 2.0:
            # We detect solid structures
            return "Verified"
        else:
            return "Pending"

    except Exception as e:
        print(f"[AI ENGINE ERROR] {str(e)}")
        return "Pending"